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
- Requirements: [`需求文档.md`](./需求文档.md)
- TODO: [`TODO.md`](./TODO.md)

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
