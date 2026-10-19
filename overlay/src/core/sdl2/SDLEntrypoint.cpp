/* SPDX-License-Identifier: MIT */
/* Copyright (c) Kirikiri SDL2 Developers */

#include "SDLApplication.h"
#include "SysInitImpl.h"
#include <cstdio>
#include <string>
#include <vector>
#ifdef __APPLE__
#include <TargetConditionals.h>
#if TARGET_OS_IPHONE
extern const char *RuntimeDocumentsPath();
#endif
#endif
#ifdef USE_SDL_MAIN
#include <SDL_main.h>
#endif

#if defined(USE_SDL_MAIN)
extern "C" int SDL_main(int argc, char **argv)
#elif defined(_WIN32) && defined(_UNICODE)
extern "C" int wmain(int argc, wchar_t **argv)
#else
extern "C" int main(int argc, char **argv)
#endif
{
	setvbuf(stdout, nullptr, _IONBF, 0);
	setvbuf(stderr, nullptr, _IONBF, 0);
	try
	{
		krkrsdl2_pre_init_platform();

#if defined(_WIN32) && defined(_UNICODE)
		krkrsdl2_set_args(argc, argv);
#else
		#if defined(__APPLE__) && TARGET_OS_IPHONE
        std::string rootArg = std::string("-game-root=") + RuntimeDocumentsPath() + "/Game/";
        std::string saveArg = std::string("-datapath=") + RuntimeDocumentsPath() + "/Saves/";
        std::vector<char *> arguments(argv, argv + argc);
        arguments.push_back(const_cast<char *>(rootArg.c_str()));
        arguments.push_back(const_cast<char *>(saveArg.c_str()));
        krkrsdl2_convert_set_args(static_cast<int>(arguments.size()), arguments.data());
#else
        krkrsdl2_convert_set_args(argc, argv);
#endif
#endif

		if (krkrsdl2_init_platform())
		{
			TVPTerminateCode = 0;
			return TVPTerminateCode;
		}

		krkrsdl2_run_main_loop();

#ifndef __EMSCRIPTEN__
		krkrsdl2_cleanup();
#endif
	}
	catch (...)
	{
		TVPTerminateCode = 2;
		return TVPTerminateCode;
	}
#ifdef _WIN32
	::TerminateProcess(::GetCurrentProcess(), (UINT)TVPTerminateCode);
#endif
	return TVPTerminateCode;
}

