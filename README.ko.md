# muse-repo-explorer

[English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | **한국어**

muse-repo-explorer는 GitHub 저장소의 로컬 clone을 Muse 환경에 유지하고, 다음 두 가지 용도로 제공합니다.

- **Muse용:** 소스 코드를 로컬 파일에서 읽습니다. 커넥터를 거치는 것보다 빠르며 토큰 사용량도 크게 줄어듭니다.
- **사용자용:** clone의 스냅샷으로 스마트폰 열람에 맞춘 비공개 코드 브라우저(Muse 스페이스)를 만듭니다. 파일명과 파일 내용을 검색할 수 있고, 선택한 범위를 질문과 함께 Muse에 전달할 수 있으며, Markdown은 서식을 적용해 표시하며 Mermaid 다이어그램도 렌더링합니다. 페이지는 사용자의 언어(영어, 일본어, 중국어, 한국어)로 표시되며 설정에서 바꿀 수 있습니다. 각 저장소의 내용은 필요할 때만 불러오므로 저장소가 늘어나도 느려지지 않습니다.

## 설치

다음 한 줄을 Muse에 보내십시오. 영어 그대로 보내도 되며, Muse는 평소 쓰던 언어로 계속 응답합니다.

```text
Set up muse-repo-explorer for me by following https://github.com/masato-umeno/muse-repo-explorer/blob/main/MUSE_SETUP.md (keep replying in the language we normally use)
```

Muse는 [MUSE_SETUP.md](MUSE_SETUP.md)를 읽은 뒤, 도구 자체의 안내에 따라 한 단계씩 진행합니다. 도중에 필요한 작업은 GitHub 로그인 승인과 대상 저장소 선택입니다. 저장소는 최소 하나가 필요하며, 이 저장소를 샘플로 사용할 수도 있습니다. 페이지는 평소 Muse와 대화하는 언어로 표시되며, 페이지의 설정(톱니바퀴 버튼)에서 언제든지 바꿀 수 있습니다. 나중에 같은 한 줄을 다시 보내도 문제없습니다. 완료된 단계는 건너뛰고, 기존 환경(이전 버전으로 구축한 환경 포함)은 최신 버전으로 업데이트됩니다.

이 한 줄은 이 저장소에 저장된 지시를 Muse가 따르게 합니다. 특정 버전으로 고정하려면 URL의 `main`을 커밋 ID 또는 릴리스 태그로 바꾸십시오.

## 사용법

- **페이지 최신화:** Muse에 "탐색기 최신화해 줘"라고 요청하거나 설치용 한 줄을 다시 보냅니다. 새 커밋이 있을 때만 스페이스가 갱신되며, 해당 저장소의 파일만 업로드됩니다.
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
