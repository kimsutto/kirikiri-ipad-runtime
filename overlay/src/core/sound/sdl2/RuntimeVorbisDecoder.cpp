// SPDX-License-Identifier: MIT
// Use the existing FAudio stb decoder for Vorbis assets in XP3 archives.
#include "tjsCommHead.h"
#include "StorageIntf.h"
#include "WaveIntf.h"
#include "DebugIntf.h"
#include <memory>
#include <vector>
#include <climits>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <alloca.h>
#define FAudio_alloca(size) alloca(size)
#define FAudio_dealloca(ptr) ((void)0)
#define FAUDIOAPI
#define STB_VORBIS_NO_STDIO
#define STB_VORBIS_NO_PUSHDATA_API
#include "stb_vorbis.h"

class RuntimeVorbisDecoder final : public tTVPWaveDecoder {
    std::vector<unsigned char> compressed;
    stb_vorbis *decoder = nullptr;
    tTVPWaveFormat format{};
public:
    ~RuntimeVorbisDecoder() override { if (decoder) stb_vorbis_close(decoder); }
    bool Open(const ttstr &name) {
        std::unique_ptr<tTJSBinaryStream> stream(TVPCreateStream(name, TJS_BS_READ));
        const auto length = stream->GetSize();
        // shortcut: keep compressed audio in memory; stream if assets exceed 64 MiB.
        if (!length || length > 64 * 1024 * 1024) return false;
        compressed.resize(static_cast<size_t>(length));
        if (stream->Read(compressed.data(), static_cast<tjs_uint>(length)) != length) return false;
        int error = 0;
        decoder = stb_vorbis_open_memory(compressed.data(), static_cast<int>(length), &error, nullptr);
        if (!decoder) return false;
        const auto info = stb_vorbis_get_info(decoder);
        if (info.channels < 1 || info.channels > 8 || !info.sample_rate) return false;
        format.SamplesPerSec = info.sample_rate;
        format.Channels = info.channels;
        format.BitsPerSample = 16;
        format.BytesPerSample = 2;
        format.TotalSamples = stb_vorbis_stream_length_in_samples(decoder);
        format.TotalTime = format.TotalSamples * 1000 / info.sample_rate;
        format.Seekable = true;
        TVPAddLog(ttstr(TJS_W("[audio] Vorbis opened: ")) + name);
        return true;
    }
    void GetFormat(tTVPWaveFormat &out) override { out = format; }
    bool Render(void *buffer, tjs_uint requested, tjs_uint &rendered) override {
        rendered = 0;
        if (!decoder || !buffer || !requested || requested > INT_MAX / format.Channels) return false;
        rendered = stb_vorbis_get_samples_short_interleaved(decoder, format.Channels,
            static_cast<short *>(buffer), static_cast<int>(requested * format.Channels));
        return rendered == requested;
    }
    bool SetPosition(tjs_uint64 sample) override {
        return decoder && sample <= UINT_MAX && stb_vorbis_seek(decoder, static_cast<unsigned int>(sample));
    }
};
class RuntimeVorbisCreator final : public tTVPWaveDecoderCreator {
    tTVPWaveDecoder *Create(const ttstr &name, const ttstr &extension) override {
        if (extension != TJS_W(".ogg")) return nullptr;
        std::unique_ptr<RuntimeVorbisDecoder> decoder(new RuntimeVorbisDecoder());
        return decoder->Open(name) ? decoder.release() : nullptr;
    }
};
void TVPRegisterRuntimeVorbisDecoder() {
    static RuntimeVorbisCreator creator;
    TVPRegisterWaveDecoderCreator(&creator);
}
