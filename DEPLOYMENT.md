# SynapsCode — Live Hosting & Deployment Guide

SynapsCode is configured for multi-tier hosting, ranging from instant live public access to containerized cloud deployment.

---

## 1. Active Live Access Links (Running Right Now)

| Scope | URL | Notes |
| :--- | :--- | :--- |
| **Local Machine** | [http://127.0.0.1:5000](http://127.0.0.1:5000) | Instant local access on this computer |
| **Local Network / Wi-Fi** | `http://10.5.168.42:5000` | Open from your phone, laptop, or any device on your Wi-Fi |
| **Public HTTPS Tunnel** | [https://tame-women-hide.loca.lt](https://tame-women-hide.loca.lt) | Live public tunnel (If prompted for password, enter your external IP: `103.217.237.55`) |

---

## 2. Permanent Free Cloud Hosting (Render / Railway / Hugging Face)

All cloud configuration files have been created in the repository:
- `requirements.txt` (Pinned production dependencies)
- `Procfile` (`web: gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`)
- `render.yaml` (1-Click Blueprint for Render)
- `Dockerfile` (Containerized deployment)

### Option A: Render.com (Recommended Free Tier)
1. Push this directory to your GitHub account (`git push origin main`).
2. Go to [https://dashboard.render.com](https://dashboard.render.com) and click **New +** $\to$ **Web Service**.
3. Select your repository.
4. Render will automatically detect `render.yaml` and configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`
5. Click **Deploy Web Service**. In ~2 minutes, your permanent custom URL `https://synapscode.onrender.com` will be live.

### Option B: Docker Container Deployment
Run locally or on any VPS (AWS EC2, DigitalOcean, GCP):
```bash
docker build -t synapscode .
docker run -d -p 5000:5000 --name synapscode-app synapscode
```
Visit `http://localhost:5000`.

---

## 3. Production Architecture
- **Web Server**: Gunicorn / Waitress WSGI server bound to `0.0.0.0:$PORT`
- **Frontend SPA**: React 19 + TypeScript + Tailwind CSS pre-compiled in `dist/`
- **Static Asset Serving**: High-efficiency caching headers via Flask
- **Engines**: Deterministic AST Normalization + Mersenne-Prime Karp-Rabin Winnowing ($0.93\text{ ms}$ latency)
