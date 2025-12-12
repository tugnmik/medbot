# Railway Deployment Guide - Vietnamese Medical Chatbot

## Prerequisites
1. Railway account (https://railway.app)
2. Git installed
3. GitHub account (optional but recommended)

## Quick Deploy Steps

### Option 1: Deploy via GitHub (Recommended)

1. **Push code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Railway deployment"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Connect to Railway**:
   - Go to https://railway.app/new
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Dockerfile and deploy

### Option 2: Deploy via Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Deploy**:
   ```bash
   railway login
   railway init
   railway up
   ```

## Configuration

Railway will automatically:
- Build using Dockerfile
- Set PORT environment variable
- Provide a public URL

## Environment Variables (auto-configured)

| Variable | Value |
|----------|-------|
| PORT | Auto-set by Railway |
| FLASK_ENV | production |

## API Endpoints (after deployment)

Replace `YOUR_APP_URL` with Railway-provided URL:

- **Chat**: POST `https://YOUR_APP_URL/api/chat`
- **Intents**: GET `https://YOUR_APP_URL/api/intents`
- **Search**: GET `https://YOUR_APP_URL/api/search?q=viêm xoang`
- **Patients**: GET/POST `https://YOUR_APP_URL/api/patients`

## Notes

- First build may take 10-15 minutes (downloading dependencies)
- Cold start may take ~30 seconds
- Free tier: 500 hours/month
