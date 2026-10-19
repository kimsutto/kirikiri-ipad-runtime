// SPDX-License-Identifier: MIT
#pragma once
void *RuntimeVideoOpen(const char *path);
void RuntimeVideoClose(void *handle);
void RuntimeVideoPlay(void *handle);
void RuntimeVideoPause(void *handle);
void RuntimeVideoSeek(void *handle, double seconds);
void RuntimeVideoVisible(void *handle, bool visible);
void RuntimeVideoVolume(void *handle, float volume);
// 0 loading, 1 ready, 2 genuinely finished, -1 failed.
int RuntimeVideoState(void *handle);
double RuntimeVideoPosition(void *handle);
double RuntimeVideoDuration(void *handle);
