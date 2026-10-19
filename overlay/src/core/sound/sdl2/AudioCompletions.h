#pragma once
#include <atomic>
#include <cstdint>

// The audio callback must never acquire KAG's buffer lock while FAudio holds its voice lock.
// A generation prevents flushed buffers from retiring samples in a newly opened sound.
class AudioCompletions {
    std::atomic<uint64_t> state{uint64_t(1) << 32};
public:
    uint32_t Generation() const { return static_cast<uint32_t>(state.load() >> 32); }
    void Complete(uint32_t generation) {
        auto value = state.load();
        while(static_cast<uint32_t>(value >> 32) == generation) {
            if(state.compare_exchange_weak(value, value + 1)) return;
        }
    }
    uint32_t Take() {
        auto value = state.load();
        while(!state.compare_exchange_weak(value, value & 0xffffffff00000000ULL)) {}
        return static_cast<uint32_t>(value);
    }
    void Reset() {
        auto value = state.load();
        while(!state.compare_exchange_weak(value, ((value >> 32) + 1) << 32)) {}
    }
};
