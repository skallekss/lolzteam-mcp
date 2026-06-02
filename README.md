<p align="center">
  <img src="assets/logo_ru.png" alt="lolzteam-mcp" width="100%"/>
</p>

<p align="center">
  <a href="README.en.md">🇬🇧 English</a> · <b>🇷🇺 Русский</b>
</p>

# lolzteam-mcp

Один MCP-сервер, который даёт Claude (или любому другому MCP-клиенту) доступ ко всей публичной экосистеме Lolzteam:

- **117 методов Lolzteam Market** — поиск аккаунтов по 25 категориям, покупка, продажа, выплаты, инвойсы, корзина, прокси, IMAP, управление купленным аккаунтом
- **154 метода Lolzteam Forum** — темы, посты, комментарии, личные сообщения, чатбокс, профили пользователей, лайки, репосты, теги, поиск, уведомления

Итого **271 действие** через единое подключение, плюс 3 вспомогательных tool'а для навигации.

## Содержание

- [Что можно делать](#что-можно-делать)
- [Установка](#установка)
- [Подключение к Claude Desktop](#подключение-к-claude-desktop)
- [Подключение к Claude Code](#подключение-к-claude-code)
- [Подключение к Cursor](#подключение-к-cursor)
- [Другие MCP-клиенты](#другие-mcp-клиенты)
- [Переменные окружения](#переменные-окружения)
- [Каталог Market API (117 методов)](#каталог-market-api-117-методов)
- [Каталог Forum API (154 метода)](#каталог-forum-api-154-метода)
- [Вспомогательные tool'ы](#вспомогательные-toolы)
- [Что под капотом](#что-под-капотом)
- [Лицензия](#лицензия)

## Что можно делать

Несколько примеров того, как это выглядит в диалоге с LLM. Каждая «реплика» сервера — это один вызов tool'а.

```
Запрос:    «Найди Steam-аккаунты до 500₽ с CS:GO в инвентаре, верни первые 10.»
Действия:  → market_category_steam(pmax=500, game="cs:go", per_page=10)

Запрос:    «Опубликуй на форуме тему в разделе 766 с заголовком "Продаю Steam"
            и текстом с описанием товара.»
Действия:  → forum_threads_create(forum_id=766, thread_title="Продаю Steam", post_body="...")

Запрос:    «Ответь в этой теме что цена ещё актуальна.»
Действия:  → forum_posts_create(thread_id=..., post_body="Цена актуальна, в ЛС")

Запрос:    «Покажи мои непрочитанные ЛС и ответь на первое.»
Действия:  → forum_conversations_list(unread=true)
           → forum_conversations_messages_create(conversation_id=..., message_body="...")

Запрос:    «Создай инвойс на 250₽ и отправь покупателю ссылку в ЛС.»
Действия:  → market_payments_invoice_create(amount=250, currency="rub", comment="за дизайн")
           → forum_conversations_messages_create(conversation_id=..., message_body="оплата: ...")

Запрос:    «Лайкни 10 последних постов в моей теме и проверь, кто их написал.»
Действия:  → forum_threads_get(thread_id=...)
           → forum_posts_list(thread_id=..., limit=10)
           → forum_posts_like(post_id=...)  × 10
```

## Установка

```bash
git clone https://github.com/skallekss/lolzteam-mcp
cd lolzteam-mcp
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # Linux/macOS
pip install -e .
```

Запуск:

```bash
python -m lolzteam_mcp
```

Команда блокируется и слушает stdin/stdout — это нормально, так работает MCP по stdio. Клиент (Claude Desktop и т.д.) запускает её сам, вручную дёргать обычно не нужно.

Токен берётся из переменной окружения `LOLZTEAM_TOKEN`. Получить можно здесь: <https://zelenka.guru/account/api>. У Lolzteam один токен покрывает и маркет, и форум.

## Подключение к Claude Desktop

Файл конфигурации:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

Содержимое:

```json
{
  "mcpServers": {
    "lolzteam": {
      "command": "python",
      "args": ["-m", "lolzteam_mcp"],
      "env": {
        "LOLZTEAM_TOKEN": "СЮДА_ВПИСАТЬ_ТОКЕН"
      }
    }
  }
}
```

Если в системе несколько Python — лучше прописать полный путь до `python.exe` из своего venv. После сохранения нужно полностью перезапустить Claude Desktop (выйти из трея, не просто закрыть окно). В строке ввода появится индикатор подключённых MCP-серверов — `lolzteam` должен быть в списке.

## Подключение к Claude Code

Самый быстрый способ — одна команда:

```bash
claude mcp add lolzteam -- python -m lolzteam_mcp
```

С прокидыванием токена:

```bash
claude mcp add lolzteam --env LOLZTEAM_TOKEN=СЮДА_ВПИСАТЬ_ТОКЕН -- python -m lolzteam_mcp
```

Альтернатива — отредактировать `~/.claude/settings.json` (или проектный `.claude/settings.json`):

```json
{
  "mcpServers": {
    "lolzteam": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "lolzteam_mcp"],
      "env": {
        "LOLZTEAM_TOKEN": "СЮДА_ВПИСАТЬ_ТОКЕН"
      }
    }
  }
}
```

Проверка: `claude mcp list` — в выводе должна быть строка `lolzteam`.

## Подключение к Cursor

В UI: `File → Preferences → Cursor Settings → MCP → Add New MCP Server`.

Через файл — `~/.cursor/mcp.json` (для конкретного проекта — `.cursor/mcp.json` в корне):

```json
{
  "mcpServers": {
    "lolzteam": {
      "command": "python",
      "args": ["-m", "lolzteam_mcp"],
      "env": {
        "LOLZTEAM_TOKEN": "СЮДА_ВПИСАТЬ_ТОКЕН"
      }
    }
  }
}
```

После сохранения нужно перезапустить чат — Cursor сам поднимет сервер и покажет инструменты.

## Другие MCP-клиенты

Любой клиент, поддерживающий stdio MCP-серверы — Continue, Codex, Cline, Zed, Goose и др. Шаблон один и тот же: `command: python`, `args: ["-m", "lolzteam_mcp"]`, токен через env. Готовые конфиги лежат в [`examples/`](examples).

## Переменные окружения

| Переменная                     | Назначение                                            | По умолчанию                       |
|--------------------------------|-------------------------------------------------------|------------------------------------|
| `LOLZTEAM_TOKEN`               | Общий Bearer-токен (используется и для маркета, и для форума, если отдельные не заданы) | — |
| `LOLZTEAM_MARKET_TOKEN`        | Отдельный токен для Market API                        | значение `LOLZTEAM_TOKEN`          |
| `LOLZTEAM_FORUM_TOKEN`         | Отдельный токен для Forum API                         | значение `LOLZTEAM_TOKEN`          |
| `LOLZTEAM_MARKET_BASE_URL`     | URL Market API                                        | `https://prod-api.lzt.market`      |
| `LOLZTEAM_FORUM_BASE_URL`      | URL Forum API                                         | `https://prod-api.lolz.live`       |
| `LOLZTEAM_ENABLE_MARKET`       | Включить методы Market API                            | `true`                             |
| `LOLZTEAM_ENABLE_FORUM`        | Включить методы Forum API                             | `true`                             |
| `LOLZTEAM_HTTP_TIMEOUT`        | Таймаут HTTP-запроса (секунды)                        | `30`                               |
| `LOLZTEAM_LOG_LEVEL`           | Уровень логирования                                   | `INFO`                             |

`.env` подхватывается автоматически из текущего каталога.

Чтобы выключить один из API (например, нужен только форум) — `LOLZTEAM_ENABLE_MARKET=false`.

## Каталог Market API (117 методов)

Имена приведены к формату MCP: префикс `market_` + название. Для точной схемы любого метода — `lolzteam_describe_endpoint(tool="market_...")`.

### Профиль (2)

| Tool                        | Метод | Путь  | Что делает |
|-----------------------------|-------|-------|------------|
| `market_profile_get`        | GET   | `/me` | Получить данные профиля: логин, ID, баланс, настройки. |
| `market_profile_edit`       | PUT   | `/me` | Изменить настройки профиля на маркете. |

### Категории (3)

| Tool                          | Метод | Путь                          | Что делает |
|-------------------------------|-------|-------------------------------|------------|
| `market_category_list`        | GET   | `/category`                   | Список всех категорий с метаданными. |
| `market_category_params`      | GET   | `/{categoryName}/params`      | Параметры фильтрации для категории. |
| `market_category_games`       | GET   | `/{categoryName}/games`       | Игры внутри категории. |

### Поиск аккаунтов в 25 категориях (25)

Каждый метод принимает фильтры: цена, ключевые слова, сортировка, страна и десятки специфичных параметров (для Steam — игры/часы, для Telegram — подписчики, для Fortnite — V-Bucks/скины и т.д.).

| Tool                                  | Категория                                  |
|---------------------------------------|--------------------------------------------|
| `market_category_all`                 | Последние аккаунты во всех категориях |
| `market_category_steam`               | Steam |
| `market_category_fortnite`            | Fortnite |
| `market_category_mihoyo`              | miHoYo (Genshin Impact, Honkai и др.) |
| `market_category_riot`                | Riot (League of Legends, Valorant) |
| `market_category_telegram`            | Telegram |
| `market_category_supercell`           | Supercell (Brawl Stars, Clash и др.) |
| `market_category_ea`                  | EA (Origin) |
| `market_category_wot`                 | World of Tanks |
| `market_category_wotblitz`            | WoT Blitz |
| `market_category_gifts`               | Gifts (подарки и коды) |
| `market_category_epicgames`           | Epic Games |
| `market_category_escapefromtarkov`    | Escape from Tarkov |
| `market_category_socialclub`          | Rockstar Social Club |
| `market_category_uplay`               | Uplay (Ubisoft) |
| `market_category_discord`             | Discord |
| `market_category_tiktok`              | TikTok |
| `market_category_instagram`           | Instagram |
| `market_category_battlenet`           | Battle.net |
| `market_category_llm`                 | LLM-аккаунты (ChatGPT, Claude и др.) |
| `market_category_vpn`                 | VPN-сервисы |
| `market_category_roblox`              | Roblox |
| `market_category_warface`             | Warface |
| `market_category_minecraft`           | Minecraft |
| `market_category_hytale`              | Hytale |

### Покупка (6)

| Tool                                    | Метод  | Путь                              | Что делает |
|-----------------------------------------|--------|-----------------------------------|------------|
| `market_purchasing_fastbuy`             | POST   | `/{item_id}/fast-buy`             | Быстрая покупка с основного баланса. |
| `market_purchasing_check`               | POST   | `/{item_id}/check-account`        | Проверка аккаунта перед покупкой. |
| `market_purchasing_confirm`             | POST   | `/{item_id}/confirm-buy`          | Подтвердить покупку после холда. |
| `market_purchasing_discountrequest`     | POST   | `/{item_id}/discount`             | Запросить скидку. |
| `market_purchasing_discountreview`      | PUT    | `/{item_id}/discount`             | Одобрить/отклонить запрос скидки. |
| `market_purchasing_discountcancel`      | DELETE | `/{item_id}/discount`             | Отменить запрос скидки. |

### Корзина (3)

| Tool                  | Метод  | Путь    | Что делает |
|-----------------------|--------|---------|------------|
| `market_cart_get`     | GET    | `/cart` | Содержимое корзины. |
| `market_cart_add`     | POST   | `/cart` | Положить аккаунт в корзину. |
| `market_cart_delete`  | DELETE | `/cart` | Удалить позицию. |

### Списки и наблюдение (6)

| Tool                         | Метод | Путь                              | Что делает |
|------------------------------|-------|-----------------------------------|------------|
| `market_list_user`           | GET   | `/user/items`                     | Все аккаунты на продаже у пользователя. |
| `market_list_orders`         | GET   | `/user/orders`                    | Все купленные аккаунты. |
| `market_list_states`         | GET   | `/user/item-states`               | Состояния товаров. |
| `market_list_download`       | GET   | `/user/{type}/download`           | Скачать данные аккаунтов для бэкапа. |
| `market_list_favorites`      | GET   | `/fave`                           | Избранное. |
| `market_list_viewed`         | GET   | `/viewed`                         | История просмотров. |

### Публикация (4)

| Tool                                | Метод | Путь                              | Что делает |
|-------------------------------------|-------|-----------------------------------|------------|
| `market_publishing_fastsell`        | POST  | `/item/fast-sell`                 | Быстрая загрузка аккаунта на продажу. |
| `market_publishing_add`             | POST  | `/item/add`                       | Полное добавление с заполнением всех полей. |
| `market_publishing_check`           | POST  | `/{item_id}/goods/check`          | Проверка данных перед публикацией. |
| `market_publishing_external`        | POST  | `/{item_id}/external-account`     | Добавить дополнительный внешний аккаунт. |

### Управление аккаунтами (42)

Базовое:

| Tool                                    | Метод  | Путь                           | Что делает |
|-----------------------------------------|--------|--------------------------------|------------|
| `market_managing_get`                   | GET    | `/{item_id}`                   | Карточка аккаунта. |
| `market_manging_delete`                 | DELETE | `/{item_id}`                   | Удалить аккаунт. |
| `market_managing_edit`                  | PUT    | `/{item_id}/edit`              | Редактировать (название, описание, цена, теги). |
| `market_managing_bulkget`               | POST   | `/bulk/items`                  | Пачкой получить данные. |
| `market_managing_bulkaction`            | POST   | `/items/bulk-action`           | Пачкой выполнить действие. |
| `market_managing_note`                  | POST   | `/{item_id}/note-save`         | Сохранить заметку. |
| `market_managing_image`                 | GET    | `/{item_id}/image`             | Превью. |

Цена и продвижение:

| Tool                                    | Метод  | Путь                           | Что делает |
|-----------------------------------------|--------|--------------------------------|------------|
| `market_managing_aiprice`               | GET    | `/{item_id}/ai-price`          | AI-оценка цены. |
| `market_managing_autobuyprice`          | GET    | `/{item_id}/auto-buy-price`    | Цена быстрой покупки. |
| `market_managing_bump`                  | POST   | `/{item_id}/bump`              | Поднять в выдаче. |
| `market_managing_autobump`              | POST   | `/{item_id}/auto-bump`         | Включить автоподнятие. |
| `market_managing_autobumpdisable`       | DELETE | `/{item_id}/auto-bump`         | Выключить автоподнятие. |
| `market_managing_open`                  | POST   | `/{item_id}/open`              | Открыть продажу. |
| `market_managing_close`                 | POST   | `/{item_id}/close`             | Закрыть продажу. |
| `market_managing_stick`                 | POST   | `/{item_id}/stick`             | Закрепить наверху. |
| `market_managing_unstick`               | DELETE | `/{item_id}/stick`             | Снять закрепление. |
| `market_managing_favorite`              | POST   | `/{item_id}/star`              | В избранное. |
| `market_managing_unfavorite`            | DELETE | `/{item_id}/star`              | Из избранного. |

Теги:

| Tool                                    | Метод  | Путь                           | Что делает |
|-----------------------------------------|--------|--------------------------------|------------|
| `market_managing_tag`                   | POST   | `/{item_id}/tag`               | Приватный тег. |
| `market_managing_untag`                 | DELETE | `/{item_id}/tag`               | Убрать. |
| `market_managing_publictag`             | POST   | `/{item_id}/public-tag`        | Публичный тег. |
| `market_managing_publicuntag`           | DELETE | `/{item_id}/public-tag`        | Убрать. |

Жалобы и гарантия:

| Tool                                          | Метод | Путь                                  | Что делает |
|-----------------------------------------------|-------|---------------------------------------|------------|
| `market_profile_claims`                       | GET   | `/claims`                             | Список жалоб. |
| `market_managing_createclaim`                 | POST  | `/claims`                             | Создать жалобу. |
| `market_managing_refuseguarantee`             | POST  | `/{item_id}/refuse-guarantee`         | Отказаться от гарантии. |
| `market_managing_checkguarantee`              | POST  | `/{item_id}/check-guarantee`          | Проверить статус. |
| `market_managing_declinevideorecording`       | POST  | `/{item_id}/decline-video-recording`  | Отклонить запрос на видеозапись. |

Смена реквизитов:

| Tool                                  | Метод | Путь                                  | Что делает |
|---------------------------------------|-------|---------------------------------------|------------|
| `market_managing_changepassword`      | POST  | `/{item_id}/change-password`          | Сменить пароль. |
| `market_managing_tempemailpassword`   | GET   | `/{item_id}/temp-email-password`      | Пароль временной почты. |
| `market_managing_transfer`            | POST  | `/{item_id}/change-owner`             | Передать другому владельцу. |

Письма и коды:

| Tool                                | Метод | Путь                                  | Что делает |
|-------------------------------------|-------|---------------------------------------|------------|
| `market_managing_emailcode`         | GET   | `/{item_id}/email-code`               | Код подтверждения с почты. |
| `market_managing_getletters2`       | GET   | `/letters2`                           | Письма из ящика. |

Steam-специфика:

| Tool                                          | Метод  | Путь                                  | Что делает |
|-----------------------------------------------|--------|---------------------------------------|------------|
| `market_managing_steaminventoryvalue`         | GET    | `/{item_id}/inventory-value`          | Стоимость Steam-инвентаря лота. |
| `market_managing_steamvalue`                  | GET    | `/steam-value`                        | Оценить по SteamID. |
| `market_managing_steampreview`                | GET    | `/{item_id}/steam-preview`            | HTML-превью профиля. |
| `market_managing_steamupdatevalue`            | POST   | `/{item_id}/update-inventory`         | Перепроверить стоимость. |
| `market_managing_steam_getmafile`             | GET    | `/{item_id}/mafile`                   | Скачать mafile (Steam Guard). |
| `market_managing_steam_addmafile`             | POST   | `/{item_id}/mafile`                   | Загрузить mafile. |
| `market_managing_steam_removemafile`          | DELETE | `/{item_id}/mafile`                   | Удалить mafile. |
| `market_managing_steammafilecode`             | GET    | `/{item_id}/guard-code`               | Код Steam Guard. |
| `market_managing_steamsda`                    | POST   | `/{item_id}/confirm-sda`              | Подтвердить операцию через SDA. |

Telegram-специфика:

| Tool                                              | Метод | Путь                                          | Что делает |
|---------------------------------------------------|-------|-----------------------------------------------|------------|
| `market_managing_telegramcode`                    | GET   | `/{item_id}/telegram-login-code`              | Код входа Telegram. |
| `market_managing_telegramresetauth`               | POST  | `/{item_id}/telegram-reset-authorizations`    | Сбросить авторизации. |

### Персональные скидки (4)

| Tool                                | Метод  | Путь                  | Что делает |
|-------------------------------------|--------|-----------------------|------------|
| `market_customdiscounts_get`        | GET    | `/custom-discounts`   | Список скидок. |
| `market_customdiscounts_create`     | POST   | `/custom-discounts`   | Создать персональную скидку. |
| `market_customdiscounts_edit`       | PUT    | `/custom-discounts`   | Изменить. |
| `market_customdiscounts_delete`     | DELETE | `/custom-discounts`   | Удалить. |

### Платежи и переводы (12)

| Tool                                | Метод  | Путь                              | Что делает |
|-------------------------------------|--------|-----------------------------------|------------|
| `market_payments_currency`          | GET    | `/currency`                       | Курсы валют. |
| `market_payments_balance_list`      | GET    | `/balance/exchange`               | Все балансы (RUB, USD и т.д.). |
| `market_payments_balanceexchange`   | POST   | `/balance/exchange`               | Обменять баланс между валютами. |
| `market_payments_transfer`          | POST   | `/balance/transfer`               | Перевод другому пользователю. |
| `market_payments_fee`               | GET    | `/balance/transfer/fee`           | Комиссия за перевод. |
| `market_payments_cancel`            | POST   | `/balance/transfer/cancel`        | Отменить отправленный перевод. |
| `market_payments_history`           | GET    | `/user/payments`                  | История платежей. |
| `market_autopayments_list`          | GET    | `/auto-payments`                  | Автоплатежи. |
| `market_autopayments_create`        | POST   | `/auto-payment`                   | Создать автоплатёж. |
| `market_autopayments_delete`        | DELETE | `/auto-payment`                   | Удалить. |
| `market_payments_payoutservices`    | GET    | `/balance/payout/services`        | Сервисы вывода (СБП, карты). |
| `market_payments_payout`            | POST   | `/balance/payout`                 | Запросить вывод. |

### Инвойсы (3)

| Tool                                | Метод | Путь            | Что делает |
|-------------------------------------|-------|-----------------|------------|
| `market_payments_invoice_get`       | GET   | `/invoice`      | Инвойс по ID. |
| `market_payments_invoice_create`    | POST  | `/invoice`      | Создать ссылку на оплату с суммой и комментарием. |
| `market_payments_invoice_list`      | GET   | `/invoice/list` | Список инвойсов. |

### Прокси (3)

| Tool                     | Метод  | Путь    | Что делает |
|--------------------------|--------|---------|------------|
| `market_proxy_get`       | GET    | `/proxy`| Список прокси. |
| `market_proxy_add`       | POST   | `/proxy`| Добавить. |
| `market_proxy_delete`    | DELETE | `/proxy`| Удалить. |

### IMAP (2)

| Tool                    | Метод  | Путь   | Что делает |
|-------------------------|--------|--------|------------|
| `market_imap_create`    | POST   | `/imap`| Подключить IMAP. |
| `market_imap_delete`    | DELETE | `/imap`| Отключить. |

### Пакетные запросы (1)

| Tool                  | Метод | Путь    | Что делает |
|-----------------------|-------|---------|------------|
| `market_batch`        | POST  | `/batch`| Несколько вызовов одним запросом. |

## Каталог Forum API (154 метода)

Префикс — `forum_`. Базовый URL — `https://prod-api.lolz.live`.

### Аутентификация (1)

| Tool                  | Метод | Путь            | Что делает |
|-----------------------|-------|-----------------|------------|
| `forum_oauth_token`   | POST  | `/oauth/token`  | Получить access token (обычно не нужен — токен берётся в личном кабинете). |

### Темы (22)

| Tool                              | Метод  | Путь                                      | Что делает |
|-----------------------------------|--------|-------------------------------------------|------------|
| `forum_threads_list`              | GET    | `/threads`                                | Список тем. |
| `forum_threads_create`            | POST   | `/threads`                                | **Создать тему** (статью/обсуждение). |
| `forum_threads_createcontest`     | POST   | `/contests`                               | Создать конкурс. |
| `forum_threads_claim`             | POST   | `/claims`                                 | Создать заявку (жалоба). |
| `forum_threads_get`               | GET    | `/threads/{thread_id}`                    | Получить тему по ID. |
| `forum_threads_edit`              | PUT    | `/threads/{thread_id}`                    | Редактировать тему. |
| `forum_threads_delete`            | DELETE | `/threads/{thread_id}`                    | Удалить. |
| `forum_threads_move`              | POST   | `/threads/{thread_id}/move`               | Переместить в другой раздел. |
| `forum_threads_bump`              | POST   | `/threads/{thread_id}/bump`               | Поднять. |
| `forum_threads_hide`              | POST   | `/threads/{thread_id}/hide`               | Скрыть. |
| `forum_threads_star`              | POST   | `/threads/{thread_id}/star`               | Добавить в закладки. |
| `forum_threads_unstar`            | DELETE | `/threads/{thread_id}/star`               | Убрать из закладок. |
| `forum_threads_followers`         | GET    | `/threads/{thread_id}/followers`          | Подписчики темы. |
| `forum_threads_follow`            | POST   | `/threads/{thread_id}/followers`          | Подписаться. |
| `forum_threads_unfollow`          | DELETE | `/threads/{thread_id}/followers`          | Отписаться. |
| `forum_threads_followed`          | GET    | `/threads/followed`                       | Список тем, на которые подписан. |
| `forum_threads_navigation`        | GET    | `/threads/{thread_id}/navigation`         | Хлебные крошки/навигация. |
| `forum_threads_poll_get`          | GET    | `/threads/{thread_id}/poll`               | Получить опрос в теме. |
| `forum_threads_poll_vote`         | POST   | `/threads/{thread_id}/poll/votes`         | Проголосовать. |
| `forum_threads_unread`            | GET    | `/threads/new`                            | Непрочитанные темы. |
| `forum_threads_recent`            | GET    | `/threads/recent`                         | Недавние темы. |
| `forum_threads_finish`            | POST   | `/contests/{thread_id}/finish`            | Завершить конкурс. |

### Посты в темах (12)

| Tool                                  | Метод  | Путь                              | Что делает |
|---------------------------------------|--------|-----------------------------------|------------|
| `forum_posts_list`                    | GET    | `/posts`                          | Список постов. |
| `forum_posts_create`                  | POST   | `/posts`                          | **Написать пост** (ответ в теме). |
| `forum_posts_get`                     | GET    | `/posts/{post_id}`                | Получить пост. |
| `forum_posts_edit`                    | PUT    | `/posts/{post_id}`                | Редактировать. |
| `forum_posts_delete`                  | DELETE | `/posts/{post_id}`                | Удалить. |
| `forum_posts_likes`                   | GET    | `/posts/{post_id}/likes`          | Кто поставил лайк. |
| `forum_posts_like`                    | POST   | `/posts/{post_id}/likes`          | Поставить лайк. |
| `forum_posts_unlike`                  | DELETE | `/posts/{post_id}/likes`          | Снять лайк. |
| `forum_posts_reportreasons`           | GET    | `/posts/{post_id}/report`         | Причины для жалобы. |
| `forum_posts_report`                  | POST   | `/posts/{post_id}/report`         | Пожаловаться. |
| `forum_posts_comments_reportreasons`  | GET    | `/posts/comments/report`          | Причины для жалобы на комментарий. |
| `forum_posts_comments_report`         | POST   | `/posts/comments/report`          | Пожаловаться на комментарий. |

### Комментарии к постам (4)

| Tool                                | Метод  | Путь              | Что делает |
|-------------------------------------|--------|-------------------|------------|
| `forum_posts_comments_get`          | GET    | `/posts/comments` | Список комментариев. |
| `forum_posts_comments_create`       | POST   | `/posts/comments` | Создать комментарий. |
| `forum_posts_comments_edit`         | PUT    | `/posts/comments` | Изменить. |
| `forum_posts_comments_delete`       | DELETE | `/posts/comments` | Удалить. |

### Личные сообщения (24)

| Tool                                              | Метод  | Путь                                                          | Что делает |
|---------------------------------------------------|--------|---------------------------------------------------------------|------------|
| `forum_conversations_list`                        | GET    | `/conversations`                                              | Список диалогов. |
| `forum_conversations_create`                      | POST   | `/conversations`                                              | Создать диалог. |
| `forum_conversations_update`                      | PUT    | `/conversations`                                              | Изменить настройки диалога. |
| `forum_conversations_delete`                      | DELETE | `/conversations`                                              | Выйти из диалога. |
| `forum_conversations_start`                       | POST   | `/conversations/start`                                        | Начать новый диалог. |
| `forum_conversations_save`                        | POST   | `/conversations/save`                                         | Отправить в «Сохранённые». |
| `forum_conversations_get`                         | GET    | `/conversations/{conversation_id}`                            | Получить диалог. |
| `forum_conversations_sharecontent`                | GET    | `/conversations/share-content`                                | Получить расшариваемый контент. |
| `forum_conversations_messages_list`               | GET    | `/conversations/{conversation_id}/messages`                   | Список сообщений. |
| `forum_conversations_messages_create`             | POST   | `/conversations/{conversation_id}/messages`                   | **Отправить сообщение в ЛС**. |
| `forum_conversations_search`                      | POST   | `/conversations/search`                                       | Поиск по сообщениям. |
| `forum_conversations_messages_get`                | GET    | `/conversations/messages/{message_id}`                        | Конкретное сообщение. |
| `forum_conversations_messages_edit`               | PUT    | `/conversations/{conversation_id}/messages/{message_id}`      | Редактировать. |
| `forum_conversations_messages_delete`             | DELETE | `/conversations/{conversation_id}/messages/{message_id}`      | Удалить. |
| `forum_conversations_invite`                      | POST   | `/conversations/{conversation_id}/invite`                     | Пригласить пользователей. |
| `forum_conversations_kick`                        | POST   | `/conversations/{conversation_id}/kick`                       | Исключить. |
| `forum_conversations_read`                        | POST   | `/conversations/{conversation_id}/read`                       | Отметить как прочитанный. |
| `forum_conversations_readall`                     | POST   | `/conversations/read-all`                                     | Все диалоги — прочитанные. |
| `forum_conversations_messages_stick`              | POST   | `/conversations/{conversation_id}/messages/{message_id}/stick`| Закрепить сообщение. |
| `forum_conversations_messages_unstick`            | DELETE | `/conversations/{conversation_id}/messages/{message_id}/stick`| Открепить. |
| `forum_conversations_star`                        | POST   | `/conversations/{conversation_id}/star`                       | В избранные диалоги. |
| `forum_conversations_unstar`                      | DELETE | `/conversations/{conversation_id}/star`                       | Убрать. |
| `forum_conversations_alerts_enable`               | POST   | `/conversations/{conversation_id}/alerts`                     | Включить уведомления. |
| `forum_conversations_alerts_disable`              | DELETE | `/conversations/{conversation_id}/alerts`                     | Выключить. |

### Записи в профиле (12)

| Tool                                    | Метод  | Путь                                              | Что делает |
|-----------------------------------------|--------|---------------------------------------------------|------------|
| `forum_profileposts_list`               | GET    | `/users/{user_id}/profile-posts`                  | Записи в стене пользователя. |
| `forum_profileposts_get`                | GET    | `/profile-posts/{profile_post_id}`                | Конкретная запись. |
| `forum_profileposts_edit`               | PUT    | `/profile-posts/{profile_post_id}`                | Редактировать. |
| `forum_profileposts_delete`             | DELETE | `/profile-posts/{profile_post_id}`                | Удалить. |
| `forum_profileposts_create`             | POST   | `/profile-posts`                                  | **Написать на стену**. |
| `forum_profileposts_stick`              | POST   | `/profile-posts/{profile_post_id}/stick`          | Закрепить. |
| `forum_profileposts_unstick`            | DELETE | `/profile-posts/{profile_post_id}/stick`          | Открепить. |
| `forum_profileposts_likes`              | GET    | `/profile-posts/{profile_post_id}/likes`          | Лайки. |
| `forum_profileposts_like`               | POST   | `/profile-posts/{profile_post_id}/likes`          | Лайкнуть. |
| `forum_profileposts_unlike`             | DELETE | `/profile-posts/{profile_post_id}/likes`          | Снять лайк. |
| `forum_profileposts_reportreasons`      | GET    | `/profile-posts/{profile_post_id}/report`         | Причины жалоб. |
| `forum_profileposts_report`             | POST   | `/profile-posts/{profile_post_id}/report`         | Пожаловаться. |

### Комментарии к записям в профиле (7)

| Tool                                              | Метод  | Путь                                                          | Что делает |
|---------------------------------------------------|--------|---------------------------------------------------------------|------------|
| `forum_profileposts_comments_list`                | GET    | `/profile-posts/comments`                                     | Список. |
| `forum_profileposts_comments_create`              | POST   | `/profile-posts/comments`                                     | Создать. |
| `forum_profileposts_comments_edit`                | PUT    | `/profile-posts/comments`                                     | Изменить. |
| `forum_profileposts_comments_delete`              | DELETE | `/profile-posts/comments`                                     | Удалить. |
| `forum_profileposts_comments_get`                 | GET    | `/profile-posts/{profile_post_id}/comments/{comment_id}`      | Конкретный. |
| `forum_profileposts_comments_reportreasons`       | GET    | `/profile-posts/comments/report`                              | Причины жалоб. |
| `forum_profileposts_comments_report`              | POST   | `/profile-posts/comments/report`                              | Пожаловаться. |

### Разделы форума (9)

| Tool                              | Метод | Путь                                  | Что делает |
|-----------------------------------|-------|---------------------------------------|------------|
| `forum_forums_list`               | GET   | `/forums`                             | Список разделов. |
| `forum_forums_grouped`            | GET   | `/forums/grouped`                     | Дерево разделов. |
| `forum_forums_get`                | GET   | `/forums/{forum_id}`                  | Раздел по ID. |
| `forum_forums_followers`          | GET   | `/forums/{forum_id}/followers`        | Подписчики. |
| `forum_forums_follow`             | POST  | `/forums/{forum_id}/followers`        | Подписаться. |
| `forum_forums_unfollow`           | DELETE| `/forums/{forum_id}/followers`        | Отписаться. |
| `forum_forums_followed`           | GET   | `/forums/followed`                    | На какие разделы подписан. |
| `forum_forums_getfeedoptions`     | GET   | `/forums/feed/options`                | Настройки ленты. |
| `forum_forums_editfeedoptions`    | PUT   | `/forums/feed/options`                | Изменить настройки ленты. |

### Категории форума (2)

| Tool                            | Метод | Путь                              | Что делает |
|---------------------------------|-------|-----------------------------------|------------|
| `forum_categories_list`         | GET   | `/categories`                     | Список категорий. |
| `forum_categories_get`          | GET   | `/categories/{category_id}`       | Категория по ID. |

### Пользователи (27)

| Tool                                  | Метод  | Путь                                          | Что делает |
|---------------------------------------|--------|-----------------------------------------------|------------|
| `forum_users_list`                    | GET    | `/users`                                      | Список пользователей. |
| `forum_users_fields`                  | GET    | `/users/fields`                               | Доступные поля профиля. |
| `forum_users_find`                    | GET    | `/users/find`                                 | Найти пользователя. |
| `forum_users_current`                 | GET    | `/users/me`                                   | Свой профиль. |
| `forum_users_get`                     | GET    | `/users/{user_id}`                            | Чужой профиль. |
| `forum_users_edit`                    | PUT    | `/users/{user_id}`                            | Изменить профиль. |
| `forum_users_claims`                  | GET    | `/users/{user_id}/claims`                     | Заявки пользователя. |
| `forum_users_avatar_upload`           | POST   | `/users/{user_id}/avatar`                     | Загрузить аватар. |
| `forum_users_avatar_delete`           | DELETE | `/users/{user_id}/avatar`                     | Удалить аватар. |
| `forum_users_avatar_crop`             | POST   | `/users/{user_id}/avatar/crop`                | Обрезать аватар. |
| `forum_users_background_upload`       | POST   | `/users/{user_id}/background`                 | Загрузить фон профиля. |
| `forum_users_background_delete`       | DELETE | `/users/{user_id}/background`                 | Удалить фон. |
| `forum_users_background_crop`         | POST   | `/users/{user_id}/background/crop`            | Обрезать фон. |
| `forum_users_followers`               | GET    | `/users/{user_id}/followers`                  | Подписчики. |
| `forum_users_follow`                  | POST   | `/users/{user_id}/followers`                  | Подписаться. |
| `forum_users_unfollow`                | DELETE | `/users/{user_id}/followers`                  | Отписаться. |
| `forum_users_followings`              | GET    | `/users/{user_id}/followings`                 | На кого подписан. |
| `forum_users_likes`                   | GET    | `/users/{user_id}/likes`                      | Лайки пользователя. |
| `forum_users_ignored`                 | GET    | `/users/ignored`                              | Список игнора. |
| `forum_users_ignore`                  | POST   | `/users/{user_id}/ignore`                     | В игнор. |
| `forum_users_ignoreedit`              | PUT    | `/users/{user_id}/ignore`                     | Настройки игнора. |
| `forum_users_unignore`                | DELETE | `/users/{user_id}/ignore`                     | Из игнора. |
| `forum_users_contents`                | GET    | `/users/{user_id}/timeline`                   | Лента активности. |
| `forum_users_trophies`                | GET    | `/users/{user_id}/trophies`                   | Трофеи/награды. |
| `forum_users_secretanswertypes`       | GET    | `/users/secret-answer/types`                  | Типы секретных вопросов. |
| `forum_users_sa_reset`                | POST   | `/account/secret-answer/reset`                | Сбросить секретный вопрос. |
| `forum_users_sa_cancelreset`          | DELETE | `/account/secret-answer/reset`                | Отменить сброс. |

### Уведомления (3)

| Tool                            | Метод | Путь                                          | Что делает |
|---------------------------------|-------|-----------------------------------------------|------------|
| `forum_notifications_list`      | GET   | `/notifications`                              | Список уведомлений. |
| `forum_notifications_get`       | GET   | `/notifications/{notification_id}/content`    | Содержимое. |
| `forum_notifications_read`      | POST  | `/notifications/read`                         | Пометить прочитанными. |

### Чатбокс (12)

| Tool                                  | Метод  | Путь                                  | Что делает |
|---------------------------------------|--------|---------------------------------------|------------|
| `forum_chatbox_index`                 | GET    | `/chatbox`                            | Список чатов. |
| `forum_chatbox_getmessages`           | GET    | `/chatbox/messages`                   | Сообщения в чате. |
| `forum_chatbox_postmessage`           | POST   | `/chatbox/messages`                   | Написать в чат. |
| `forum_chatbox_editmessage`           | PUT    | `/chatbox/messages`                   | Изменить. |
| `forum_chatbox_deletemessage`         | DELETE | `/chatbox/messages`                   | Удалить. |
| `forum_chatbox_online`                | GET    | `/chatbox/messages/online`            | Кто онлайн. |
| `forum_chatbox_reportreasons`         | GET    | `/chatbox/messages/report`            | Причины жалоб. |
| `forum_chatbox_report`                | POST   | `/chatbox/messages/report`            | Пожаловаться. |
| `forum_chatbox_getleaderboard`        | GET    | `/chatbox/messages/leaderboard`       | Топ участников. |
| `forum_chatbox_getignore`             | GET    | `/chatbox/ignore`                     | Игнорируемые. |
| `forum_chatbox_postignore`            | POST   | `/chatbox/ignore`                     | В игнор. |
| `forum_chatbox_deleteignore`          | DELETE | `/chatbox/ignore`                     | Из игнора. |

### Поиск (7)

| Tool                            | Метод | Путь                                  | Что делает |
|---------------------------------|-------|---------------------------------------|------------|
| `forum_search_all`              | POST  | `/search`                             | Общий поиск. |
| `forum_search_threads`          | POST  | `/search/threads`                     | По темам. |
| `forum_search_posts`            | POST  | `/search/posts`                       | По постам. |
| `forum_search_users`            | POST  | `/search/users`                       | По пользователям. |
| `forum_search_profileposts`     | POST  | `/search/profile-posts`               | По записям в профиле. |
| `forum_search_tagged`           | POST  | `/search/tagged`                      | По тегам. |
| `forum_search_results`          | GET   | `/search/{search_id}/results`         | Результаты по ID поиска. |

### Теги контента (4)

| Tool                  | Метод | Путь              | Что делает |
|-----------------------|-------|-------------------|------------|
| `forum_tags_popular`  | GET   | `/tags`           | Популярные теги. |
| `forum_tags_list`     | GET   | `/tags/list`      | Все теги. |
| `forum_tags_get`      | GET   | `/tags/{tag_id}`  | Контент по тегу. |
| `forum_tags_find`     | GET   | `/tags/find`      | Найти по тегу. |

### Ссылки-разделы (2)

| Tool                | Метод | Путь                          | Что делает |
|---------------------|-------|-------------------------------|------------|
| `forum_links_list`  | GET   | `/link-forums`                | Список. |
| `forum_links_get`   | GET   | `/link-forums/{link_id}`      | Конкретный. |

### Страницы (2)

| Tool                | Метод | Путь              | Что делает |
|---------------------|-------|-------------------|------------|
| `forum_pages_list`  | GET   | `/pages`          | Список страниц. |
| `forum_pages_get`   | GET   | `/pages/{page_id}`| Страница по ID. |

### Формы (2)

| Tool                  | Метод | Путь          | Что делает |
|-----------------------|-------|---------------|------------|
| `forum_forms_list`    | GET   | `/forms`      | Список форм. |
| `forum_forms_create`  | POST  | `/forms/save` | Создать форму. |

### Ассеты (1)

| Tool                  | Метод | Путь   | Что делает |
|-----------------------|-------|--------|------------|
| `forum_assets_css`    | GET   | `/css` | Получить CSS форума. |

### Пакетные запросы (1)

| Tool                  | Метод | Путь    | Что делает |
|-----------------------|-------|---------|------------|
| `forum_batch_execute` | POST  | `/batch`| Несколько вызовов одним запросом. |

## Вспомогательные tool'ы

В дополнение к 271 методу сервер даёт три служебных tool'а — чтобы LLM не получала весь каталог сразу.

| Tool                              | Что делает |
|-----------------------------------|------------|
| `lolzteam_list_endpoints`         | Список доступных методов, сгруппированный по API и разделу. Принимает фильтры `api` (`market` / `forum`) и `tag`. |
| `lolzteam_describe_endpoint`      | Полная схема параметров и описание любого метода по имени tool'а. |
| `lolzteam_set_token`              | Установить токен в рантайме. Параметр `api`: `market`, `forum` или пусто (для обоих). |

## Что под капотом

```
lolzteam_mcp/
  specs/
    market.json     описание Lolzteam Market API
    forum.json      описание Lolzteam Forum API
  config.py         настройки из env (раздельные токены и URL для каждого API)
  openapi.py        разбор описания API и сборка схем параметров
  client.py         httpx.AsyncClient с Bearer auth, нормализация ответов
  server.py         MCP server, объединение операций двух API под одним подключением
  __main__.py       запуск через stdio
```

Все 271 метод строятся автоматически из официальных описаний API — не описаны руками. К имени каждого метода добавляется префикс API (`market_` / `forum_`), чтобы избежать конфликтов. Параметры правильно раскладываются на path / query / header / body, тип тела запроса (JSON / form / multipart) определяется автоматически.

## Лицензия

MIT. Неофициальный проект, к Lolzteam отношения не имеет. Официальные описания API — авторства [@AS7RIDENIED](https://github.com/AS7RIDENIED/LOLZTEAM).
