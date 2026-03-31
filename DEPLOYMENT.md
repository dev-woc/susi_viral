# Vercel Deployment

This repo contains the deployable Next.js app under `frontend/`.

## Required Vercel Project Settings

Set the Vercel project `Root Directory` to:

```text
frontend
```

Without that setting, `susi-viral.vercel.app` can return `404 NOT_FOUND` even if the repo itself is valid.

## Required Frontend Environment Variables

Add these in the Vercel project for the frontend deployment:

```text
NEXT_PUBLIC_API_BASE_URL=<your-public-backend-url>
INTERNAL_API_BASE_URL=<your-public-backend-url>
```

Do not use `http://localhost:8000` in Vercel.

## Repo Hints

The repo also includes root-level Vercel-friendly commands:

- `npm run build`
- `npm run start`
- `npm run vercel-build`

And a root [`vercel.json`](/Users/jordanmason/WOC/2026/susi_viral/vercel.json) for the recommended setup where Vercel `Root Directory` is `frontend`.
