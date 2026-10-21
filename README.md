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
- Configurable automatic join-request approval and channel reactions
- Referral links with Premium rewards via `/refer`
- Admin `/ban`, `/unban`, and `/user` controls with global ban enforcement
- Paginated, expiring search sessions with Previous/Next navigation
- `/latest` and `/top` discovery commands
- Admin maintenance mode via `/maintenance on|off`
- `/id` chat and user ID utility
- Inline admin dashboard via `/settings`
- Configurable delivery captions via `/setcaption` and `/clearcaption`
- Media-type search filters such as `/search video:movie`
- File requests via `/request`, `/requests`, and `/closerequest`
- Filename metadata extraction and `/info` for replied media
- Metadata search filters such as `quality:WEB-DL`, `resolution:1080p`, `season:S02`, and `language:Hindi`
- User bookmarks with `/saved` and Save/Remove buttons on search results
- Bookmark cleanup with `/unsave <filename>` and `/clearsaved`
- Per-user recent search history with `/history` and one-tap reruns
- Privacy control `/clearhistory` to remove your personal search history
- Deep-link file sharing with `/share` on indexed messages
- Inline Share buttons on search results
- Inline Info buttons for metadata without downloading
- Categorized `/help` menu with separate user and admin commands
- Personal request tracking with `/myrequests` and filename-based `/cancelrequest`
- In-memory anti-spam rate limiting for users; admins are exempt
- Live `/admin` dashboard with database, catalog, subscription, and request status
- Download counters and `/popular` discovery list
- Admin catalog cleanup with `/deletefile` (reply to a file, pass chat/message IDs, or search by filename)
- Admin title editing with `/renamefile <new title>` on reply, or `/renamefile <old filename> => <new title>`
- Filename fallback for `/share`, with safe handling when multiple files match
- `/info` supports replies and unique filename matches with indexed metadata
- `/random` discovery command for a random indexed file
- Docker and Docker Compose setup

## Local setup

1. Copy `.env.example` to `.env`.
2. Set `BOT_TOKEN` and `ADMIN_IDS`.
3. Start the services with `docker compose up --build`.

The health endpoint is available at `http://localhost:8080/health`.

Only index and distribute media that you are authorized to access and share. Never commit tokens,
session strings, database credentials, or other secrets.
