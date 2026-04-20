# Silver Shield AI: Anti-Fraud Protection System

Silver Shield AI is a web project for anti-fraud protection of older adults. It connects elders, family members, community workers, and administrators in one coordinated workflow.

## What This Project Does

- Elder portal: risk alerts, one-click help, family binding, anti-fraud knowledge, accessibility settings
- Family portal: overview, elder list, alert details, notifications, remote reminders
- Community portal: district overview, key elders, work orders, education management, reports
- Admin portal: users, roles, risk rules, content management, system settings

## Demo Flow

`Login -> Risk Recognition -> Risk Alert -> Family Notification -> Community Work Order -> Admin Configuration`

## Project Structure

- Frontend: `apps/web-antd`
- Backend: `apps/backend-fastapi`
- Independent AI API Service: `ai-api-service`
- Requirements: [`需求文档.md`](./需求文档.md)
- TODO: [`TODO.md`](./TODO.md)

## Independent AI Service

This repository now also contains an isolated anti-fraud AI service in [`ai-api-service`](./ai-api-service/).

It is designed as a standalone service that:

- lives at the repository root but does not depend on the monorepo packages
- provides fraud-detection APIs for text, batch input, chat logs, suspicious links, and manual review
- supports remote Qwen-compatible endpoints through local environment configuration
- can fall back to rule-based detection when the remote model is unavailable or returns invalid structured output

Key documents:

- Module README: [`ai-api-service/README.md`](./ai-api-service/README.md)
- Module TODO: [`ai-api-service/TODO.md`](./ai-api-service/TODO.md)

Local configuration is expected in:

```bash
ai-api-service/.env.local
```

Main fields:

```bash
QWEN_BASE_URL=...
QWEN_API_KEY=...
QWEN_MODEL=...
```

## Run Locally

1. Install dependencies

```bash
pnpm install
```



2. Start frontend

```bash
pnpm dev:antd
```

3. Start backend

```bash
cd apps/backend-fastapi
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Build frontend

```bash
pnpm build:antd
```

## Notes

- This repository has been refocused from a scaffold project into the Silver Shield AI competition project.
- The current goal is to make the anti-fraud business flow clear, stable, and demo-ready.

## License

[MIT](./LICENSE)
qwq
