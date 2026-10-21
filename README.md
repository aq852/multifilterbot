# MultiFilterBot

Modular Telegram media filtering and management bot built with Python, aiogram, and MongoDB.

## Current milestone

- asynchronous aiogram application
- MongoDB connection and indexes
- user, channel, and file repositories
- `/addchannel`, `/removechannel`, and `/channels` admin commands
- automatic indexing of documents, videos, audio, and photos posted to configured channels
- normalized title search through `/search <query>`
- clickable search results with protected file delivery
- force-subscription channel management with `/addfsub`, `/removefsub`, and `/fsub`
- Premium plans, Telegram Stars checkout, and `/myplan`
- Admin redeem-code creation and user Premium code redemption
- Admin `/stats` reporting and paced reply-based `/broadcast`
- Docker and Docker Compose setup

## Local setup

1. Copy `.env.example` to `.env`.
2. Set `BOT_TOKEN` and `ADMIN_IDS`.
3. Start the services with `docker compose up --build`.

The health endpoint is available at `http://localhost:8080/health`.

Only index and distribute media that you are authorized to access and share. Never commit tokens,
session strings, database credentials, or other secrets.
