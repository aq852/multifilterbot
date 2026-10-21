# Deployment

## VPS with Docker

1. Install Docker and Docker Compose on the VPS.
2. Copy `.env.example` to `.env` and set `BOT_TOKEN`, `ADMIN_IDS`, and a persistent `MONGO_URI`.
3. Run `docker compose up -d --build`.
4. Check `http://<server-ip>:8080/health` and inspect logs with `docker compose logs -f bot`.

For external MongoDB or MongoDB Atlas, use `docker-compose.prod.yml`; it runs only the bot container.

## Koyeb with external MongoDB

Deploy this repository as a Docker-based service using the included `Dockerfile`. Configure port `8080`, health path `/health`, and these environment variables:

- `BOT_TOKEN`
- `ADMIN_IDS`
- `MONGO_URI`
- `MONGO_DB_NAME`
- `HEALTH_HOST=0.0.0.0`
- `HEALTH_PORT=8080`

Do not run the local MongoDB service on Koyeb; use a managed external MongoDB connection. Store secrets in platform environment settings, never in Git.
