# LLM Poker Bot — One-Shot Build Plan (2026-03-02)

## Requirements Summary
- Deliver a playable 6-max Texas Hold'em demo: 1 human vs 4–6 AI bots with distinct personalities and speech-bubble reasoning.
- Backend: FastAPI + Python 3.11, LLM-provider switch (OpenAI ↔ Ollama) via `LLM_PROVIDER` env; fully async game loop and WebSocket streaming.
- Poker engine: deck, positions, betting rounds, pot/side-pot logic, hand evaluation (treys), game orchestrator with blinds/streets.
- LLM layer: prompt builder, response parser with retries/fallbacks, personality prompts, adaptive opponent notes after 5+ hands; exhaustive reasoning logs per decision.
- Frontend: React 18 + Vite + Tailwind; table UI, seats, community cards, action panel, reasoning bubbles, backend toggle, WebSocket hook; uses SVG card assets.
- Containerization: Dockerfiles for frontend/backed and `docker-compose.yml` for one-command launch.
- Tests: engine correctness, LLM parsing/validation, 50–100 hand simulated games with mocked LLM; WebSocket event ordering.

## Acceptance Criteria (testable)
1) `docker compose up --build` starts backend on :8000 and frontend on :3000 without errors.
2) Setting `LLM_PROVIDER=ollama` uses base URL `http://host.docker.internal:11434/v1` and model `OLLAMA_MODEL` fallback `llama3.1:8b`; `LLM_PROVIDER=openai` uses `OPENAI_API_KEY` and model `OPENAI_MODEL` fallback `gpt-4o-mini`.
3) Poker engine deals exactly 52 unique cards per deck shuffle and rotates button positions BTN→SB→BB→UTG→HJ→CO correctly across hands.
4) Side-pot logic pays correct amounts in a 3-player all-in scenario with uneven stacks (covered by unit test in `backend/tests/test_engine.py`).
5) Hand evaluator returns same ranks as treys for sampled hands (covered by unit test).
6) Game orchestrator completes 100 simulated hands with six random-action bots without exceptions (integration test).
7) LLM response parser: invalid/partial JSON triggers up to 3 retries; final fallback action is fold with reasoning "(parse failure — auto fold)"; raise amounts are clamped to [min_raise, stack] and call over-stack becomes all-in.
8) Personality prompt injection verified in tests: each AI uses its assigned system prompt, and adaptive opponent notes appear only after 5+ hands.
9) WebSocket event stream for a hand emits the sequence `new_hand → deal → action ... → your_turn → action ... → showdown/hand_result` in order, verified in `backend/tests/test_game_sim.py` with mocked LLM.
10) Frontend shows: six seats with icons, stacks, action badges; community cards and pot; human action panel (fold/call/raise with slider); reasoning bubbles appear on AI actions; backend toggle reflects server state.
11) Card assets load from `frontend/public/cards/` and display correctly for board + hero hand; AI hole cards stay hidden until showdown events.
12) Reasoning logs persist per hand/player including raw LLM response, parsed action, and game state snapshot; `/api/game/{id}/logs` returns JSON filterable by `hand_number`.
13) `npm test` (if present) or `npm run lint` passes for frontend; `pytest` passes for backend.

## Implementation Steps
1) **Repo bootstrap**: create directories `backend/`, `frontend/`, `backend/engine/`, `backend/llm/`, `backend/adaptive/`, `backend/api/`, `backend/tests/`, `frontend/src/components/`, `frontend/src/hooks/`, `frontend/src/utils/`, `frontend/public/cards/`. Add root `.env.example` for `LLM_PROVIDER`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `OLLAMA_MODEL`.
2) **Docker setup**: write root `docker-compose.yml` with backend/frontend services, port mappings, env passthrough, and host gateway for Ollama. Add `backend/Dockerfile` (uvicorn, prod-ready) and `frontend/Dockerfile` (Vite preview or dev server with env passthrough).
3) **Backend dependencies**: create `backend/requirements.txt` (fastapi, uvicorn[standard], treys, openai>=1.0, pydantic>=2, websockets, pytest, pytest-asyncio, httpx, anyio).
4) **Config module** (`backend/config.py`): implement provider switch per spec with `get_client()` and `get_model()`; include typed helpers and docstrings.
5) **Engine core**:
   - `backend/engine/deck.py`: Deck class using treys `Card`; shuffle and `deal(n)` ensuring no duplicates.
   - `backend/engine/positions.py`: define positions list and `rotate_button(table)`.
   - `backend/engine/table.py`: Player dataclass and Table state (players, community_cards, pot, bets, button, street management).
   - `backend/engine/betting.py`: BettingRound to compute valid actions, enforce min-raise/all-in rules, track current bet, detect round completion.
   - `backend/engine/pot.py`: main + side pots, distribution to winners.
   - `backend/engine/hand_evaluator.py`: wrap treys Evaluator; compare hands util.
   - `backend/engine/game.py`: orchestrate hand flow, blinds posting, dealing streets, invoking betting rounds, showdown handling, wiring to LLM/human actions (async hooks).
6) **Adaptive layer**:
   - `backend/adaptive/tracker.py`: PlayerStats dataclass, update functions, stat properties (vpip, pfr, 3bet, cbet, cbet_fold).
   - `backend/adaptive/notes.py`: generate notes when `hands_played >=5`, including style estimate.
7) **LLM layer**:
   - `backend/llm/personalities.py`: personality map with name/icon/description/system_prompt (rock, shark, maniac, fish).
   - `backend/llm/prompt_builder.py`: build messages with opponent notes and valid actions formatting helpers.
   - `backend/llm/response_parser.py`: async `get_action_from_llm` with up to 3 retries, JSON extraction, validation/clamping, logging.
   - `backend/llm/client.py`: client factory using `config.get_client()` and `config.get_model()`.
8) **API layer**:
   - `backend/api/schemas.py`: Pydantic v2 models for settings, events, human actions.
   - `backend/api/routes.py`: FastAPI app, `/ws/game/{game_id}` WebSocket streaming events, REST endpoints for new game, update settings (provider toggle), and logs.
   - Add `backend/main.py` to create app, include routes, CORS, lifespan for game manager.
9) **Game manager & logging**: Implement a simple `GameManager` (singleton dict) to manage games by id, provide `event_stream` async generator, and persist `reasoning_logs` (e.g., JSONL per game in `backend/logs/`).
10) **Tests** (`backend/tests/`):
    - `test_engine.py`: deck uniqueness, position rotation, side pots, treys parity, 100-hand random sim.
    - `test_llm.py`: parser retries/fallbacks, invalid action correction, personality/notes injection (mock client).
    - `test_game_sim.py`: 50-hand mock-LLM simulation with WebSocket event order assertions.
11) **Frontend setup**: initialize Vite React + Tailwind in `frontend/`; configure Tailwind theme and global styles.
12) **Frontend components**:
    - `src/App.jsx`: layout wiring, load game, handle backend toggle state.
    - `components/Table.jsx`, `CommunityCards.jsx`, `PotDisplay.jsx` for center table.
    - `components/PlayerSeat.jsx`: shows icon/name, stack, bets, highlights active, hides AI hole cards until showdown.
    - `components/ActionPanel.jsx`: fold/call/raise with slider; disabled when not player turn; emits REST/WS actions.
    - `components/ReasoningBubble.jsx`: typing animation; color by personality; shows latest AI reasoning.
    - `components/BackendToggle.jsx`: toggle provider via `/api/game/{id}/settings`, display latency.
    - `hooks/useGameSocket.js`: WebSocket connect/reconnect, event handlers updating client state queues.
    - `utils/cardImages.js`: map ranks/suits to SVG paths in `public/cards/`.
13) **Assets**: import open-source SVG deck into `frontend/public/cards/` plus card back; ensure export script or mapping uses filenames.
14) **State management**: simple `useReducer` or Zustand store for game state (players, board, pot, action log, reasoning bubbles), ensuring event ordering and optimistic human actions.
15) **Styling & UX**: Tailwind classes for oval table, seat positions, chip badges, and speech bubbles; ensure responsive layout for desktop and mobile widths.
16) **Logging & error handling**: central logger writing to `backend/logs/reasoning_logs.jsonl`; ensure WebSocket errors are caught and clients get error events; wrap LLM calls in try/except.
17) **Scripts**: add npm scripts (`dev`, `build`, `preview`, `lint`) and backend scripts (`dev` via uvicorn, `test` via pytest). Add `Makefile` (optional) for `make dev`/`make test`.
18) **Documentation**: update `README.md` with setup, env vars, commands, and sample cURL/WebSocket usage; include backend/ frontend run instructions and test commands.

## Risks & Mitigations
- **LLM latency or failures**: Use retries with exponential backoff and fold fallback; allow provider toggle to a local model for offline play.
- **JSON parsing brittleness**: Strict regex/json detection; clamp invalid actions to safe defaults; log raw responses for debugging.
- **Side-pot/math bugs**: Cover with deterministic unit tests and treys cross-checks; add asserts in pot distribution.
- **WebSocket desync**: Enforce sequential event emission in GameManager; client-side queue with last-seen hand/action ids.
- **Asset loading/performance**: Preload card SVGs; lazy-load reasoning bubbles; keep Tailwind build size small via purge config.
- **Container networking (Ollama)**: Use `host.docker.internal` in compose and document prerequisites; add healthcheck for backend service.

## Verification Steps
- Run `python -m pytest backend/tests -q` (from repo root) — all tests pass.
- Start stack with `docker compose up --build`; open http://localhost:3000 and play a hand; verify reasoning bubbles and toggling providers.
- Manually toggle `LLM_PROVIDER` to `ollama` and confirm backend hits Ollama endpoint (observe logs or mock server).
- Trigger mock game sim (`pytest backend/tests/test_game_sim.py -k simulation`) to ensure 50-hand WebSocket flow passes.
- Frontend lint/build: `cd frontend && npm install && npm run build && npm run lint` succeed.
- Verify reasoning logs: GET `/api/game/{id}/logs?hand_number=1` returns entries with raw/parsed actions and game snapshot.
