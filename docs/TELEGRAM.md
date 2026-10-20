# Optional Telegram bot operations

The local web app makes no Telegram calls. This is a separate, opt-in adapter. Live use requires a bot account, the owner's permission, credentials, an allowlisted private chat, and review of Telegram's handling of messages. No live polling or sending has been performed.

## Offline first

```sh
python3 telegram_adapter.py --fixture data/telegram-updates.json
```

This reads synthetic update objects and prints proposed replies to standard output. It needs no token and cannot send messages. The fixture includes an ignored group message.

## Configure

1. Register your own bot using Telegram's official BotFather process. Store the token in a secret manager or process environment, not a committed file, command history or screenshot.
2. Decide which private chat IDs may use it. Set `TELEGRAM_ALLOWED_CHAT_IDS` to their comma-separated numeric IDs. Groups and non-allowlisted chats are ignored. Remove any configured webhook before using long polling; webhook and `getUpdates` operation are mutually exclusive.
3. Set `TELEGRAM_BOT_TOKEN` in the process environment. The program does not load a `.env` file.
4. Inform participants that Telegram receives their messages. Ask them to redact identifiers. This adapter does not retain raw messages, but dry-run stdout contains the proposed reply. Keep terminal/log access private and avoid logging stdout into a shared service.
5. Poll one batch in dry-run mode:

```sh
python3 telegram_adapter.py --poll --once
```

Polling is a real external API operation. It prints proposed replies and persists only the next update ID in `work/telegram-offset.json`; it does not send replies. Using a higher offset acknowledges previous updates at Telegram, so dry-run polling consumes updates for this worker. Do not run multiple workers or reuse the same offset file across unrelated bots.

When the owner separately authorizes replies, the complete operational command is:

```sh
python3 telegram_adapter.py --poll --send-replies
```

This enables actual `sendMessage` calls to allowlisted private chats. It is documented for future use and has **not been run**. Omit `--send-replies` to keep dry-run mode. Replies are educational English text; the web UI provides the full bilingual experience. Ctrl+C stops polling.

## Behavior and failure recovery

- Requests use HTTPS, JSON, timeouts and a fixed Telegram API host. Supported methods are limited to `getUpdates` and `sendMessage`; link previews are disabled.
- `/start` describes privacy and limits. Plain-text offers are analysed; non-text messages are ignored. Group messages and unknown chat IDs receive no reply.
- An update is checkpointed only after processing; a failed send stops before advancing its offset. Transient failures exit with a generic message that omits the token. An operator may retry after inspecting configuration/network access.
- Delivery is at least once: if Telegram receives a reply but the client loses its response, retrying may duplicate that reply. There is no exactly-once delivery claim.
- Telegram rate limiting/retry scheduling is not automated. Honour any provider wait instruction, reduce load and restart deliberately. This is a small private pilot adapter, not a high-volume bot service.
- Revoke/rotate the token in BotFather if exposed. The app never prints request URLs containing the token. Restrict access to your environment, terminal and checkpoint files.

## Run before any real pilot

Use a new consented test chat, exercise `/start`, a harmless offer, blocked chat IDs and a network failure, then verify retention and delivery expectations. Complete a fluent Malay review and an institutional review before any campus branding or campaign. Those checks are outstanding; local mocked request contracts do not prove provider acceptance.

API source: [Telegram Bot API](https://core.telegram.org/bots/api), `getUpdates` and `sendMessage`, consulted 19 October 2026. Do not place tokens in documentation or evidence files.
