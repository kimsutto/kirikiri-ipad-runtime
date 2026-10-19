// SPDX-License-Identifier: MIT
#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>
#include <string>

static id RuntimeLifecycleObservers[4] = {};
static bool RuntimeApplicationActive = true;
void RuntimeInstallLifecycleCallbacks(void (*callback)(bool)) {
    NSArray *names = @[UIApplicationWillResignActiveNotification, UISceneWillDeactivateNotification,
                       UIApplicationDidBecomeActiveNotification, UISceneDidActivateNotification];
    for (NSUInteger i = 0; i < 4; ++i) {
        const bool active = i >= 2;
        RuntimeLifecycleObservers[i] = [[NSNotificationCenter.defaultCenter
            addObserverForName:names[i] object:nil queue:nil usingBlock:^(NSNotification *) {
                if (RuntimeApplicationActive == active) return;
                RuntimeApplicationActive = active;
                callback(active);
            }] retain];
    }
}
void RuntimeRemoveLifecycleCallbacks() {
    for (id &observer : RuntimeLifecycleObservers) {
        if (observer) [NSNotificationCenter.defaultCenter removeObserver:observer];
        [observer release];
        observer = nil;
    }
}

const char *RuntimeDocumentsPath() {
    static std::string path;
    if (path.empty()) {
        @autoreleasepool {
            NSString *documents = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES).firstObject;
            path = documents.UTF8String;
            NSFileManager *files = NSFileManager.defaultManager;
            for (NSString *folder in @[@"Game", @"Saves"]) {
                [files createDirectoryAtPath:[documents stringByAppendingPathComponent:folder]
                 withIntermediateDirectories:YES attributes:nil error:nil];
            }
        }
    }
    return path.c_str();
}
