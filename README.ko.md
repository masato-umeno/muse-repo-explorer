# muse-repo-viewer

[English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | **한국어**

Muse에서 동작하는 저장소 뷰어입니다. GitHub 저장소의 로컬 clone을 Muse 환경에 유지하여 다음을 할 수 있게 합니다.

- **사용자는** Muse의 비공개 스페이스에서 휴대폰으로 코드를 읽고 검색할 수 있으며, 선택한 줄에 대해 Muse에 질문할 수 있습니다.
- **Muse는** 소스 코드를 로컬 파일에서 읽습니다. 커넥터를 거치는 것보다 빠르고 토큰도 적게 씁니다.

소개 페이지: <https://masato-umeno.github.io/muse-repo-viewer/>

## 설치

다음 한 줄을 복사해 Muse에 붙여 넣으십시오. Muse는 평소 쓰는 언어로 계속 응답합니다.

```text
Set up muse-repo-viewer for me by following https://github.com/masato-umeno/muse-repo-viewer/blob/main/MUSE_SETUP.md (keep replying in the language we normally use)
```

설치 중에 GitHub 로그인 승인과 대상 저장소 선택을 요청받습니다(이 저장소를 샘플로 쓸 수 있습니다). 스페이스를 만들기 전 등에 계속할지 묻는다면 진행해도 된다고 답하십시오. 나중에 업데이트할 때도 같은 한 줄을 보내면 됩니다.

## 사용법

- **최신화:** Muse에 "뷰어 최신화해 줘"라고 요청합니다. 새 커밋이 있는 저장소만 업로드됩니다.
- **저장소 추가:** Muse에 clone을 요청한 뒤 최신화합니다.
- **파일 숨기기:** `~/workspace/repo-viewer/exclude.txt`에 `.env*` 같은 glob 패턴을 적습니다.
- **표시 언어:** 페이지 설정(톱니바퀴 버튼)에서 바꿀 수 있습니다.

## 보안

스페이스에는 대상 저장소의 소스 코드 전체가 들어갑니다. 비공개로 유지하십시오. 설치용 한 줄은 이 저장소에 있는 지시를 Muse가 따르게 합니다. 버전을 고정하려면 URL의 `main`을 커밋 ID나 태그로 바꾸십시오. 자세한 내용은 [보안](docs/security.md)을 참고하십시오.

## 문서

문서는 영어로 작성되어 있습니다.

| 문서 | 내용 |
| --- | --- |
| [아키텍처](docs/architecture.md) | 구성 요소, 데이터 흐름, 설계 판단, 토큰 효율 |
| [보안](docs/security.md) | 다루는 데이터, 내장 보호 기능, 사용자 권장 사항 |
| [수동 설치](docs/manual-setup.md) | 프롬프트 없이 직접 또는 Claude Code로 구축하는 절차 |
| [운영](docs/operations.md) | 최신화, 유지 관리, 문제 해결, 제거 |
| [레퍼런스](docs/reference.md) | 명령, 설정, 상태 파일, 스냅샷 형식 |
| [뷰어 페이지](docs/page.md) | 포함된 페이지의 제공 형식과 동작 |

## 기여

이 저장소는 공개 저장소입니다. 첫 커밋 전에 [CONTRIBUTING.md](CONTRIBUTING.md)를 읽어 주십시오.

## 라이선스

[MIT](LICENSE)
