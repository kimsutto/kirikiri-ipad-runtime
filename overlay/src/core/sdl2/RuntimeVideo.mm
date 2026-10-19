// SPDX-License-Identifier: MIT
#import <AVFoundation/AVFoundation.h>
#import <UIKit/UIKit.h>
#include "RuntimeVideo.h"
#include <cmath>

@interface RuntimeVideoView : UIView
@end
@implementation RuntimeVideoView
+ (Class)layerClass { return [AVPlayerLayer class]; }
@end

@interface RuntimeVideoSession : NSObject
@property(nonatomic, strong) AVPlayer *player;
@property(nonatomic, strong) RuntimeVideoView *view;
@property(nonatomic, strong) id endObserver;
@property(nonatomic) BOOL finished;
@end
@implementation RuntimeVideoSession
- (void)dealloc {
    if (_endObserver) [[NSNotificationCenter defaultCenter] removeObserver:_endObserver];
    [_player pause];
    [_view removeFromSuperview];
}
@end

static RuntimeVideoSession *Session(void *handle) {
    return (__bridge RuntimeVideoSession *)handle;
}

void *RuntimeVideoOpen(const char *path) {
    NSCAssert([NSThread isMainThread], @"Video must use the UIKit thread");
    NSString *filename = [NSString stringWithUTF8String:path];
    if (!filename || ![[NSFileManager defaultManager] isReadableFileAtPath:filename]) return nullptr;
    UIWindow *window = nil;
    for (UIScene *scene in UIApplication.sharedApplication.connectedScenes) {
        // KAG can open a movie while UIKit is still activating the existing game window.
        if ([scene isKindOfClass:UIWindowScene.class] &&
            (scene.activationState == UISceneActivationStateForegroundActive ||
             scene.activationState == UISceneActivationStateForegroundInactive)) {
            for (UIWindow *candidate in ((UIWindowScene *)scene).windows) {
                if (candidate.isKeyWindow) { window = candidate; break; }
            }
        }
    }
    if (!window.rootViewController) return nullptr;
    RuntimeVideoSession *session = [RuntimeVideoSession new];
    session.player = [AVPlayer playerWithURL:[NSURL fileURLWithPath:filename]];
    session.player.actionAtItemEnd = AVPlayerActionAtItemEndPause;
    UIView *parent = window.rootViewController.view;
    // shortcut: video fills the viewport; arbitrary overlay rectangles are not implemented.
    session.view = [[RuntimeVideoView alloc] initWithFrame:parent.bounds];
    session.view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    session.view.userInteractionEnabled = NO; // KAG retains its original skip/click policy.
    session.view.backgroundColor = UIColor.blackColor;
    session.view.hidden = YES;
    AVPlayerLayer *layer = (AVPlayerLayer *)session.view.layer;
    layer.player = session.player;
    layer.videoGravity = AVLayerVideoGravityResizeAspect;
    [parent addSubview:session.view];
    __weak RuntimeVideoSession *weakSession = session;
    session.endObserver = [[NSNotificationCenter defaultCenter]
        addObserverForName:AVPlayerItemDidPlayToEndTimeNotification
        object:session.player.currentItem queue:NSOperationQueue.mainQueue
        usingBlock:^(NSNotification *) { weakSession.finished = YES; }];
    return (__bridge_retained void *)session;
}
void RuntimeVideoClose(void *handle) {
    if (!handle) return;
    RuntimeVideoSession *session = (__bridge_transfer RuntimeVideoSession *)handle;
    [session.player pause];
    [session.view removeFromSuperview];
}
void RuntimeVideoPlay(void *handle) { [Session(handle).player play]; }
void RuntimeVideoPause(void *handle) { [Session(handle).player pause]; }
void RuntimeVideoSeek(void *handle, double seconds) {
    RuntimeVideoSession *session = Session(handle);
    session.finished = NO;
    [session.player seekToTime:CMTimeMakeWithSeconds(seconds, 600)
               toleranceBefore:kCMTimeZero toleranceAfter:kCMTimeZero];
}
void RuntimeVideoVisible(void *handle, bool visible) { Session(handle).view.hidden = !visible; }
void RuntimeVideoVolume(void *handle, float volume) { Session(handle).player.volume = volume; }
int RuntimeVideoState(void *handle) {
    RuntimeVideoSession *session = Session(handle);
    if (!session || session.player.status == AVPlayerStatusFailed ||
        session.player.currentItem.status == AVPlayerItemStatusFailed) return -1;
    if (session.finished) return 2;
    return session.player.currentItem.status == AVPlayerItemStatusReadyToPlay ? 1 : 0;
}
double RuntimeVideoPosition(void *handle) {
    const double value = CMTimeGetSeconds(Session(handle).player.currentTime);
    return std::isfinite(value) ? value : 0;
}
double RuntimeVideoDuration(void *handle) {
    const double value = CMTimeGetSeconds(Session(handle).player.currentItem.duration);
    return std::isfinite(value) ? value : 0;
}
