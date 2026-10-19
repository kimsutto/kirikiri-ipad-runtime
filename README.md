# Kirikiri iPad Runtime

키리키리 게임 데이터를 iPad에서 실행하는 실험적인 오픈소스 프로젝트입니다.

게임 파일, 번역 패치, 게임 화면, 세이브는 포함하지 않습니다. 처음 설치하면 직접 만든 간단한 데모가 나타납니다. 게임 데이터는 사용자가 자신의 iPad에 직접 넣습니다.

키리키리 엔진을 iPad용으로 빌드한 뒤 게임 데이터를 읽는 방식입니다. Windows `.exe`와 `.dll`은 실행할 수 없습니다. 키리키리 게임도 전용 플러그인·폰트·스크립트에 따라 추가 수정이 필요할 수 있습니다.

## 처음이라면: 전체 순서

1. Mac에 Xcode와 CMake를 준비합니다.
2. 이 저장소를 다운로드하고 준비 명령을 실행합니다.
3. 생성된 Xcode 프로젝트에서 본인 Apple 계정과 iPad를 선택합니다.
4. 앱을 설치하고 테스트 화면가 보이는지 확인합니다.
5. 합법적으로 보유한 호환 게임 데이터를 iPad의 `Game` 폴더에 넣습니다.
6. 앱을 완전히 닫고 다시 실행합니다.

게임 데이터를 바꿀 때마다 앱을 다시 빌드할 필요는 없습니다. 현재 버전은 앱 하나에 게임 한 개를 넣어 사용합니다.

## 1. 준비물

- **Mac**: 실제 iPad용 앱을 빌드하고 서명하는 데 필요합니다.
- **Xcode 전체 앱**: Command Line Tools만으로는 부족합니다. iPad의 OS를 지원하는 버전이어야 합니다.
- **iPad와 연결 케이블**, 본인의 Apple 계정.
- **Git, Python 3, CMake**, 최초 소스 다운로드를 위한 인터넷 연결.
- 충분한 저장 공간과, 수정·사용 권한이 있는 게임 데이터.

앱은 iPadOS 16 이상을 대상으로 빌드합니다. 실제로 확인한 환경과 남은 문제는 [검증 기록](VERIFICATION.md)에 적어 두었습니다.

### Mac 준비

1. App Store에서 Xcode를 설치하고 **한 번 실행**해 추가 구성요소 설치를 마칩니다.
2. 터미널을 열어 아래 명령으로 도구가 보이는지 확인합니다.

```sh
xcodebuild -version
python3 --version
git --version
cmake --version
```

`cmake: command not found`가 나오면 [CMake 공식 설치 안내](https://cmake.org/download/)를 참고하세요. 이미 Homebrew를 사용한다면 다음 명령으로 설치할 수 있습니다.

```sh
brew install cmake
```

`xcodebuild`가 전체 Xcode를 찾지 못하고 Command Line Tools 경로를 가리킨다면, Xcode를 설치한 뒤 다음과 같이 개발 도구 경로를 선택합니다. Xcode를 다른 위치에 설치했다면 그 경로로 바꾸세요.

```sh
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
```

Mac 암호나 Apple 계정 암호는 Apple이 표시하는 창에 직접 입력하세요. 저장소 설정 파일에 적지 않습니다.

## 2. 소스 준비와 프로젝트 생성

GitHub 저장소의 **Code → Download ZIP**으로 내려받아 압축을 풉니다. 터미널에서 압축을 푼 폴더로 이동하세요. `cd `를 입력하고 Finder의 해당 폴더를 터미널로 끌어온 뒤 Enter를 누르면 경로를 직접 입력하지 않아도 됩니다.

이후 다음을 실행합니다.

```sh
python3 tools/prepare.py --platform device --bundle-id org.example.kirikiri.myipad
```

- `org.example.kirikiri.myipad`는 앱의 식별자입니다. 충돌한다면 `org.example.kirikiri.myreader`처럼 본인만 사용하는 값으로 바꾸세요. 실명이나 이메일을 사용할 필요는 없습니다.
- 정해진 버전의 엔진 소스와 필요한 라이브러리를 내려받고, 이 저장소의 수정 파일을 적용합니다.
- 게임이나 개인 자료를 다운로드하거나 업로드하지 않습니다.
- 최초 실행은 네트워크와 Mac 성능에 따라 시간이 걸립니다.
- 결과는 `.local/`에 생깁니다. 이 폴더에는 빌드 경로와 개인 서명 설정이 들어갈 수 있으므로 **공개하지 마세요**.

완료되면 프로젝트를 엽니다.

```sh
open .local/build-device/krkrsdl2.xcodeproj
```

중간에 다운로드가 끊겼다면 같은 명령을 다시 실행할 수 있습니다. `Unexpected engine revision/origin` 오류는 다른 소스가 섞이지 않도록 한 검사입니다. 기존 작업을 덮어쓰지 말고 다음처럼 새 작업 폴더를 지정하세요.

```sh
python3 tools/prepare.py --platform device --work-dir .local/retry --bundle-id org.example.kirikiri.myipad
```

이 경우 출력된 새 프로젝트 경로를 사용합니다.

## 3. 본인 계정으로 서명하고 iPad에 설치

1. iPad를 Mac에 연결하고 iPad의 잠금을 풉니다. ‘이 컴퓨터를 신뢰하겠습니까?’가 나오면 직접 신뢰합니다.
2. Xcode의 **Settings → Accounts**에서 본인 Apple 계정으로 로그인합니다.
3. 프로젝트에서 **TARGETS → krkrsdl2 → Signing & Capabilities**로 이동합니다.
4. **Automatically manage signing**을 켜고 **Team**에서 본인의 팀을 고릅니다.
5. **Bundle Identifier**가 앞에서 정한 값인지 확인합니다. 충돌하면 다른 값으로 바꿉니다.
6. Xcode 위쪽의 실행 스킴을 **krkrsdl2**, 실행 기기를 **연결한 iPad**로 선택합니다.
7. **Run(▶)**을 누릅니다. 첫 빌드는 시간이 걸릴 수 있습니다.

필요하면 iPad에서 **설정 → 개인정보 보호 및 보안 → 개발자 모드**를 켜고 재시동 후 확인합니다. 개발자 앱 신뢰를 요청하면 **설정 → 일반 → VPN 및 기기 관리**에서 본인 개발자 계정을 확인하고 신뢰하세요. 메뉴는 OS 버전에 따라 다를 수 있습니다.

Mac의 `codesign` 키체인 확인창은 앱 서명 키 사용을 승인하는 창입니다. 본인이 빌드를 시작한 상황인지 확인하고 Mac에서 직접 처리하세요.

- [Apple: 개발자 모드 활성화](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device)
- [Apple: 개발자 계정 종류와 Personal Team 제한](https://developer.apple.com/help/account/basics/about-your-developer-account)

무료 Personal Team은 프로비저닝에 유효기간이 있어 주기적으로 다시 서명·설치해야 합니다. 기한이 지나 실행되지 않을 때는 **앱을 삭제하지 말고** 같은 계정·Bundle Identifier로 Xcode에서 다시 설치하세요. 삭제하면 앱 내부 세이브도 지워질 수 있습니다.

## 4. 데모로 설치 확인

게임 파일이 없는 상태에서는 `Kirikiri iPad Runtime` 제목과 `Engine ready` 안내가 나옵니다. 화면을 누르면 숫자가 올라갑니다.

이 데모로 엔진이 시작되고, 글자를 그리며, 터치에 반응하는지 확인할 수 있습니다. 데모에 쓰는 영문 폰트는 공개 라이선스 폰트이며, 사용자 게임의 한글·일본어 폰트는 별도로 필요할 수 있습니다.

## 5. 내 게임 데이터 넣기

### 어떤 파일이 필요한가요?

키리키리 게임은 보통 `.xp3` 아카이브나 `startup.tjs`가 있는 데이터 폴더를 사용합니다. 확장자만으로 완전한 호환성을 판단할 수는 없습니다.

현재 엔진은 다음 순서로 시작 파일을 고릅니다.

1. `Game/startup.tjs`가 있으면 그 폴더의 스크립트를 실행합니다.
2. 없으면 `Game/data.xp3` 안의 `startup.tjs`를 실행합니다.
3. 둘 다 없으면 기본 데모를 표시합니다.

`EXE`와 Windows용 `DLL`을 복사해도 iPad에서 실행되지는 않습니다. XP3가 암호화돼 있거나 별도의 실행 파일에 데이터가 묶여 있다면 이 도구만으로 가져올 수 없을 수 있습니다. DRM 해제 기능은 제공하지 않습니다.

### iPad에 복사하기

1. 앱을 한 번 실행합니다. `Game`과 `Saves` 폴더가 만들어집니다.
2. iPad의 **파일 앱 → 나의 iPad → Kirikiri iPad Runtime → Game**을 엽니다.
3. 본인이 보유한 게임 데이터의 파일·하위 폴더 구조를 유지해서 넣습니다. AirDrop이나 iCloud Drive 등으로 먼저 옮겨 와서 복사할 수 있습니다.
4. 실행 중인 앱을 앱 전환기에서 완전히 닫고 다시 엽니다.

예를 들어 폴더가 다음처럼 되어야 합니다.

```text
Kirikiri iPad Runtime/
├── Game/
│   ├── data.xp3
│   ├── ...게임에 필요한 나머지 데이터...
│   └── video-ios/       # 외부 MP4를 사용하는 경우
└── Saves/
```

풀린 스크립트 형태라면 다음 구조도 가능합니다.

```text
Game/
├── startup.tjs
├── scenario/
└── ...기타 리소스...
```

`Game/게임폴더/data.xp3`처럼 한 단계 더 들어가 있으면 현재 자동 검색에서 찾지 못합니다. 게임이 요구하는 패치 적용 순서는 원래 게임의 스크립트·설명에 따릅니다. 이 엔진이 번역 패치를 자동으로 찾거나 적용하지는 않습니다.

### 데이터만 넣었는데 실행되지 않아요

일부 게임은 Windows 메뉴, 모달 창, 외부 플러그인 또는 전용 폰트를 기대합니다. 이런 기능을 사용하는 게임은 스크립트나 엔진 코드를 직접 수정해야 할 수 있습니다.

내장 플러그인은 KAGParser, AlphaMovie, 일부 전환 효과와 Vorbis 오디오를 지원합니다. 외부 Windows DLL 로딩은 비활성화되어 있습니다. 정확한 시작 스크립트와 필요한 플러그인이 맞는지 확인하세요. 문제를 제보할 때 게임 전체 파일을 올리지 마세요.

### 영상이 필요한 경우

iOS 동영상 경로는 `Game/video-ios/`의 로컬 파일을 사용합니다. 스크립트가 `ending.wmv`를 열면 `Game/video-ios/ending.mp4`를 찾도록 되어 있습니다. 원본 WMV를 이 폴더에 복사하는 것만으로 변환되지는 않습니다.

변환할 권한이 있는 영상은 별도 도구로 iPad가 재생할 수 있는 MP4(예: H.264 영상/AAC 음성)로 변환해야 합니다. 현재 저장소에는 상용 게임 영상이나 변환된 영상, 아카이브 추출 도구를 포함하지 않습니다. 영상 위치·프레임 단위 제어 등 모든 Windows 동영상 기능이 구현된 것은 아닙니다.

## 6. 세이브와 재설치

- 엔진의 기본 데이터 경로는 `Documents/Saves`입니다. 실제 저장 방식·파일명·클리어 조건은 게임 스크립트가 결정합니다. 일부 게임이 별도 경로를 사용할 수도 있습니다.
- 앱 삭제·기기 교체·다른 게임으로 교체하기 전에는 `Saves`와 게임이 별도로 쓰는 저장 폴더를 복사해 두세요.
- 한 앱에서 게임을 바꿀 때 서로 다른 게임의 저장 파일을 섞지 마세요. 백업 후 데이터와 저장을 구분하거나 다른 Bundle Identifier로 별도의 앱을 만드세요.
- 앱이 백그라운드로 전환되면 스크립트에 알립니다. 이때 자동 저장하려면 게임 스크립트에서도 저장 처리를 해야 합니다.
- 네이티브 `System.confirm` API가 추가되어 있지만, 게임이 기존 Windows 모달 창을 쓰면 로컬 호환 코드에서 이 API를 호출하도록 바꿔야 합니다.

## 자주 겪는 문제

| 증상 | 먼저 확인할 것 |
|---|---|
| 기기가 Xcode 목록에 없음 | 케이블, 잠금 해제, 컴퓨터 신뢰, Xcode의 해당 OS 지원 여부 |
| Signing/Provisioning 오류 | 본인 Team, 고유 Bundle Identifier, 계정 로그인, 네트워크 |
| 며칠 뒤 앱이 열리지 않음 | 개발 서명 만료 여부. 세이브 백업 후 같은 식별자로 다시 빌드·설치 |
| 파일을 넣어도 데모만 보임 | `Game` 바로 아래의 `startup.tjs` 또는 `data.xp3`, 중첩 폴더 여부 |
| 스크립트·플러그인 오류 | 게임이 요구하는 엔진 버전과 전용 플러그인 |
| 한글·일본어가 깨지거나 글꼴 오류 | 게임에서 요구하는 폰트와 로딩 코드. 데모 폰트는 영문용 |
| 영상이 재생되지 않음 | `video-ios` 파일명, MP4 코덱, 변환 결과와 원본의 길이 |
| 잘못된 데이터로 시작하며 오류 반복 | 파일 앱에서 `Game` 폴더의 해당 시작 파일을 다른 위치로 옮기고 앱 재실행 |

오류 로그에는 개인 경로, 기기 정보나 게임 대사가 들어갈 수 있습니다. 제보 전에 해당 정보를 지우고 오류 종류와 최소 재현 절차만 공유하세요. 인증서·프로비저닝 파일·암호·세이브는 올리지 마세요.

## 개발자용: 시뮬레이터와 검사

```sh
python3 tools/prepare.py --platform simulator
xcodebuild -project .local/build-simulator/krkrsdl2.xcodeproj \
  -scheme krkrsdl2 -configuration Release -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO
```

Xcode에서 시뮬레이터를 선택하고 Run을 눌러도 됩니다. 실제 iPad 성능과 동일하지는 않습니다.

원본 게임 데이터가 필요 없는 검사:

```sh
python3 -B tests/test_public_check.py
c++ -std=c++17 -pthread tests/audio_completions.cpp -o /tmp/kirikiri-audio-test
/tmp/kirikiri-audio-test
```

공개 검사 도구는 빌드 결과가 없는 **깨끗한 소스 사본**에서 실행합니다. `.local/`은 검사에서 의도적으로 거부합니다. Git 추적 파일만 별도 폴더로 내보내 검사하는 것도 가능합니다.

```sh
python3 -B tools/check_public.py
```

이 도구는 공개하면 안 되는 파일 형식, 빌드 결과물, 일부 비밀정보 패턴을 검사합니다. 놓치는 정보도 있으니 공개할 파일과 Git 이력을 직접 확인하세요.

## 구성과 라이선스

- `overlay/`: 고정된 공개 엔진에 적용하는 수정 소스
- `demo/`: 게임 자료를 사용하지 않은 테스트 스크립트
- `tools/`: 소스 준비와 공개 파일 검사
- `tests/`: 오디오 완료 처리와 검사 도구 테스트
- `upstream.json`: 원본 저장소와 커밋
- `licenses/`, [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md): 원저작권·의존성 라이선스
- [VERIFICATION.md](VERIFICATION.md): 실제 검증 범위와 남은 제한

새로 작성한 코드는 MIT 라이선스이며 기존 코드에는 각 원본 라이선스가 적용됩니다. 게임 구매가 게임 데이터·번역·변환 영상의 재배포 허가를 뜻하지는 않습니다. 게임 파일은 이 저장소나 공개 이슈에 올리지 마세요.
