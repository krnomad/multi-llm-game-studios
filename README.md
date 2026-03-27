# multi-llm-game-studios

멀티 LLM 하네스 환경에서 사용할 수 있도록 Game Studios 템플릿을 재구성한 저장소입니다.
하나의 canonical source를 `common/`에 유지하고, 이를 다음 타깃별 출력으로 projection 합니다.

- OpenCode / Oh My OpenCode
- OpenAI Codex
- OpenClaw (repo/CLI compatibility)

이 저장소의 핵심 목적은 **하네스별로 따로 관리하지 않고**, 공통 계약을 한 곳에서 정의한 뒤 각 런타임에 맞는 형태로 안정적으로 생성하는 것입니다.

## 한눈에 보기

### 지원 수준

| Target | Posture | 의미 |
| --- | --- | --- |
| OpenCode | `highest_fidelity_v0_target` | v0 기준 가장 높은 충실도로 매핑되는 주 타깃 |
| Codex | `supported_with_workarounds` | 사용 가능하지만 일부 기능은 fallback / wrapper가 필요 |
| OpenClaw | `repo_cli_compatibility_only` | 레포 구조와 CLI 중심 호환성 제공 |

### 누가 이 저장소를 쓰면 좋은가

- OpenCode와 Codex 둘 다에서 현재 v0 범위의 canonical workflow surface를 운영하고 싶은 사람
- canonical manifest 기반으로 agents / skills / workflows를 관리하고 싶은 사람
- 특정 하네스에 종속되지 않는 장기 유지 구조를 원하는 사람

## 저장소 구조

```text
common/      canonical manifests, docs, schemas, compatibility contracts
adapters/    target-specific generated projections
tools/       projectors and validation scripts
tests/       schema / manifest / projection / drift / docs validation
fixtures/    expected generated outputs for drift checks
docs/        operator-facing supplemental documentation
```

### Source of truth

항상 다음 원칙을 따릅니다.

1. 사람이 수정하는 주 표면은 `common/` 입니다.
2. `adapters/` 아래 파일은 생성 결과물입니다.
3. 어댑터 출력이 이상하면 `common/` 또는 `tools/projectors/`를 수정한 뒤 다시 생성해야 합니다.

## 빠른 시작

### 1) 레포 준비

```bash
git clone git@github.com:krnomad/multi-llm-game-studios.git
cd multi-llm-game-studios
```

### 2) 전체 projection 생성

```bash
python3 tools/projectors/generate_all.py
```

### 3) 전체 검증

```bash
python3 tools/validate/run_all.py
```

이 명령은 schema, manifests, policies, docs, projector tests, drift tests, OpenCode/Codex/OpenClaw smoke validation까지 한 번에 확인합니다.

## 타깃별 사용 가이드

### OpenCode / Oh My OpenCode

OpenCode는 이 저장소에서 가장 높은 fidelity로 지원되는 기본 타깃입니다.

### 생성 결과 위치

- 프로젝트 루트: `adapters/opencode/project/`
- 핵심 설정: `adapters/opencode/project/opencode.json`
- 지시문: `adapters/opencode/project/AGENTS.md`
- skill 패키지: `adapters/opencode/project/.opencode/skills/`
- command alias: `adapters/opencode/project/.opencode/commands/`
- OpenCode 메타데이터: `adapters/opencode/project/.opencode/oh-my-opencode.jsonc`

### OpenCode 설치 개념

OpenCode에서는 project-local surface가 주 경로입니다. 즉, 생성된 `adapters/opencode/project/` 자체를 OpenCode가 읽는 프로젝트로 사용하면 됩니다.

다만 highest fidelity라고 해서 모든 상호작용이 완전한 native parity를 의미하는 것은 아닙니다. 일부 structured choice / hybrid 흐름은 generated wrapper나 helper alias를 함께 사용합니다.

권장 흐름:

1. `python3 tools/projectors/generate_all.py` 실행
2. `adapters/opencode/project/`를 OpenCode에서 작업 루트로 사용
3. `AGENTS.md`, `.opencode/skills/`, `.opencode/commands/`를 통해 워크플로 진입

### OpenCode에서 제공되는 주요 엔트리포인트

현재 v0 기준 skill entrypoints:

- `start`
- `brainstorm`
- `setup-engine`
- `design-review`

각 엔트리포인트는 다음 경로로 projection 됩니다.

- `.opencode/skills/start/SKILL.md`
- `.opencode/skills/brainstorm/SKILL.md`
- `.opencode/skills/setup-engine/SKILL.md`
- `.opencode/skills/design-review/SKILL.md`

그리고 command alias는 다음에 생성됩니다.

- `.opencode/commands/start.md`
- `.opencode/commands/brainstorm.md`
- `.opencode/commands/setup-engine.md`
- `.opencode/commands/design-review.md`

### OpenCode 사용 예시

#### 예시 1: 프로젝트 시작점 진단

OpenCode에서 생성된 project를 연 뒤, `start` 엔트리포인트를 사용해 현재 상태를 진단합니다.

예상 목적:

- 아이디어 단계인지
- 이미 작업물이 있는지
- 다음 워크플로를 무엇으로 시작할지

예시 요청:

```text
start workflow를 사용해서 현재 프로젝트 상태를 진단하고,
내가 어떤 단계부터 시작해야 할지 옵션으로 정리해줘.
```

#### 예시 2: 엔진 선택 / 셋업

```text
setup-engine 워크플로를 기준으로
2D 액션 로그라이크에 맞는 엔진 후보를 추천하고,
Godot와 Unity의 트레이드오프를 비교해줘.
```

#### 예시 3: 아이디어 확장

```text
brainstorm 엔트리포인트를 사용해서
협동 퍼즐 게임 아이디어를 3개 방향으로 확장해줘.
```

### OpenCode 운영 메모

- approval-before-write 의도가 유지됩니다.
- human decision owner 원칙이 유지됩니다.
- OpenCode는 native mapping 비중이 높아서 Codex보다 자연스러운 v0 운영이 가능합니다.

### Codex

Codex는 지원되지만, OpenCode와 같은 수준의 native parity를 전제하지 않습니다.
특히 **project-local custom agents는 신뢰 가능한 기본 로딩 표면으로 간주하지 않기 때문에**, 이 저장소는 Codex용 global-agent workaround를 공식 경로로 제공합니다.

### 생성 결과 위치

- 프로젝트 루트: `adapters/codex/project/`
- 지시문: `adapters/codex/project/AGENTS.md`
- 설정 파일: `adapters/codex/project/.codex/config.toml`
- project-local agents: `adapters/codex/project/.codex/agents/*.toml`
- projected skills: `adapters/codex/project/.agents/skills/*/SKILL.md`
- global install package: `adapters/codex/install/global-agents/`

### Codex 설치 방법

#### 권장 설치 흐름

```bash
python3 tools/projectors/generate_all.py
python3 tools/projectors/install_codex_global_agents.py --target-dir ~/.codex/agents/
python3 tools/validate/smoke_codex.py
```

이 과정은 다음을 수행합니다.

1. 최신 Codex projection 생성
2. global fallback agent TOML 설치
3. Codex projection smoke validation 실행

#### 설치되는 global agents

- `creative-director.toml`
- `producer.toml`
- `qa-lead.toml`
- `technical-director.toml`

### 왜 global install이 필요한가

Codex v0에서는 project-local `.codex/agents/` 로딩이 항상 신뢰 가능하다고 보지 않습니다.
그래서 이 저장소는 다음 fallback을 문서화된 1급 경로로 유지합니다.

- default global install target example: `~/.codex/agents/`
- install package: `adapters/codex/install/global-agents/`
- support posture: `supported_with_workarounds`

`~/.codex/agents/`는 기본 예시 경로이며, 로컬 Codex 설정이 다른 global agent directory를 스캔한다면 그 경로를 사용해도 됩니다.

즉, workaround는 임시 땜질이 아니라 **공식 운영 경로**입니다.

### Codex 사용 예시

Codex에서는 slash command parity를 전제하지 말고, 설치된 agent와 projected skill 문서를 기반으로 작업을 유도하는 방식이 안전합니다.

#### 예시 1: Creative Director 활용

```text
creative-director 역할로,
현재 게임 콘셉트의 핵심 판타지와 톤을 3가지 옵션으로 정리해줘.
각 옵션은 OPTION_A / OPTION_B / OPTION_C 형식으로 보여주고,
마지막에 CHOSEN_OPTION과 RATIONALE 형식으로 추천안도 줘.
```

#### 예시 2: Technical Director 활용

```text
technical-director 관점에서,
이 프로젝트의 엔진 후보와 기술 리스크를 비교해줘.
구조화된 선택지와 추천 근거를 함께 제시해줘.
```

#### 예시 3: QA Lead 활용

```text
qa-lead 역할로,
현재 변경사항에 필요한 테스트 전략과 회귀 테스트 체크리스트를 정리해줘.
```

### Codex 운영 메모

- structured choice는 text-first deterministic option 방식이 기본입니다.
- `OPTION_A`, `OPTION_B` 같은 라벨 기반 캡처를 전제로 합니다.
- `CHOSEN_OPTION`, `RATIONALE` 같은 명시적 응답 필드를 요구하는 흐름이 안전합니다.
- OpenCode-equivalent fidelity를 주장하면 안 됩니다.

## OpenCode와 Codex의 차이

| 항목 | OpenCode | Codex |
| --- | --- | --- |
| 지원 수준 | `highest_fidelity_v0_target` | `supported_with_workarounds` |
| 주 사용 표면 | project-local | project-local + global fallback |
| custom agents | native mapping 중심 | global workaround 권장 |
| structured choice | 비교적 자연스러운 매핑 | text-first deterministic wrapper 중심 |
| 운영 난이도 | 낮음 | 중간 |

## 유지보수자 워크플로

새 canonical 변경을 반영할 때는 항상 아래 순서를 권장합니다.

1. `common/` 수정
2. projection 재생성
3. validation 실행
4. 생성 결과 검토

```bash
python3 tools/projectors/generate_all.py
python3 tools/validate/run_all.py
```

Codex global-agent install까지 같이 검증하려면:

```bash
python3 tools/projectors/install_codex_global_agents.py --target-dir ~/.codex/agents/
python3 tools/validate/smoke_codex.py
```

## 문서 맵

추가 참고 문서:

- `docs/multi-harness-overview.md`
- `docs/support-levels.md`
- `docs/codex-global-install.md`
- `common/docs/workflows/onboarding.md`
- `common/docs/workflows/engine-setup.md`

## 주의 사항

- `adapters/`는 보통 직접 수정하지 않습니다.
- scope는 `common/docs/migration/v0-whitelist.md`에 잠겨 있습니다.
- support posture 문구는 release language로 취급해야 하며, 실제 지원 수준보다 과장하면 안 됩니다.

## Upstream attribution

이 프로젝트는 `Donchitos/Claude-Code-Game-Studios`의 아이디어와 소스 구조를 멀티 하네스 형태로 재구성한 작업입니다.
