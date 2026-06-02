<p align="center">
  <img src="assets/logo_en.png" alt="lolzteam-mcp" width="100%"/>
</p>

<p align="center">
  <b>🇬🇧 English</b> · <a href="README.md">🇷🇺 Русский</a>
</p>

# lolzteam-mcp

A single MCP server that exposes the entire Lolzteam public ecosystem to Claude (and any other MCP-capable client):

- **117 Lolzteam Market endpoints** — account search across 25 categories, buying, selling, payouts, invoices, cart, proxies, IMAP, full management of purchased accounts
- **154 Lolzteam Forum endpoints** — threads, posts, comments, direct messages, chatbox, user profiles, likes, reposts, tags, search, notifications

**271 actions** in total through one connection, plus 3 helper tools for navigation.

## Table of contents

- [What the server can do](#what-the-server-can-do)
- [Installation](#installation)
- [Claude Desktop setup](#claude-desktop-setup)
- [Claude Code setup](#claude-code-setup)
- [Cursor setup](#cursor-setup)
- [Other MCP clients](#other-mcp-clients)
- [Environment variables](#environment-variables)
- [Market API catalogue (117 endpoints)](#market-api-catalogue-117-endpoints)
- [Forum API catalogue (154 endpoints)](#forum-api-catalogue-154-endpoints)
- [Helper tools](#helper-tools)
- [Under the hood](#under-the-hood)
- [License](#license)

## What the server can do

A few examples of how this looks in an LLM conversation. Each "server action" line is a single tool call.

```
User:    "Find Steam accounts under 500₽ with CS:GO, return the top 10."
Server:  → market_category_steam(pmax=500, game="cs:go", per_page=10)

User:    "Post a thread in forum 766 titled 'Selling Steam' with the body
          describing the item."
Server:  → forum_threads_create(forum_id=766, thread_title="Selling Steam", post_body="...")

User:    "Reply in this thread that the price is still valid."
Server:  → forum_posts_create(thread_id=..., post_body="Price is still valid, DM me")

User:    "Show my unread DMs and reply to the first one."
Server:  → forum_conversations_list(unread=true)
         → forum_conversations_messages_create(conversation_id=..., message_body="...")

User:    "Create a 250₽ invoice and send the link to the buyer in DMs."
Server:  → market_payments_invoice_create(amount=250, currency="rub", comment="design work")
         → forum_conversations_messages_create(conversation_id=..., message_body="payment: ...")

User:    "Like the 10 most recent posts in my thread and check who wrote them."
Server:  → forum_threads_get(thread_id=...)
         → forum_posts_list(thread_id=..., limit=10)
         → forum_posts_like(post_id=...)  × 10
```

## Installation

```bash
git clone https://github.com/skallekss/lolzteam-mcp
cd lolzteam-mcp
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # Linux/macOS
pip install -e .
```

To run:

```bash
python -m lolzteam_mcp
```

The command blocks and listens on stdin/stdout — that's normal, MCP uses stdio transport. The client (Claude Desktop etc.) launches it automatically; manual invocation usually isn't needed.

The token is read from `LOLZTEAM_TOKEN`. Obtain one at <https://zelenka.guru/account/api>. The same Lolzteam token covers both the market and the forum.

## Claude Desktop setup

Configuration file location:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

Content:

```json
{
  "mcpServers": {
    "lolzteam": {
      "command": "python",
      "args": ["-m", "lolzteam_mcp"],
      "env": {
        "LOLZTEAM_TOKEN": "PUT_TOKEN_HERE"
      }
    }
  }
}
```

If multiple Python installations exist on the system, the full path to `python.exe` from the local venv is preferable. After saving, Claude Desktop must be fully restarted (quit from the tray). The MCP indicator should then list `lolzteam`.

## Claude Code setup

Fastest path — one command:

```bash
claude mcp add lolzteam -- python -m lolzteam_mcp
```

With the token included:

```bash
claude mcp add lolzteam --env LOLZTEAM_TOKEN=PUT_TOKEN_HERE -- python -m lolzteam_mcp
```

Alternative — editing `~/.claude/settings.json` (or the project-level `.claude/settings.json`):

```json
{
  "mcpServers": {
    "lolzteam": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "lolzteam_mcp"],
      "env": {
        "LOLZTEAM_TOKEN": "PUT_TOKEN_HERE"
      }
    }
  }
}
```

Verification: `claude mcp list` should show `lolzteam` in the output.

## Cursor setup

Via UI: `File → Preferences → Cursor Settings → MCP → Add New MCP Server`.

Via file — `~/.cursor/mcp.json` (or, for a single project, `.cursor/mcp.json` at the project root):

```json
{
  "mcpServers": {
    "lolzteam": {
      "command": "python",
      "args": ["-m", "lolzteam_mcp"],
      "env": {
        "LOLZTEAM_TOKEN": "PUT_TOKEN_HERE"
      }
    }
  }
}
```

A chat restart is required — Cursor will spawn the server and surface the tools.

## Other MCP clients

Any client supporting stdio MCP servers — Continue, Codex, Cline, Zed, Goose, etc. The template stays the same: `command: python`, `args: ["-m", "lolzteam_mcp"]`, token via env. Ready-made snippets are in [`examples/`](examples).

## Environment variables

| Variable                       | Purpose                                                       | Default                            |
|--------------------------------|---------------------------------------------------------------|------------------------------------|
| `LOLZTEAM_TOKEN`               | Shared Bearer token (used for both market and forum unless overridden) | — |
| `LOLZTEAM_MARKET_TOKEN`        | Dedicated token for Market API                                | falls back to `LOLZTEAM_TOKEN`     |
| `LOLZTEAM_FORUM_TOKEN`         | Dedicated token for Forum API                                 | falls back to `LOLZTEAM_TOKEN`     |
| `LOLZTEAM_MARKET_BASE_URL`     | Market API base URL                                           | `https://prod-api.lzt.market`      |
| `LOLZTEAM_FORUM_BASE_URL`      | Forum API base URL                                            | `https://prod-api.lolz.live`       |
| `LOLZTEAM_ENABLE_MARKET`       | Toggle Market API methods                                     | `true`                             |
| `LOLZTEAM_ENABLE_FORUM`        | Toggle Forum API methods                                      | `true`                             |
| `LOLZTEAM_HTTP_TIMEOUT`        | HTTP request timeout (seconds)                                | `30`                               |
| `LOLZTEAM_LOG_LEVEL`           | Logging level                                                 | `INFO`                             |

A `.env` file in the working directory is picked up automatically.

To use only one API (e.g. forum-only) — set `LOLZTEAM_ENABLE_MARKET=false`.

## Market API catalogue (117 endpoints)

Names follow the MCP format: `market_` prefix + name. For the exact schema of any method — `lolzteam_describe_endpoint(tool="market_...")`.

### Profile (2)

| Tool                        | Method | Path  | Purpose |
|-----------------------------|--------|-------|---------|
| `market_profile_get`        | GET    | `/me` | Current profile: login, ID, balance, settings. |
| `market_profile_edit`       | PUT    | `/me` | Edit market profile settings. |

### Categories (3)

| Tool                          | Method | Path                          | Purpose |
|-------------------------------|--------|-------------------------------|---------|
| `market_category_list`        | GET    | `/category`                   | All market categories with metadata. |
| `market_category_params`      | GET    | `/{categoryName}/params`      | Filter parameters for a category. |
| `market_category_games`       | GET    | `/{categoryName}/games`       | Games inside a category. |

### Account search across 25 categories (25)

Each method takes filters: price, keywords, sorting, country, and dozens of category-specific parameters (Steam — games/hours, Telegram — subscribers, Fortnite — V-Bucks/cosmetics, etc.).

| Tool                                  | Category                                  |
|---------------------------------------|-------------------------------------------|
| `market_category_all`                 | Latest accounts across all categories |
| `market_category_steam`               | Steam |
| `market_category_fortnite`            | Fortnite |
| `market_category_mihoyo`              | miHoYo (Genshin Impact, Honkai, etc.) |
| `market_category_riot`                | Riot (League of Legends, Valorant) |
| `market_category_telegram`            | Telegram |
| `market_category_supercell`           | Supercell (Brawl Stars, Clash, etc.) |
| `market_category_ea`                  | EA (Origin) |
| `market_category_wot`                 | World of Tanks |
| `market_category_wotblitz`            | WoT Blitz |
| `market_category_gifts`               | Gifts (gift cards / codes) |
| `market_category_epicgames`           | Epic Games |
| `market_category_escapefromtarkov`    | Escape from Tarkov |
| `market_category_socialclub`          | Rockstar Social Club |
| `market_category_uplay`               | Uplay (Ubisoft) |
| `market_category_discord`             | Discord |
| `market_category_tiktok`              | TikTok |
| `market_category_instagram`           | Instagram |
| `market_category_battlenet`           | Battle.net |
| `market_category_llm`                 | LLM accounts (ChatGPT, Claude, etc.) |
| `market_category_vpn`                 | VPN services |
| `market_category_roblox`              | Roblox |
| `market_category_warface`             | Warface |
| `market_category_minecraft`           | Minecraft |
| `market_category_hytale`              | Hytale |

### Purchasing (6)

| Tool                                    | Method | Path                              | Purpose |
|-----------------------------------------|--------|-----------------------------------|---------|
| `market_purchasing_fastbuy`             | POST   | `/{item_id}/fast-buy`             | Fast buy from main balance. |
| `market_purchasing_check`               | POST   | `/{item_id}/check-account`        | Pre-purchase account validity check. |
| `market_purchasing_confirm`             | POST   | `/{item_id}/confirm-buy`          | Confirm purchase after hold. |
| `market_purchasing_discountrequest`     | POST   | `/{item_id}/discount`             | Ask the seller for a discount. |
| `market_purchasing_discountreview`      | PUT    | `/{item_id}/discount`             | Approve/decline a discount request. |
| `market_purchasing_discountcancel`      | DELETE | `/{item_id}/discount`             | Cancel a discount request. |

### Cart (3)

| Tool                  | Method  | Path    | Purpose |
|-----------------------|---------|---------|---------|
| `market_cart_get`     | GET     | `/cart` | Cart contents. |
| `market_cart_add`     | POST    | `/cart` | Add an account to the cart. |
| `market_cart_delete`  | DELETE  | `/cart` | Remove an item. |

### Lists and tracking (6)

| Tool                         | Method | Path                              | Purpose |
|------------------------------|--------|-----------------------------------|---------|
| `market_list_user`           | GET    | `/user/items`                     | All accounts listed for sale by the user. |
| `market_list_orders`         | GET    | `/user/orders`                    | All purchased accounts. |
| `market_list_states`         | GET    | `/user/item-states`               | Item statuses. |
| `market_list_download`       | GET    | `/user/{type}/download`           | Download account data for backups. |
| `market_list_favorites`      | GET    | `/fave`                           | Favorites. |
| `market_list_viewed`         | GET    | `/viewed`                         | View history. |

### Publishing (4)

| Tool                                | Method | Path                              | Purpose |
|-------------------------------------|--------|-----------------------------------|---------|
| `market_publishing_fastsell`        | POST   | `/item/fast-sell`                 | Fast-track upload for sale. |
| `market_publishing_add`             | POST   | `/item/add`                       | Full publish with all fields. |
| `market_publishing_check`           | POST   | `/{item_id}/goods/check`          | Validate data before going live. |
| `market_publishing_external`        | POST   | `/{item_id}/external-account`     | Attach an external account. |

### Account management (42)

Basics:

| Tool                                    | Method  | Path                           | Purpose |
|-----------------------------------------|---------|--------------------------------|---------|
| `market_managing_get`                   | GET     | `/{item_id}`                   | Account card. |
| `market_manging_delete`                 | DELETE  | `/{item_id}`                   | Delete account. |
| `market_managing_edit`                  | PUT     | `/{item_id}/edit`              | Edit (title, description, price, tags). |
| `market_managing_bulkget`               | POST    | `/bulk/items`                  | Bulk fetch data. |
| `market_managing_bulkaction`            | POST    | `/items/bulk-action`           | Bulk action across multiple accounts. |
| `market_managing_note`                  | POST    | `/{item_id}/note-save`         | Save a note. |
| `market_managing_image`                 | GET     | `/{item_id}/image`             | Image/preview. |

Pricing and promotion:

| Tool                                    | Method  | Path                           | Purpose |
|-----------------------------------------|---------|--------------------------------|---------|
| `market_managing_aiprice`               | GET     | `/{item_id}/ai-price`          | AI price estimate. |
| `market_managing_autobuyprice`          | GET     | `/{item_id}/auto-buy-price`    | Quick-buy price. |
| `market_managing_bump`                  | POST    | `/{item_id}/bump`              | Bump listing. |
| `market_managing_autobump`              | POST    | `/{item_id}/auto-bump`         | Enable auto-bump. |
| `market_managing_autobumpdisable`       | DELETE  | `/{item_id}/auto-bump`         | Disable auto-bump. |
| `market_managing_open`                  | POST    | `/{item_id}/open`              | Open for sale. |
| `market_managing_close`                 | POST    | `/{item_id}/close`             | Close. |
| `market_managing_stick`                 | POST    | `/{item_id}/stick`             | Pin to the top. |
| `market_managing_unstick`               | DELETE  | `/{item_id}/stick`             | Unpin. |
| `market_managing_favorite`              | POST    | `/{item_id}/star`              | Add to favorites. |
| `market_managing_unfavorite`            | DELETE  | `/{item_id}/star`              | Remove from favorites. |

Tags:

| Tool                                    | Method  | Path                           | Purpose |
|-----------------------------------------|---------|--------------------------------|---------|
| `market_managing_tag`                   | POST    | `/{item_id}/tag`               | Private tag. |
| `market_managing_untag`                 | DELETE  | `/{item_id}/tag`               | Remove. |
| `market_managing_publictag`             | POST    | `/{item_id}/public-tag`        | Public tag. |
| `market_managing_publicuntag`           | DELETE  | `/{item_id}/public-tag`        | Remove. |

Claims and guarantee:

| Tool                                          | Method | Path                                  | Purpose |
|-----------------------------------------------|--------|---------------------------------------|---------|
| `market_profile_claims`                       | GET    | `/claims`                             | Claims list. |
| `market_managing_createclaim`                 | POST   | `/claims`                             | File a claim. |
| `market_managing_refuseguarantee`             | POST   | `/{item_id}/refuse-guarantee`         | Decline the guarantee. |
| `market_managing_checkguarantee`              | POST   | `/{item_id}/check-guarantee`          | Check status. |
| `market_managing_declinevideorecording`       | POST   | `/{item_id}/decline-video-recording`  | Decline a video recording request. |

Credentials:

| Tool                                  | Method | Path                                  | Purpose |
|---------------------------------------|--------|---------------------------------------|---------|
| `market_managing_changepassword`      | POST   | `/{item_id}/change-password`          | Rotate password. |
| `market_managing_tempemailpassword`   | GET    | `/{item_id}/temp-email-password`      | Temporary email password. |
| `market_managing_transfer`            | POST   | `/{item_id}/change-owner`             | Transfer to another owner. |

Email and codes:

| Tool                                | Method | Path                                  | Purpose |
|-------------------------------------|--------|---------------------------------------|---------|
| `market_managing_emailcode`         | GET    | `/{item_id}/email-code`               | Email confirmation code. |
| `market_managing_getletters2`       | GET    | `/letters2`                           | Letters from the inbox. |

Steam-specific:

| Tool                                          | Method  | Path                                  | Purpose |
|-----------------------------------------------|---------|---------------------------------------|---------|
| `market_managing_steaminventoryvalue`         | GET     | `/{item_id}/inventory-value`          | Steam inventory value for this lot. |
| `market_managing_steamvalue`                  | GET     | `/steam-value`                        | Value by SteamID. |
| `market_managing_steampreview`                | GET     | `/{item_id}/steam-preview`            | HTML profile preview. |
| `market_managing_steamupdatevalue`            | POST    | `/{item_id}/update-inventory`         | Re-check inventory value. |
| `market_managing_steam_getmafile`             | GET     | `/{item_id}/mafile`                   | Download mafile (Steam Guard). |
| `market_managing_steam_addmafile`             | POST    | `/{item_id}/mafile`                   | Upload mafile. |
| `market_managing_steam_removemafile`          | DELETE  | `/{item_id}/mafile`                   | Remove mafile. |
| `market_managing_steammafilecode`             | GET     | `/{item_id}/guard-code`               | Steam Guard code. |
| `market_managing_steamsda`                    | POST    | `/{item_id}/confirm-sda`              | Confirm via SDA. |

Telegram-specific:

| Tool                                              | Method | Path                                          | Purpose |
|---------------------------------------------------|--------|-----------------------------------------------|---------|
| `market_managing_telegramcode`                    | GET    | `/{item_id}/telegram-login-code`              | Telegram login code. |
| `market_managing_telegramresetauth`               | POST   | `/{item_id}/telegram-reset-authorizations`    | Reset Telegram authorisations. |

### Custom discounts (4)

| Tool                                | Method  | Path                  | Purpose |
|-------------------------------------|---------|-----------------------|---------|
| `market_customdiscounts_get`        | GET     | `/custom-discounts`   | List discounts. |
| `market_customdiscounts_create`     | POST    | `/custom-discounts`   | Create a personal discount. |
| `market_customdiscounts_edit`       | PUT     | `/custom-discounts`   | Edit. |
| `market_customdiscounts_delete`     | DELETE  | `/custom-discounts`   | Delete. |

### Payments and transfers (12)

| Tool                                | Method  | Path                              | Purpose |
|-------------------------------------|---------|-----------------------------------|---------|
| `market_payments_currency`          | GET     | `/currency`                       | FX rates. |
| `market_payments_balance_list`      | GET     | `/balance/exchange`               | All balances (RUB, USD, etc.). |
| `market_payments_balanceexchange`   | POST    | `/balance/exchange`               | Convert balance between currencies. |
| `market_payments_transfer`          | POST    | `/balance/transfer`               | Send money to another user. |
| `market_payments_fee`               | GET     | `/balance/transfer/fee`           | Transfer fee. |
| `market_payments_cancel`            | POST    | `/balance/transfer/cancel`        | Cancel a sent transfer. |
| `market_payments_history`           | GET     | `/user/payments`                  | Payment history. |
| `market_autopayments_list`          | GET     | `/auto-payments`                  | Auto-payments. |
| `market_autopayments_create`        | POST    | `/auto-payment`                   | Create auto-payment. |
| `market_autopayments_delete`        | DELETE  | `/auto-payment`                   | Delete. |
| `market_payments_payoutservices`    | GET     | `/balance/payout/services`        | Payout providers (SBP, cards). |
| `market_payments_payout`            | POST    | `/balance/payout`                 | Request a payout. |

### Invoices (3)

| Tool                                | Method | Path             | Purpose |
|-------------------------------------|--------|------------------|---------|
| `market_payments_invoice_get`       | GET    | `/invoice`       | Invoice by ID. |
| `market_payments_invoice_create`    | POST   | `/invoice`       | Create a payment link with fixed amount and note. |
| `market_payments_invoice_list`      | GET    | `/invoice/list`  | Invoice list. |

### Proxy (3)

| Tool                     | Method  | Path    | Purpose |
|--------------------------|---------|---------|---------|
| `market_proxy_get`       | GET     | `/proxy`| Proxy list. |
| `market_proxy_add`       | POST    | `/proxy`| Add proxy. |
| `market_proxy_delete`    | DELETE  | `/proxy`| Remove proxy. |

### IMAP (2)

| Tool                    | Method  | Path   | Purpose |
|-------------------------|---------|--------|---------|
| `market_imap_create`    | POST    | `/imap`| Connect IMAP. |
| `market_imap_delete`    | DELETE  | `/imap`| Disconnect. |

### Batch requests (1)

| Tool                  | Method | Path     | Purpose |
|-----------------------|--------|----------|---------|
| `market_batch`        | POST   | `/batch` | Run multiple calls in a single request. |

## Forum API catalogue (154 endpoints)

Prefix — `forum_`. Base URL — `https://prod-api.lolz.live`.

### Authentication (1)

| Tool                  | Method | Path           | Purpose |
|-----------------------|--------|----------------|---------|
| `forum_oauth_token`   | POST   | `/oauth/token` | Get an access token (usually not needed — the token comes from the account panel). |

### Threads (22)

| Tool                              | Method  | Path                                      | Purpose |
|-----------------------------------|---------|-------------------------------------------|---------|
| `forum_threads_list`              | GET     | `/threads`                                | Thread list. |
| `forum_threads_create`            | POST    | `/threads`                                | **Create a thread** (article/discussion). |
| `forum_threads_createcontest`     | POST    | `/contests`                               | Create a contest. |
| `forum_threads_claim`             | POST    | `/claims`                                 | File a claim. |
| `forum_threads_get`               | GET     | `/threads/{thread_id}`                    | Get a thread by ID. |
| `forum_threads_edit`              | PUT     | `/threads/{thread_id}`                    | Edit a thread. |
| `forum_threads_delete`            | DELETE  | `/threads/{thread_id}`                    | Delete. |
| `forum_threads_move`              | POST    | `/threads/{thread_id}/move`               | Move to another forum. |
| `forum_threads_bump`              | POST    | `/threads/{thread_id}/bump`               | Bump. |
| `forum_threads_hide`              | POST    | `/threads/{thread_id}/hide`               | Hide. |
| `forum_threads_star`              | POST    | `/threads/{thread_id}/star`               | Bookmark. |
| `forum_threads_unstar`            | DELETE  | `/threads/{thread_id}/star`               | Unbookmark. |
| `forum_threads_followers`         | GET     | `/threads/{thread_id}/followers`          | Thread followers. |
| `forum_threads_follow`            | POST    | `/threads/{thread_id}/followers`          | Follow. |
| `forum_threads_unfollow`          | DELETE  | `/threads/{thread_id}/followers`          | Unfollow. |
| `forum_threads_followed`          | GET     | `/threads/followed`                       | Threads the user follows. |
| `forum_threads_navigation`        | GET     | `/threads/{thread_id}/navigation`         | Breadcrumbs/navigation. |
| `forum_threads_poll_get`          | GET     | `/threads/{thread_id}/poll`               | Get the poll. |
| `forum_threads_poll_vote`         | POST    | `/threads/{thread_id}/poll/votes`         | Vote. |
| `forum_threads_unread`            | GET     | `/threads/new`                            | Unread threads. |
| `forum_threads_recent`            | GET     | `/threads/recent`                         | Recent threads. |
| `forum_threads_finish`            | POST    | `/contests/{thread_id}/finish`            | Finish a contest. |

### Posts (12)

| Tool                                  | Method  | Path                              | Purpose |
|---------------------------------------|---------|-----------------------------------|---------|
| `forum_posts_list`                    | GET     | `/posts`                          | Post list. |
| `forum_posts_create`                  | POST    | `/posts`                          | **Reply in a thread**. |
| `forum_posts_get`                     | GET     | `/posts/{post_id}`                | Get a post. |
| `forum_posts_edit`                    | PUT     | `/posts/{post_id}`                | Edit. |
| `forum_posts_delete`                  | DELETE  | `/posts/{post_id}`                | Delete. |
| `forum_posts_likes`                   | GET     | `/posts/{post_id}/likes`          | Who liked. |
| `forum_posts_like`                    | POST    | `/posts/{post_id}/likes`          | Like a post. |
| `forum_posts_unlike`                  | DELETE  | `/posts/{post_id}/likes`          | Unlike. |
| `forum_posts_reportreasons`           | GET     | `/posts/{post_id}/report`         | Report reasons. |
| `forum_posts_report`                  | POST    | `/posts/{post_id}/report`         | Report. |
| `forum_posts_comments_reportreasons`  | GET     | `/posts/comments/report`          | Reasons for reporting a comment. |
| `forum_posts_comments_report`         | POST    | `/posts/comments/report`          | Report a comment. |

### Post comments (4)

| Tool                                | Method  | Path              | Purpose |
|-------------------------------------|---------|-------------------|---------|
| `forum_posts_comments_get`          | GET     | `/posts/comments` | List of comments. |
| `forum_posts_comments_create`       | POST    | `/posts/comments` | Create. |
| `forum_posts_comments_edit`         | PUT     | `/posts/comments` | Edit. |
| `forum_posts_comments_delete`       | DELETE  | `/posts/comments` | Delete. |

### Direct messages (24)

| Tool                                              | Method  | Path                                                          | Purpose |
|---------------------------------------------------|---------|---------------------------------------------------------------|---------|
| `forum_conversations_list`                        | GET     | `/conversations`                                              | Conversation list. |
| `forum_conversations_create`                      | POST    | `/conversations`                                              | Create a conversation. |
| `forum_conversations_update`                      | PUT     | `/conversations`                                              | Edit conversation settings. |
| `forum_conversations_delete`                      | DELETE  | `/conversations`                                              | Leave a conversation. |
| `forum_conversations_start`                       | POST    | `/conversations/start`                                        | Start a new conversation. |
| `forum_conversations_save`                        | POST    | `/conversations/save`                                         | Send to Saved Messages. |
| `forum_conversations_get`                         | GET     | `/conversations/{conversation_id}`                            | Get a conversation. |
| `forum_conversations_sharecontent`                | GET     | `/conversations/share-content`                                | Get shareable content. |
| `forum_conversations_messages_list`               | GET     | `/conversations/{conversation_id}/messages`                   | Messages list. |
| `forum_conversations_messages_create`             | POST    | `/conversations/{conversation_id}/messages`                   | **Send a DM**. |
| `forum_conversations_search`                      | POST    | `/conversations/search`                                       | Search messages. |
| `forum_conversations_messages_get`                | GET     | `/conversations/messages/{message_id}`                        | Specific message. |
| `forum_conversations_messages_edit`               | PUT     | `/conversations/{conversation_id}/messages/{message_id}`      | Edit. |
| `forum_conversations_messages_delete`             | DELETE  | `/conversations/{conversation_id}/messages/{message_id}`      | Delete. |
| `forum_conversations_invite`                      | POST    | `/conversations/{conversation_id}/invite`                     | Invite users. |
| `forum_conversations_kick`                        | POST    | `/conversations/{conversation_id}/kick`                       | Kick out. |
| `forum_conversations_read`                        | POST    | `/conversations/{conversation_id}/read`                       | Mark as read. |
| `forum_conversations_readall`                     | POST    | `/conversations/read-all`                                     | All conversations — read. |
| `forum_conversations_messages_stick`              | POST    | `/conversations/{conversation_id}/messages/{message_id}/stick`| Pin message. |
| `forum_conversations_messages_unstick`            | DELETE  | `/conversations/{conversation_id}/messages/{message_id}/stick`| Unpin. |
| `forum_conversations_star`                        | POST    | `/conversations/{conversation_id}/star`                       | Star. |
| `forum_conversations_unstar`                      | DELETE  | `/conversations/{conversation_id}/star`                       | Unstar. |
| `forum_conversations_alerts_enable`               | POST    | `/conversations/{conversation_id}/alerts`                     | Enable alerts. |
| `forum_conversations_alerts_disable`              | DELETE  | `/conversations/{conversation_id}/alerts`                     | Disable alerts. |

### Profile posts (12)

| Tool                                    | Method  | Path                                              | Purpose |
|-----------------------------------------|---------|---------------------------------------------------|---------|
| `forum_profileposts_list`               | GET     | `/users/{user_id}/profile-posts`                  | Profile wall posts. |
| `forum_profileposts_get`                | GET     | `/profile-posts/{profile_post_id}`                | Specific post. |
| `forum_profileposts_edit`               | PUT     | `/profile-posts/{profile_post_id}`                | Edit. |
| `forum_profileposts_delete`             | DELETE  | `/profile-posts/{profile_post_id}`                | Delete. |
| `forum_profileposts_create`             | POST    | `/profile-posts`                                  | **Post on a wall**. |
| `forum_profileposts_stick`              | POST    | `/profile-posts/{profile_post_id}/stick`          | Pin. |
| `forum_profileposts_unstick`            | DELETE  | `/profile-posts/{profile_post_id}/stick`          | Unpin. |
| `forum_profileposts_likes`              | GET     | `/profile-posts/{profile_post_id}/likes`          | Likes. |
| `forum_profileposts_like`               | POST    | `/profile-posts/{profile_post_id}/likes`          | Like. |
| `forum_profileposts_unlike`             | DELETE  | `/profile-posts/{profile_post_id}/likes`          | Unlike. |
| `forum_profileposts_reportreasons`      | GET     | `/profile-posts/{profile_post_id}/report`         | Report reasons. |
| `forum_profileposts_report`             | POST    | `/profile-posts/{profile_post_id}/report`         | Report. |

### Profile post comments (7)

| Tool                                              | Method  | Path                                                          | Purpose |
|---------------------------------------------------|---------|---------------------------------------------------------------|---------|
| `forum_profileposts_comments_list`                | GET     | `/profile-posts/comments`                                     | List. |
| `forum_profileposts_comments_create`              | POST    | `/profile-posts/comments`                                     | Create. |
| `forum_profileposts_comments_edit`                | PUT     | `/profile-posts/comments`                                     | Edit. |
| `forum_profileposts_comments_delete`              | DELETE  | `/profile-posts/comments`                                     | Delete. |
| `forum_profileposts_comments_get`                 | GET     | `/profile-posts/{profile_post_id}/comments/{comment_id}`      | Specific comment. |
| `forum_profileposts_comments_reportreasons`       | GET     | `/profile-posts/comments/report`                              | Report reasons. |
| `forum_profileposts_comments_report`              | POST    | `/profile-posts/comments/report`                              | Report. |

### Forums (9)

| Tool                              | Method  | Path                                  | Purpose |
|-----------------------------------|---------|---------------------------------------|---------|
| `forum_forums_list`               | GET     | `/forums`                             | Forum list. |
| `forum_forums_grouped`            | GET     | `/forums/grouped`                     | Forum tree. |
| `forum_forums_get`                | GET     | `/forums/{forum_id}`                  | Forum by ID. |
| `forum_forums_followers`          | GET     | `/forums/{forum_id}/followers`        | Followers. |
| `forum_forums_follow`             | POST    | `/forums/{forum_id}/followers`        | Follow. |
| `forum_forums_unfollow`           | DELETE  | `/forums/{forum_id}/followers`        | Unfollow. |
| `forum_forums_followed`           | GET     | `/forums/followed`                    | Followed forums. |
| `forum_forums_getfeedoptions`     | GET     | `/forums/feed/options`                | Feed settings. |
| `forum_forums_editfeedoptions`    | PUT     | `/forums/feed/options`                | Edit feed settings. |

### Categories (2)

| Tool                            | Method | Path                              | Purpose |
|---------------------------------|--------|-----------------------------------|---------|
| `forum_categories_list`         | GET    | `/categories`                     | Category list. |
| `forum_categories_get`          | GET    | `/categories/{category_id}`       | Category by ID. |

### Users (27)

| Tool                                  | Method  | Path                                          | Purpose |
|---------------------------------------|---------|-----------------------------------------------|---------|
| `forum_users_list`                    | GET     | `/users`                                      | User list. |
| `forum_users_fields`                  | GET     | `/users/fields`                               | Available profile fields. |
| `forum_users_find`                    | GET     | `/users/find`                                 | Find a user. |
| `forum_users_current`                 | GET     | `/users/me`                                   | Current user. |
| `forum_users_get`                     | GET     | `/users/{user_id}`                            | Another user's profile. |
| `forum_users_edit`                    | PUT     | `/users/{user_id}`                            | Edit profile. |
| `forum_users_claims`                  | GET     | `/users/{user_id}/claims`                     | User claims. |
| `forum_users_avatar_upload`           | POST    | `/users/{user_id}/avatar`                     | Upload avatar. |
| `forum_users_avatar_delete`           | DELETE  | `/users/{user_id}/avatar`                     | Delete avatar. |
| `forum_users_avatar_crop`             | POST    | `/users/{user_id}/avatar/crop`                | Crop avatar. |
| `forum_users_background_upload`       | POST    | `/users/{user_id}/background`                 | Upload profile background. |
| `forum_users_background_delete`       | DELETE  | `/users/{user_id}/background`                 | Delete background. |
| `forum_users_background_crop`         | POST    | `/users/{user_id}/background/crop`            | Crop background. |
| `forum_users_followers`               | GET     | `/users/{user_id}/followers`                  | Followers. |
| `forum_users_follow`                  | POST    | `/users/{user_id}/followers`                  | Follow. |
| `forum_users_unfollow`                | DELETE  | `/users/{user_id}/followers`                  | Unfollow. |
| `forum_users_followings`              | GET     | `/users/{user_id}/followings`                 | Users they follow. |
| `forum_users_likes`                   | GET     | `/users/{user_id}/likes`                      | User likes. |
| `forum_users_ignored`                 | GET     | `/users/ignored`                              | Ignore list. |
| `forum_users_ignore`                  | POST    | `/users/{user_id}/ignore`                     | Ignore. |
| `forum_users_ignoreedit`              | PUT     | `/users/{user_id}/ignore`                     | Edit ignore options. |
| `forum_users_unignore`                | DELETE  | `/users/{user_id}/ignore`                     | Unignore. |
| `forum_users_contents`                | GET     | `/users/{user_id}/timeline`                   | Activity timeline. |
| `forum_users_trophies`                | GET     | `/users/{user_id}/trophies`                   | Trophies. |
| `forum_users_secretanswertypes`       | GET     | `/users/secret-answer/types`                  | Secret answer types. |
| `forum_users_sa_reset`                | POST    | `/account/secret-answer/reset`                | Reset secret answer. |
| `forum_users_sa_cancelreset`          | DELETE  | `/account/secret-answer/reset`                | Cancel reset. |

### Notifications (3)

| Tool                            | Method  | Path                                          | Purpose |
|---------------------------------|---------|-----------------------------------------------|---------|
| `forum_notifications_list`      | GET     | `/notifications`                              | Notification list. |
| `forum_notifications_get`       | GET     | `/notifications/{notification_id}/content`    | Content. |
| `forum_notifications_read`      | POST    | `/notifications/read`                         | Mark as read. |

### Chatbox (12)

| Tool                                  | Method  | Path                                  | Purpose |
|---------------------------------------|---------|---------------------------------------|---------|
| `forum_chatbox_index`                 | GET     | `/chatbox`                            | Chat list. |
| `forum_chatbox_getmessages`           | GET     | `/chatbox/messages`                   | Chat messages. |
| `forum_chatbox_postmessage`           | POST    | `/chatbox/messages`                   | Post a chat message. |
| `forum_chatbox_editmessage`           | PUT     | `/chatbox/messages`                   | Edit. |
| `forum_chatbox_deletemessage`         | DELETE  | `/chatbox/messages`                   | Delete. |
| `forum_chatbox_online`                | GET     | `/chatbox/messages/online`            | Who is online. |
| `forum_chatbox_reportreasons`         | GET     | `/chatbox/messages/report`            | Report reasons. |
| `forum_chatbox_report`                | POST    | `/chatbox/messages/report`            | Report. |
| `forum_chatbox_getleaderboard`        | GET     | `/chatbox/messages/leaderboard`       | Leaderboard. |
| `forum_chatbox_getignore`             | GET     | `/chatbox/ignore`                     | Ignored chat users. |
| `forum_chatbox_postignore`            | POST    | `/chatbox/ignore`                     | Ignore. |
| `forum_chatbox_deleteignore`          | DELETE  | `/chatbox/ignore`                     | Unignore. |

### Search (7)

| Tool                            | Method | Path                                  | Purpose |
|---------------------------------|--------|---------------------------------------|---------|
| `forum_search_all`              | POST   | `/search`                             | Global search. |
| `forum_search_threads`          | POST   | `/search/threads`                     | Threads. |
| `forum_search_posts`            | POST   | `/search/posts`                       | Posts. |
| `forum_search_users`            | POST   | `/search/users`                       | Users. |
| `forum_search_profileposts`     | POST   | `/search/profile-posts`               | Profile posts. |
| `forum_search_tagged`           | POST   | `/search/tagged`                      | By tags. |
| `forum_search_results`          | GET    | `/search/{search_id}/results`         | Results by search ID. |

### Content tagging (4)

| Tool                  | Method | Path              | Purpose |
|-----------------------|--------|-------------------|---------|
| `forum_tags_popular`  | GET    | `/tags`           | Popular tags. |
| `forum_tags_list`     | GET    | `/tags/list`      | All tags. |
| `forum_tags_get`      | GET    | `/tags/{tag_id}`  | Content by tag. |
| `forum_tags_find`     | GET    | `/tags/find`      | Filtered content. |

### Link forums (2)

| Tool                | Method | Path                          | Purpose |
|---------------------|--------|-------------------------------|---------|
| `forum_links_list`  | GET    | `/link-forums`                | List. |
| `forum_links_get`   | GET    | `/link-forums/{link_id}`      | Specific link forum. |

### Pages (2)

| Tool                | Method | Path              | Purpose |
|---------------------|--------|-------------------|---------|
| `forum_pages_list`  | GET    | `/pages`          | Pages list. |
| `forum_pages_get`   | GET    | `/pages/{page_id}`| Page by ID. |

### Forms (2)

| Tool                  | Method | Path          | Purpose |
|-----------------------|--------|---------------|---------|
| `forum_forms_list`    | GET    | `/forms`      | Form list. |
| `forum_forms_create`  | POST   | `/forms/save` | Create a form. |

### Assets (1)

| Tool                  | Method | Path   | Purpose |
|-----------------------|--------|--------|---------|
| `forum_assets_css`    | GET    | `/css` | Get forum CSS. |

### Batch requests (1)

| Tool                  | Method | Path     | Purpose |
|-----------------------|--------|----------|---------|
| `forum_batch_execute` | POST   | `/batch` | Run multiple calls in a single request. |

## Helper tools

In addition to the 271 endpoints, three helper tools ship with the server — so an LLM doesn't have to swallow the entire catalogue at once.

| Tool                              | Purpose |
|-----------------------------------|---------|
| `lolzteam_list_endpoints`         | Returns available endpoints grouped by API and section. Accepts `api` (`market` / `forum`) and `tag` filters. |
| `lolzteam_describe_endpoint`      | Full parameter schema and description for a single method by its tool name. |
| `lolzteam_set_token`              | Sets the token at runtime. The `api` parameter accepts `market`, `forum`, or empty (both). |

## Under the hood

```
lolzteam_mcp/
  specs/
    market.json     Lolzteam Market API description
    forum.json      Lolzteam Forum API description
  config.py         env-based settings (separate tokens and URLs per API)
  openapi.py        API description parsing and schema building
  client.py         httpx.AsyncClient with Bearer auth, response normalisation
  server.py         MCP server merging both APIs under one connection
  __main__.py       stdio entrypoint
```

All 271 endpoints are generated automatically from the official API descriptions — none are written by hand. An API prefix (`market_` / `forum_`) is added to every tool name to avoid collisions. Parameters are correctly split into path / query / header / body, and the request body type (JSON / form / multipart) is taken from the description.

## License

MIT. Unofficial project, not affiliated with Lolzteam. Official API descriptions authored by [@AS7RIDENIED](https://github.com/AS7RIDENIED/LOLZTEAM).
