# KaziLink — Vercel + Daraja ready

Vercel hosts the Vite web app. Daraja credentials are loaded by FastAPI from `backend/config/daraja.env`.

The callback URL is intentionally a placeholder until Vercel gives the project its real domain. After deployment, set:

`MPESA_CALLBACK_URL=https://YOUR-REAL-VERCEL-DOMAIN/api/v1/payments/mpesa/callback`

Do not commit `backend/config/daraja.env`.
