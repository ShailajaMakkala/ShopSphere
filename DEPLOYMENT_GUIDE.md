# 🚀 ShopSphere Deployment Guide

## Overview
| Service | Platform | Folder |
|---|---|---|
| Django Backend | **Render** | `backend` |
| ShopSphere User Frontend | **Vercel** | `user-frontend` |
| Admin Service Frontend | **Vercel** | `admin-service` |

---

## Step 1 — Deploy Backend on Render

### A. Create a New Web Service on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your **GitHub repo** (push this project to GitHub first if you haven't)
3. Fill in the settings:

| Setting | Value |
|---|---|
| **Name** | `shopsphere-backend` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate --no-input` |
| **Start Command** | `gunicorn ShopSphere.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |

### B. Set Environment Variables on Render

In the Render dashboard → your service → **Environment** tab:

| Key | Value |
|---|---|
| `DEBUG` | `False` |
| `SECRET_KEY` | *(generate a random one or let Render auto-generate)* |
| `DATABASE_URL` | *(auto-set when you create a Render Postgres DB below)* |
| `ALLOWED_HOSTS` | `*` *(update with your Render domain after first deploy)* |
| `CORS_ALLOWED_ORIGINS` | *(add Vercel URLs after Step 2 & 3 below)* |
| `EMAIL_HOST_USER` | `nandhuuppalapati@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `jzfc arto roxz wgwj` |

### C. Create a Postgres Database on Render

1. Go to Render → **New** → **PostgreSQL**
2. Name it `shopsphere-db`, plan: **Free**
3. After creation, go to your **Web Service** → Environment → add:
   - `DATABASE_URL` = copy the **Internal Database URL** from Postgres dashboard

### D. Note Your Backend URL
After deploy, your backend URL will be:
```
https://shopsphere-backend.onrender.com
```
*(May be different — copy the exact URL from Render dashboard)*

---

## Step 2 — Deploy ShopSphere Frontend on Vercel

### A. Import Project
1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Import your GitHub repo
3. Set **Root Directory**: `user-frontend`
4. Framework Preset: **Vite** (auto-detected)

### B. Set Environment Variable
In Vercel project settings → **Environment Variables**:

| Key | Value |
|---|---|
| `VITE_API_BASE_URL` | `https://shopsphere-backend.onrender.com` |

> ⚠️ Replace `shopsphere-backend` with your actual Render service name

### C. Deploy
Click **Deploy**. Note your Vercel URL (e.g., `https://shopsphere-xyz.vercel.app`).

---

## Step 3 — Deploy Admin Service Frontend on Vercel

### A. Import Project (second project)
1. Vercel → **Add New Project** → same GitHub repo
2. Set **Root Directory**: `admin-service`
3. Framework Preset: **Vite**

### B. Set Environment Variable

| Key | Value |
|---|---|
| `VITE_API_BASE_URL` | `https://shopsphere-backend.onrender.com` |

### C. Deploy
Note your Admin Vercel URL (e.g., `https://admin-xyz.vercel.app`).

---

## Step 4 — Connect Everything (CORS)

After you have both Vercel URLs, go back to **Render** → your backend service → **Environment Variables** and update:

| Key | Value |
|---|---|
| `CORS_ALLOWED_ORIGINS` | `https://shopsphere-xyz.vercel.app,https://admin-xyz.vercel.app` |

Then **manual deploy** the backend again to pick up the new env var.

---

## Step 5 — Push to GitHub

Before deploying, make sure your code is on GitHub. The key files added/modified:

```
render.yaml                                          ← Render config (root)
backend/.gitignore                      ← Backend gitignore
backend/ShopSphere/settings.py          ← Production settings
backend/ShopSphere/urls.py              ← Fixed static files
user-frontend/vercel.json               ← Vercel config
user-frontend/.env.example              ← Env template
admin-service/vercel.json               ← Vercel config
admin-service/.env.example              ← Env template
```

### Push Commands
```bash
git add .
git commit -m "chore: prepare all services for deployment"
git push origin main
```

---

## Checklist

- [ ] Code pushed to GitHub
- [ ] PostgreSQL database created on Render
- [ ] Backend deployed on Render with all env vars set
- [ ] ShopSphere frontend deployed on Vercel with `VITE_API_BASE_URL`
- [ ] Admin frontend deployed on Vercel with `VITE_API_BASE_URL`
- [ ] `CORS_ALLOWED_ORIGINS` updated on Render with both Vercel URLs
- [ ] Backend redeployed after CORS update

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `CORS blocked` | Add Vercel URL to `CORS_ALLOWED_ORIGINS` env var on Render |
| `500 on first request` | Run `python manage.py migrate` — Render build command does this automatically |
| `Static files 404` | `collectstatic` runs during build — WhiteNoise serves them |
| Frontend shows blank page | Clear browser cache; ensure `VITE_API_BASE_URL` ends without trailing slash |
| Render spins down (free tier) | First request takes ~30s on free plan — expected behavior |
