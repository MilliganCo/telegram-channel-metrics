from telethon import TelegramClient
import asyncio

import os

# Configure your own account privately; no session or API credential is bundled.
api_id = int(os.environ.get("TELEGRAM_API_ID", "0"))
api_hash = os.environ.get("TELEGRAM_API_HASH", "")
channels = [value.strip() for value in os.environ.get("TELEGRAM_CHANNELS", "").split(",") if value.strip()]

# Количество последних постов, для которых считаем средние метрики
POSTS_LIMIT = 50


async def analyze_channel(client, channel_url, posts_limit=POSTS_LIMIT):
    try:
        entity = await client.get_entity(channel_url)
        subscribers = entity.participants_count

        # Получаем последние posts_limit сообщений канала
        messages = await client.get_messages(entity, limit=posts_limit)

        total_views = 0
        total_reactions = 0
        count_messages_with_views = 0
        count_messages_with_reactions = 0

        for msg in messages:
            # Подсчет просмотров
            if msg.views is not None:
                total_views += msg.views
                count_messages_with_views += 1

            # Подсчет реакций
            # msg.reactions может быть None, если реакций нет
            if msg.reactions is not None and msg.reactions.results:
                # Суммируем количество всех реакций в посте
                msg_reaction_count = sum(r.count for r in msg.reactions.results)
                total_reactions += msg_reaction_count
                count_messages_with_reactions += 1

        # Вычисляем средние величины
        avg_views = total_views / count_messages_with_views if count_messages_with_views > 0 else 0
        avg_reactions = total_reactions / count_messages_with_reactions if count_messages_with_reactions > 0 else 0

        return {
            "channel": channel_url,
            "subscribers": subscribers,
            "average_views": avg_views,
            "average_reactions": avg_reactions
        }
    except Exception as e:
        print(f"Не удалось получить данные для канала {channel_url}: {e}")
        return None


async def main():
    if not api_id or not api_hash or not channels:
        raise SystemExit("Set TELEGRAM_API_ID, TELEGRAM_API_HASH and TELEGRAM_CHANNELS before running.")
    async with TelegramClient('session_name', api_id, api_hash) as client:
        for channel_url in channels:
            data = await analyze_channel(client, channel_url, POSTS_LIMIT)
            if data:
                print(f"Канал: {data['channel']}")
                print(f"Подписчиков: {data['subscribers']}")
                print(f"Среднее просмотров (последние {POSTS_LIMIT} постов): {data['average_views']:.2f}")
                print(f"Среднее реакций (последние {POSTS_LIMIT} постов): {data['average_reactions']:.2f}")
                print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())
