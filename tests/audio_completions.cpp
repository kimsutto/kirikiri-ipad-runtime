// SPDX-License-Identifier: MIT
#include "../overlay/src/core/sound/sdl2/AudioCompletions.h"
#include <cassert>
#include <thread>
#include <mutex>
#include <future>
#include <chrono>
int main() {
    AudioCompletions events;
    const auto old = events.Generation();
    events.Complete(old);
    events.Reset();
    events.Complete(old);
    assert(events.Take() == 0);
    const auto current = events.Generation();
    std::thread producer([&] { for(int i=0;i<100000;i++) events.Complete(current); });
    uint64_t consumed = 0;
    for(int i=0;i<1000;i++) consumed += events.Take();
    producer.join(); consumed += events.Take();
    assert(consumed == 100000);
    assert(events.Take() == 0);
    // Reproduce the lock ordering: game holds its lock while waiting on the audio thread.
    std::mutex gameLock;
    std::lock_guard<std::mutex> held(gameLock);
    auto callback = std::async(std::launch::async, [&] { events.Complete(current); });
    assert(callback.wait_for(std::chrono::seconds(1)) == std::future_status::ready);
    callback.get(); assert(events.Take() == 1);
    std::thread late([&] { for(int i=0;i<100000;i++) events.Complete(current); });
    events.Reset(); late.join();
    assert(events.Take() == 0);
}
