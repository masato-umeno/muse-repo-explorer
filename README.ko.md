# muse-repo-explorer

[English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | **한국어**

GitHub 코드를 스마트폰에서 읽고, Muse(개인 AI 에이전트)도 적은 비용으로 코드를 읽게 하는 구조입니다.

- **Muse는 로컬 clone에서 코드를 읽습니다**: 커넥터보다 빠르고 토큰도 훨씬 적게 씁니다.
- **당신은 스마트폰에서 코드를 봅니다**: 나만의 탐색기 페이지(Muse 스페이스)에서. 페이지는 이 저장소에 포함되어 있으며
  English / 日本語 / 中文 / 한국어와 라이트·다크 테마를 지원합니다.

## 시작하기: 이 내용을 Muse에 붙여넣기만 하세요

아래 블록 전체를 복사해서 Muse에 보내세요. 당신이 할 일은 두 가지뿐입니다:
GitHub 로그인 코드 승인, 그리고 포함할 저장소 선택.

````text
"muse-repo-explorer"를 내 환경에 구축해 주세요. 작업 내내 다음 규칙을 지켜 주세요.
- 토큰 절약: 아래 명령만 실행하고 그 짧은 출력만 읽을 것. snapshot.json, index.html, explorer.html 은 열거나 출력하거나 붙여넣지 말고 파일 경로 그대로 업로드할 것. 스크립트를 직접 작성하거나 페이지를 직접 만들지 말 것(페이지는 이미 완성되어 있음).
- 개인정보: 페이지는 비공개로 유지하고 공개 링크는 절대 만들지 말 것. 비밀번호나 토큰을 나에게 요구하지 말 것. 내가 고른 저장소만 clone할 것.

아래 단계에서 C 는 다음 명령을 뜻합니다: python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py

1. 도구 받기. ~/workspace/muse-repo-explorer 가 있으면 `git -C ~/workspace/muse-repo-explorer pull --ff-only`, 없으면 `git clone https://github.com/masato-umeno/muse-repo-explorer ~/workspace/muse-repo-explorer` 를 실행한다. 이어서 `C setup` 을 실행한다.
2. 로그인(setup 이 "signed in" 을 출력했으면 생략). `C login` 을 실행하고 출력된 URL과 코드를 그대로 나에게 보여 준다. 이어서 `C login --wait` 를 실행한다(내가 승인하면 끝난다).
3. 저장소 선택. `C list` 를 실행해 결과를 보여 주고, 어떤 것을 포함할지 묻는다("비공개 저장소 전부"처럼 답할 수 있음). 내가 고른 것을 `C clone owner/repo ...` 로 받는다.
4. 빌드. `C refresh` 를 실행한다.
5. 페이지 만들기. refresh 가 출력한 파일을 수정 없이 업로드해 비공개 Muse 스페이스 "저장소 탐색기"를 만든다. 가능하면 index.html 과 snapshot.json 두 파일로 하고, 스페이스에 HTML 파일을 하나만 둘 수 있으면 explorer.html 을 쓴다. 그 뒤 `C mark-synced --mode two-file` (한 파일이면 `--mode single-file`)을 실행한다.
6. 3줄 이내로 보고: GitHub 계정, 저장소 수, 만든 페이지.

앞으로를 위해 기억해 두세요: 내가 "탐색기 최신화해 줘"라고 하거나, 내가 이미 가진 정기 작업이 끝날 때 `C refresh` 를 실행한다. UP_TO_DATE 가 나오면 거기서 끝. PAGE_UPDATE_NEEDED 가 나오면 지정된 파일만 페이지에서 교체하고 `C mark-synced` 를 실행한다.
````

나중에 다시 붙여넣어도 괜찮습니다. 이미 끝난 단계는 건너뜁니다.

## 시작하기 전에: 세 가지 규칙

1. **스냅샷은 소스 코드 그 자체입니다.** `snapshot.json` 을 git이나 공유되는 곳에 두지 마세요.
2. **탐색기 페이지는 비공개로.** 공개 링크를 만들면 링크를 아는 누구나 코드를 읽을 수 있습니다.
3. **로그인은 디바이스 플로로만.** GitHub 비밀번호나 토큰을 채팅에 붙여넣지 마세요.

자세히: [docs/security.md](docs/security.md) (영어)

## 문서 (영어)

| 문서 | 내용 |
| --- | --- |
| [How it works](docs/design.md) | 전체 구조, 설계 판단, 토큰 절약 방식 |
| [Security & privacy](docs/security.md) | 사용자 규칙과 이 공개 저장소의 안전 점검 |
| [Manual setup](docs/manual-setup.md) | 직접 설치하기(Claude Code용으로도)와 명령 목록 |
| [Operations](docs/operations.md) | 최신화, 훅, 파일 제외, 제거 |
| [Explorer page spec](docs/explorer-page-spec.md) | 스냅샷 형식과 포함된 페이지 |

## 기여하기

이 저장소는 **공개** 저장소입니다. 첫 커밋 전에 반드시 실행하세요:

```sh
sh scripts/install-dev-hooks.sh
```

스냅샷, 로그, 토큰, 개인 이메일 주소, 그리고 나만의 금지어 목록에 적은 실명을 커밋 전에 차단합니다.
CI에서도 push할 때마다 같은 점검이 실행됩니다.

## 라이선스

MIT. [LICENSE](LICENSE) 참고.
