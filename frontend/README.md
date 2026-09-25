# Frontend (Next.js)

Dashboard UI for the AI Interview Orchestrator.

## Quick start (local dev)

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Environment variables

The frontend uses the following environment variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

For local development, `NEXT_PUBLIC_API_URL` should point to the FastAPI backend at `http://localhost:8000`. The WebSocket URL should point to `ws://localhost:8000`.

The default values in `.env.example` are already configured for local development, so no changes are required after copying `.env.example` to `.env.local`.

Make sure the FastAPI backend is running on port `8000` before starting the frontend.

The dashboard will be available at http://localhost:3000.

## Docker

The frontend is wired into the root `docker-compose.yml` as the `frontend`
service. The Next.js app talks to the FastAPI backend via `NEXT_PUBLIC_API_URL`.

## Architecture

```
frontend/
├── src/
│   ├── app/          # Next.js App Router pages
│   │   ├── page.tsx           # Overview dashboard
│   │   ├── sessions/          # Session management
│   │   ├── workers/           # Worker registry
│   │   ├── analytics/         # Risk + retry analytics
│   │   └── settings/          # API token + strategy controls
│   ├── components/   # Reusable UI components
│   ├── lib/          # API client, types, utils
│   └── hooks/        # Data-fetching hooks
├── Dockerfile
└── package.json
```

## Adding a new page

1. Create `src/app/<route>/page.tsx`.
2. Use the `useApi` hook for data fetching.
3. Use components from `src/components/` for consistency.
