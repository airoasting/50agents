# Orchestration Reference (Phase 3 + 5)

SKILL.md Phase 3 (BLACK draft)과 Phase 5 (RGSB 4인 채점) 의 호출 의사코드 상세.

## Phase 3: BLACK Draft (Producer)

메인 Claude가 `Agent` 도구로 BLACK 서브에이전트를 호출:

```
Agent(
    subagent_type="general-purpose",  # roasting-black.md를 system prompt로 주입
    description=f"BLACK draft for {case_id} round {n}",
    prompt=f"""
You are following agents/roasting-black.md. Use the case persona from
references/cases/{case_id}.md (BLACK section) as your character casting.

Inputs:
- xxxxx: {user_xxxxx}
- 케이스 정의 (전문): {case_md_content}
- 슬라이드 템플릿 (PPT만): {slide_meta_json}
- 이전 라운드 RGSB 코멘트 (Round 2+): {prev_critiques_md}
- enrichments (선택, 있으면): {enrichments_dict}

산출물 작성. Markdown 또는 HTML. 자평·메타 코멘트 금지.
출력 위치: _workspace/{session}/round-{n}/black-draft.{ext}
""",
)
```

BLACK은 산출물만 작성하고 종료. 다음 Phase 4(안티패턴 검사)로 진행.

## Phase 5: RGSB Review (4인 채점)

### Primary Path — Agent Teams (TeamCreate 가용 시)

#### Round 1 시작

```
TeamCreate(
    team_name=f"5color-rgsb-{case_id}-{session_id}",
    members=[
        {"name": "RED",    "agent": "roasting-red",    "model": "opus"},
        {"name": "GOLD",   "agent": "roasting-gold",   "model": "opus"},
        {"name": "SILVER", "agent": "roasting-silver", "model": "sonnet"},
        {"name": "BLUE",   "agent": "roasting-blue",   "model": "sonnet"},
    ],
)
SendMessage(to="all", content={
    "black_draft": draft_text,
    "case_definition": case_md,
    "round": n,
})
```

각 페르소나는 독립 컨텍스트에서 `agents/roasting-{name}.md`를 읽고 케이스 정의의 자기 색깔 섹션(예: RED는 RED 평가축)을 캐스팅으로 흡수.

#### 채점

각 페르소나가 BLACK 산출물을 평가하고 `TaskCreate("scoring-table-round-{n}")`에 결과 등록:

```json
{"persona": "RED", "score": 9.4, "reason": "한 줄 의도 명확", "suggestion": "마감일 추가 권장"}
```

#### σ 토론 트리거

메인이 4 점수의 표준편차 σ 계산. 트리거 시:

```python
sorted_by_score = sorted(scores.items(), key=lambda x: x[1].score)
low = sorted_by_score[0]    # (persona, score)
high = sorted_by_score[-1]

# 타이브레이커: 점수 동률 시 GOLD > RED > SILVER > BLUE
TIEBREAK_ORDER = {"GOLD": 0, "RED": 1, "SILVER": 2, "BLUE": 3}

SendMessage(
    to=high.persona,
    from_=low.persona,
    content=f"{low.persona}({low.score}) → {high.persona}({high.score}): "
            f"{low.reason} 약점, 점수 재고려",
)
SendMessage(
    to=low.persona,
    from_=high.persona,
    content=f"{high.persona}({high.score}) → {low.persona}({low.score}): "
            f"{high.reason} 강점 고려",
)
# 양측 새 점수 + 코멘트 TaskUpdate
```

1라운드 토론 후도 σ ≥ 0.5면 "합의 실패" 표시 + 분포 그대로 사용.

#### Round 2+ 진입 (재호출)

`TeamCreate` 안 함 (같은 팀 재사용). 새 BLACK 산출물 broadcast:

```
SendMessage(to="all", content={"black_draft": new_draft, "round": n})
```

채점 + σ 토론 반복.

#### Phase 7 진입 직전

```
TeamDelete(team_name=f"5color-rgsb-{case_id}-{session_id}")
```

### Fallback Path — Sub-Agent (TeamCreate `NotAvailable`/`Forbidden` 시)

병렬 dispatch (4명 동시):

```python
for reviewer in ["RED", "GOLD", "SILVER", "BLUE"]:
    Agent(
        subagent_type="general-purpose",
        description=f"{reviewer} score for {case_id} round {n}",
        prompt=f"""
You are following agents/roasting-{reviewer.lower()}.md.
Use case persona from references/cases/{case_id}.md ({reviewer} section).

Score this BLACK output 1-10:
{black_draft}

Return JSON only:
{{"score": <number>, "reason": "<1줄>", "suggestion": "<1줄>"}}
""",
        run_in_background=True,
    )
```

4 sub-agents 모두 완료 대기 후 `rgsb-scores.json` 저장:

```json
{
  "RED":    {"score": 9.4, "reason": "...", "suggestion": "..."},
  "SILVER": {"score": 8.7, "reason": "...", "suggestion": "..."},
  "BLUE":   {"score": 9.1, "reason": "...", "suggestion": "..."},
  "GOLD":   {"score": 7.8, "reason": "...", "suggestion": "..."}
}
```

σ ≥ 0.5 시 **토론 불가** (sub-agent 모드 한계). 사용자에게 알림: "분포 σ={σ:.2f} — 합의 약함. Agent Teams 모드에서 더 정확합니다." 분포 그대로 출력에 표시.

라운드 카운트 진행 시 매 라운드마다 새로 dispatch (sub-agent 컨텍스트는 라운드 간 유지 안 됨).

## 라이프사이클 비교

| | Agent Teams | Sub-Agent Fallback |
|---|---|---|
| 팀 생성 비용 | TeamCreate 1회 (Round 1) | Round마다 4 dispatch |
| 라운드 간 컨텍스트 | 유지 (Team 재사용) | 매번 새로 |
| σ ≥ 0.5 토론 | 가능 (SendMessage) | 불가 (분포 표시만) |
| 종료 | TeamDelete (Phase 7) | 자동 (sub-agent 종료) |
| Round 1 비용 | ~$0.18 | ~$0.18 |
| Round n+1 비용 | ~$0.18 | ~$0.20 (재 dispatch 비용 약간 ↑) |

## 모델 매핑

| 페르소나 | 모델 | 이유 |
|---|---|---|
| BLACK | Sonnet | 작성 품질 충분, 4라운드 반복 가능성으로 비용 절감 |
| RED (이성) | Opus | 의도·논리·결정 가능성 평가는 추론 비중 높음 |
| GOLD (독자) | Opus | 합격선 시나리오 시뮬레이션은 가장 비판적, 토론 1순위 |
| SILVER (분야 전문가) | Sonnet | 분야별 구조·관행 평가는 패턴 매칭 비중 |
| BLUE (공감) | Sonnet | 톤·분량 평가는 명확한 축이 있어 Sonnet 충분 |

Opus 일시 불가 시 RED/GOLD를 Sonnet으로 자동 다운그레이드 + 사용자 알림.
