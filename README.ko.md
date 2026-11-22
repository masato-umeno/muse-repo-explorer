# muse-repo-explorer

[English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | **한국어**

muse-repo-explorer는 GitHub 저장소의 로컬 clone을 Muse 환경에 유지하고, 다음 두 가지 용도로 제공합니다.

- **Muse용:** 소스 코드를 로컬 파일에서 읽습니다. 커넥터를 거치는 것보다 빠르며 토큰 사용량도 크게 줄어듭니다.
- **사용자용:** clone의 스냅샷으로 스마트폰 열람에 맞춘 비공개 코드 브라우저(Muse 스페이스)를 만듭니다. 파일명과 파일 내용을 검색할 수 있고, Markdown은 서식을 적용해 표시하며 Mermaid 다이어그램도 렌더링합니다. 페이지는 사용자의 언어(영어, 일본어, 중국어, 한국어)로 구축됩니다. 각 저장소의 내용은 필요할 때만 불러오므로 저장소가 늘어나도 느려지지 않습니다.

## 설치

다음 프롬프트를 Muse에 보내십시오. 설치 중에 필요한 작업은 GitHub 로그인 승인과 대상 저장소 선택 두 가지입니다. 저장소는 최소 하나가 필요하며, 이 저장소를 샘플로 사용할 수도 있습니다. 프롬프트는 언제든지 다시 보낼 수 있으며, 완료된 단계는 건너뜁니다.

````text
"muse-repo-explorer"를 내 환경에 구축해 주세요. 작업 내내 다음 규칙을 지켜 주세요.
- 토큰 절약: 아래 명령만 실행하고 그 짧은 출력만 읽을 것. dist/ 아래의 파일과 snapshot.json 은 열거나 출력하거나 붙여넣지 말고 파일 경로 그대로 업로드할 것. 스크립트를 직접 작성하거나 페이지를 직접 만들지 말 것(페이지는 이미 완성되어 있음).
- 개인정보: 스페이스는 비공개로 유지하고 공개 링크는 절대 만들지 말 것. 비밀번호나 토큰을 나에게 요구하지 말 것. 내가 고른 저장소만 clone할 것.

아래 단계에서 C 는 다음 명령을 뜻합니다: python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py

1. 도구 받기. ~/workspace/muse-repo-explorer 가 있으면 `git -C ~/workspace/muse-repo-explorer pull --ff-only`, 없으면 `git clone https://github.com/masato-umeno/muse-repo-explorer ~/workspace/muse-repo-explorer` 를 실행한다. 이어서 `C setup --lang LANG` 을 실행한다. LANG 은 내가 이 대화에서 쓰는 언어(en, ja, zh-CN, ko 중 하나)로 한다. 그 밖의 언어라면 --lang 없이 `C setup` 을 실행한다.
2. 로그인(setup 이 "signed in" 을 출력했으면 생략). `C login` 을 실행하고 출력된 URL과 코드를 그대로 나에게 보여 준다. 이어서 `C login --wait` 를 실행한다(내가 승인하면 끝난다).
3. 저장소 선택. 저장소는 최소 하나가 필요하다. `C list` 를 실행해 결과를 보여 주고, 어떤 것을 포함할지 묻는다("비공개 저장소 전부"처럼 답할 수 있음). 내가 고른 것을 `C clone owner/repo ...` 로 받는다. 고를 수 있는 저장소가 없거나 내가 아무것도 고르지 않으면, 이 도구 자체의 저장소를 샘플로 포함할지 나에게 묻고, 동의하면 `C clone masato-umeno/muse-repo-explorer` 를 실행한다. clone 출력에서 저장소 합계가 1 이상이 될 때까지 다음 단계로 넘어가지 않는다.
4. 빌드. `C refresh` 를 실행한다.
5. 스페이스 만들기. refresh 가 출력한 폴더의 모든 파일을 data/ 하위 폴더 구조를 유지한 채 수정 없이 업로드해 비공개 Muse 스페이스 "저장소 탐색기"를 만든다. 스페이스에 HTML 파일을 하나만 둘 수 있으면 대신 explorer.html 을 업로드한다. 그 뒤 `C mark-synced --mode folder` (한 파일이면 `--mode single-file`)을 실행한다.
6. 3줄 이내로 보고: GitHub 계정, 저장소 수, 만든 스페이스.

앞으로를 위해 기억해 두세요: 내가 "탐색기 최신화해 줘"라고 하거나, 내가 이미 가진 정기 작업이 끝날 때 `C refresh` 를 실행한다. UP_TO_DATE 가 나오면 거기서 끝. PAGE_UPDATE_NEEDED 가 나오면 나열된 파일만 업로드하고, 삭제 대상으로 나열된 파일을 삭제한 뒤 `C mark-synced` 를 실행한다.
````

## 사용법

- **페이지 최신화:** Muse에 "탐색기 최신화해 줘"라고 요청합니다. 새 커밋이 있을 때만 스페이스가 갱신되며, 해당 저장소의 파일만 업로드됩니다.
- **저장소 추가:** Muse에 clone을 요청한 뒤 최신화합니다.
- **파일 숨기기:** `~/workspace/repo-explorer/exclude.txt`에 glob 패턴(예: `.env*`, `*.pem`)을 적습니다. 자세한 내용은 [운영](docs/operations.md)을 참고하십시오.

## 보안

스냅샷에는 대상 저장소의 소스 코드 전체가 포함됩니다. 탐색기 페이지는 비공개로 유지하고, `snapshot.json`을 커밋하거나 공유하지 마십시오. 로그인은 디바이스 플로로만 하십시오. 자세한 내용은 [보안](docs/security.md)을 참고하십시오.

## 문서

문서는 영어로 작성되어 있습니다.

| 문서 | 내용 |
| --- | --- |
| [아키텍처](docs/architecture.md) | 구성 요소, 데이터 흐름, 설계 판단, 토큰 효율 |
| [보안](docs/security.md) | 다루는 데이터, 내장 보호 기능, 사용자 권장 사항 |
| [수동 설치](docs/manual-setup.md) | 프롬프트 없이 직접 또는 Claude Code로 구축하는 절차 |
| [운영](docs/operations.md) | 최신화, 유지 관리, 문제 해결, 제거 |
| [레퍼런스](docs/reference.md) | 명령, 설정, 상태 파일, 스냅샷 형식 |
| [탐색기 페이지](docs/page.md) | 포함된 페이지의 제공 형식과 동작 |

## 기여

이 저장소는 공개 저장소입니다. 첫 커밋 전에 [CONTRIBUTING.md](CONTRIBUTING.md)를 읽어 주십시오.

## 라이선스

[MIT](LICENSE)
