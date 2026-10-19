#!/usr/bin/env python3
"""Fetch pinned sources and generate an iOS Xcode project. No game data required."""
import argparse
import json
import platform
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    subprocess.run([str(a) for a in args], check=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=["device", "simulator"], default="device")
    parser.add_argument("--work-dir", type=Path, default=ROOT / ".local")
    parser.add_argument("--bundle-id", default="org.example.kirikiri.ipad")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+){2,}", args.bundle_id):
        parser.error("Use a reverse-DNS bundle ID, for example org.example.kirikiri.ipad")
    for executable in ["git", "cmake", "xcodebuild"]:
        if not shutil.which(executable):
            parser.error(executable + " is missing; see README prerequisites")
    work = args.work_dir.expanduser().resolve()
    if work == ROOT or work in ROOT.parents:
        parser.error("Work directory must not be the repository root or its parent")
    work.mkdir(parents=True, exist_ok=True)
    lock = json.loads((ROOT / "upstream.json").read_text())
    engine = work / "engine"
    if not engine.exists():
        run("git", "init", engine)
        run("git", "-C", engine, "remote", "add", "origin", lock["repository"])
    origin = subprocess.check_output(["git", "-C", str(engine), "remote", "get-url", "origin"], text=True).strip()
    if origin != lock["repository"]:
        parser.error("Unexpected engine origin; use a new empty work directory")
    try:
        head = subprocess.check_output(["git", "-C", str(engine), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except subprocess.CalledProcessError:
        head = ""
    if not head:
        run("git", "-C", engine, "fetch", "--depth", "1", "origin", lock["commit"])
        run("git", "-C", engine, "checkout", "--detach", lock["commit"])
    elif head != lock["commit"]:
        parser.error("Unexpected engine revision; use a new empty work directory")
    run("git", "-C", engine, "submodule", "update", "--init", "--recursive", "--depth", "1")
    for path in (ROOT / "overlay").rglob("*"):
        if path.is_file():
            target = engine / path.relative_to(ROOT / "overlay")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    shutil.copytree(ROOT / "demo", work / "data", dirs_exist_ok=True)
    shutil.copy2(engine / "external/krkrz/external/angle/src/libANGLE/overlay/DejaVuSansMono-Bold.ttf", work / "data/DejaVuSansMono-Bold.ttf")
    shutil.copytree(ROOT / "licenses", work / "data/licenses", dirs_exist_ok=True)
    for notice in engine.rglob("*"):
        if ".git" in notice.relative_to(engine).parts:
            continue
        if notice.is_file() and notice.name.lower().startswith(("license", "copying", "copyright", "ofl")):
            destination = work / "data/licenses/upstream" / notice.relative_to(engine)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(notice, destination)
    sdk = "iphoneos" if args.platform == "device" else "iphonesimulator"
    build = work / ("build-" + args.platform)
    run("cmake", "-S", engine, "-B", build, "-G", "Xcode",
        "-DCMAKE_SYSTEM_NAME=iOS", "-DCMAKE_OSX_SYSROOT=" + sdk,
        "-DCMAKE_OSX_ARCHITECTURES=" + ("arm64" if platform.machine() == "arm64" or args.platform == "device" else "x86_64"),
        "-DCMAKE_OSX_DEPLOYMENT_TARGET=16.0", "-DOPTION_ENABLE_EXTERNAL_PLUGINS=OFF",
        "-DSDL_JOYSTICK=OFF", "-DSDL_HAPTIC=OFF", "-DSDL_VULKAN=OFF",
        "-DKRKRSDL2_IOS_CODE_SIGN_IDENTITY=" + ("Apple Development" if args.platform == "device" else ""),
        "-DRUNTIME_BUNDLE_ID=" + args.bundle_id, "-DEMBED_DATA_PATH=" + str(work / "data"))
    print("Project:", build / "krkrsdl2.xcodeproj")
    print("Open in Xcode, select your iPad/simulator, and use your own signing account.")

if __name__ == "__main__":
    main()
