# Roasting — 에이전트 팀 빌더 (실행 엔진)

![Version](https://img.shields.io/badge/Version-1.0.0-2ea44f)
![License](https://img.shields.io/badge/License-Apache%202.0-1f6feb)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-8957e6)
![Agents](https://img.shields.io/badge/Agents-50%20Verified-d2691e)
![Recipes](https://img.shields.io/badge/Recipes-12%20Harnesses-d2691e)
![Mode](https://img.shields.io/badge/Mode-Agent%20Teams-2ea44f)

![Layer](https://img.shields.io/badge/Layer-L3%20Execution-d2691e)
![Sub-layer](https://img.shields.io/badge/Sub--layer-Verified%20Team%20Executor-008080)
![Quality](https://img.shields.io/badge/Quality-9.5%20Gate-2ea44f)
![README](https://img.shields.io/badge/README-KO-555555)

> 목적 한 줄을 받아, 검증된 50명 에이전트 팀원 중에서 팀을 설계하고 **실제로 돌려** 검토 통과본까지 만들어 내는 Claude Code 스킬.

`AI ROASTING`이 로스팅(5색 다관점 채점)으로 검증한 50개 역할 프롬프트와 12개 검증된 팀 레시피를 기반으로, 사용자가 "무엇을 만들지(목적)"만 말하면 팀장(오케스트레이터)이 "누가 어떤 순서로 하는지"를 정하고 끝까지 진행한다.

## 무엇을 하나

목적 입력 → ① 목적 파악 → ② 팀 설계 → ③ 팀 구조 제시 → ④ 실행 → ⑤ 검토(9.5 게이트) → 최종 결과.

- **부품(Agent)** 50개 = 단일 역할 시스템 프롬프트. 전부 9.5+ 합격선으로 로스팅 검증.
- **레시피(Harness)** 12개 = 부품을 handoff로 엮은 검증된 팀(리서치 보고서·시장 분석·재무 리뷰·발표자료·전략·회의 정리 등).
- **라우터** = 목적 → 레시피 매칭 또는 부품 새 조합. 이게 핵심 IP다.

## 설치

```bash
# 프로젝트의 .claude/skills/ 아래로 복사
cp -r roasting <your-project>/.claude/skills/roasting
```

Claude Code를 재시작하면 스킬이 로드된다.

## 사용법

```
/roasting 경쟁사 3곳을 분석해서 이사회용 보고서 만들어줘
```

또는 "팀 짜줘", "이거 팀으로 해줘", 혹은 보고서·분석·발표자료·제안서·재무검토·회의정리 같은 결과물을 "만들어 달라"고 하면 발동한다. 어떤 팀원이 필요한지 몰라도 목적만 주면 된다.

## 실행 모드 (티어드)

쓸 수 있는 도구에 따라 위에서부터 고른다.

1. **에이전트 팀** — `TeamCreate`/`SendMessage`/`TaskCreate` 가능 시. 팀원이 공유 작업목록으로 자체 조율.
2. **서브에이전트** — `Agent` 도구만 있으면. 의존 단계는 파이프라인, 독립 단계는 병렬(fan-out). (기본·안정)
3. **순차 역할극** — 에이전트 도구가 없으면 팀장이 직접 역할을 순서대로 수행. (폴백)

핵심은 팀원이 **각자 독립 컨텍스트**라는 점이다. 그래서 (a) 검토자가 진짜 독립이라 9.5 게이트가 자기채점이 아니고, (b) 독립 단계를 병렬로 돌린다.

## 품질 게이트

검토자는 산출물을 만들지 않은 **독립 에이전트**로, 사용자의 원래 목적·자료에 대고 구체적 결함부터 찾는다. 결함이 하나라도 있으면 9.5를 주지 않고, 그 단계로 한 번 되돌려 보강한 뒤 통과시킨다. (실측 테스트에서 게이트가 6.5 → 9.2로 실제 두 번 탈락 후 통과했다 — 형식적 게이트가 아니다.)

## 장착 도구

일부 팀원은 AI ROASTING 자사 도구를 역할별로 쥐고 있다.

| 도구 | 용도 | 받는 팀원 |
|---|---|---|
| [전략 도구 갤러리](https://airoasting-strategy.vercel.app/) | 70개 컨설팅 프레임워크 | 전략 기획·SWOT·비즈니스 케이스·의사결정 |
| [5color](https://5color.vercel.app/) | 5인 페르소나 검토 지침 생성 | 품질 검수·비판적 검토·문서 검토·교정 |
| [슬라이드 라이브러리](https://airoasting-slide.vercel.app/) | 35개 HTML 슬라이드 템플릿 | 프레젠테이션 기획·제안서 |
| [AI ROASTING 블로그](https://airoasting-blog.vercel.app/) | 글로벌 리서치 인사이트 | 리서치·트렌드·마켓 |
| [스킬 라이브러리](https://airoasting-skill.vercel.app/) | 엄선된 실무 AI 스킬 | 자동화 설계·SOP |

## 구조

```
roasting/
├── SKILL.md                       # 트리거 · 설계 알고리즘 · 실행 프로토콜 · 9.5 게이트
├── README.md                      # 이 문서
├── LICENSE                        # Apache License 2.0
└── references/
    ├── catalog.md                 # 50명 부품 표(선발용)
    ├── harnesses.md               # 12 레시피 + 토글 + 매칭 키워드
    ├── agent-prompts.md           # 50명 전체 시스템 프롬프트(실행용, id로 선택)
    └── execution-modes.md         # 실행 모드 3종 · 병렬/순차 · 에이전트·검토자 템플릿
```

## 영감

도메인별 에이전트 팀을 구성한다는 발상은 [`revfactory/harness`](https://github.com/revfactory/harness)(에이전트 팀·스킬을 생성하는 메타-스킬)에서 영감을 얻었다. 다만 이 스킬의 50개 역할 프롬프트·12 레시피·실행/검토 로직은 AI ROASTING이 새로 작성하고 로스팅으로 검증한 독립 산출물이다.

## 라이선스

Copyright 2026 AI ROASTING (Jayden Kang). [Apache License 2.0](./LICENSE) 하에 배포된다.
