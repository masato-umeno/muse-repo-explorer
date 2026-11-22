# muse-repo-explorer

[English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | **한국어**

Muse(개인 AI 에이전트) 환경에 GitHub 저장소를 로컬로 clone해 두고,

- **Muse는 로컬 파일에서 코드를 읽습니다** — 커넥터를 거치는 것보다 빠르고 토큰도 훨씬 적게 씁니다.
- **당신은 스마트폰에서 코드를 읽습니다** — 코드 스냅샷이 들어 있는 나만의 "파일 탐색기" 페이지(Muse 스페이스)에서.

## 시작하기: 이 내용을 Muse에 붙여넣기만 하세요

아래 블록 전체를 복사해서 Muse에 보내세요. Muse가 중간에 묻는 것은 두 가지뿐입니다:
(1) GitHub 로그인용 일회용 코드, (2) clone할 저장소 범위.

````text
"muse-repo-explorer"(https://github.com/masato-umeno/muse-repo-explorer)를 내 환경에 구축해 주세요. 마지막의 개인정보 규칙을 반드시 지켜 주세요.

1. 도구 설치 (VM이 교체되어도 남도록 홈 디렉터리 아래에 설치)
   - github.com/x-motemen/ghq 의 최신 ghq 릴리스 바이너리를 ~/.local/bin/ghq 에 둔다.
   - github.com/cli/cli 의 최신 gh(GitHub CLI) 릴리스 바이너리를 ~/.local/bin/gh 에 둔다.
   - 각각 --version 으로 동작을 확인한다.

2. GitHub 로그인 (디바이스 플로, HTTPS만)
   - `gh auth login --hostname github.com --git-protocol https --web` 를 실행한다.
   - 일회용 코드와 https://github.com/login/device 를 나에게 보여 주고, 내가 브라우저에서 승인할 때까지 기다린다.
   - 완료되면 `gh auth status` 의 계정 이름을 알려 주고 `gh auth setup-git` 을 실행한다.
   - SSH는 사용하지 않는다. 비밀번호나 토큰을 붙여넣게 하지 않는다.

3. 저장소 clone
   - 내가 접근할 수 있는 저장소(`gh repo list`, 소속 조직 포함)를 나열하고, 어떤 것을 clone할지 나에게 확인한 뒤 각각 `ghq get <owner>/<repo>` 를 실행한다.
   - 따로 요청하지 않으면 보관(archived)된 저장소는 제외한다.

4. 스냅샷 도구 설치
   - `ghq get https://github.com/masato-umeno/muse-repo-explorer` 를 실행한다.
   - 그 tools/ 디렉터리의 모든 파일을 ~/workspace/repo-explorer/ (어떤 git 저장소 안도 아닌 곳)에 복사하고 스크립트에 실행 권한을 준다.
   - `python3 ~/workspace/repo-explorer/update_snapshot.py` 를 실행해 snapshot.json 이 생성되는지 확인한다.
   - 페이지에 표시하고 싶지 않은 파일(예: `.env*`, `*.pem`, `secrets/*`)이 있는지 나에게 묻는다. 있으면 그 glob을 ~/workspace/repo-explorer/exclude.txt 에 적고 update_snapshot.py 를 다시 실행한다.

5. pull 훅 설치
   - `~/workspace/repo-explorer/install-hooks.sh` 를 실행한다.
   - 저장소 하나에서 pull 한 뒤 snapshot.json 이 다시 생성되었는지 확인한다.

6. 탐색기 페이지(Muse 스페이스) 만들기
   - 그 저장소의 docs/explorer-page-spec.md 사양대로 만든다. snapshot.json 은 하나의 독립된 에셋으로 두어, 그것만 교체하면 최신화되도록 한다.
   - 페이지 UI는 내 언어로 한다.
   - 페이지는 비공개로 유지하고, 공개 링크는 절대 만들지 않는다.

7. 최신화
   - 내가 "탐색기 최신화해 줘"라고 하면 update_snapshot.py → sync_status.py 순서로 실행한다. sync_status.py 의 종료 코드가 10일 때만 페이지의 스냅샷 에셋을 교체하고, 그 뒤 `sync_status.py --mark` 를 실행한다.
   - 선택: 주간 점검 같은 기존 정기 작업이 있으면, 그 끝에 이 최신화 단계를 덧붙여도 된다(채팅 보고는 불필요).

8. 결과 보고
   - `ghq list` 결과, 스냅샷 크기, 만든 페이지, 실패한 항목과 그 이유.

개인정보 규칙:
- snapshot.json 을 git, 공개 저장소, 파일 공유 서비스에 절대 두지 않는다.
- 탐색기 페이지를 공개 공유하지 않는다.
- 자격 증명(비밀번호, 토큰)을 채팅·파일·로그에 남기지 않는다.
- 내가 정당한 접근 권한을 가진 저장소만 clone한다.
````

## 시작하기 전에 — 세 가지 규칙

1. **스냅샷은 소스 코드 그 자체입니다.** `snapshot.json` 을 git이나 공유되는 곳에 두지 마세요.
2. **탐색기 페이지는 비공개로.** 공개 링크를 만들면 링크를 아는 누구나 코드를 읽을 수 있습니다.
3. **로그인은 디바이스 플로로만.** GitHub 비밀번호나 토큰을 채팅에 붙여넣지 마세요.

자세히: [docs/security.md](docs/security.md) (영어)

## 문서 (영어)

| 문서 | 내용 |
| --- | --- |
| [How it works](docs/design.md) | 전체 구조와 설계 판단 |
| [Security & privacy](docs/security.md) | 사용자 규칙과 이 공개 저장소의 안전 점검 |
| [Manual setup](docs/manual-setup.md) | 프롬프트 없이 직접 설치하기 (Claude Code용으로도) |
| [Operations](docs/operations.md) | 최신화, 훅, 파일 제외, 제거 |
| [Explorer page spec](docs/explorer-page-spec.md) | 스냅샷 형식과 페이지 UI 사양 |

## 기여하기

이 저장소는 **공개** 저장소입니다. 첫 커밋 전에 반드시 실행하세요:

```sh
sh scripts/install-dev-hooks.sh
```

스냅샷, 로그, 토큰, 개인 이메일 주소, 그리고 나만의 금지어 목록에 적은 실명을 커밋 전에 차단합니다.
CI에서도 push할 때마다 같은 점검이 실행됩니다.

## 라이선스

MIT — [LICENSE](LICENSE) 참고.
