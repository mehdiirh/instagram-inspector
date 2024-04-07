import socks
from telethon.sessions.memory import MemorySession
from telethon.sync import TelegramClient

from core import settings

proxy = (socks.SOCKS5, "localhost", 20170)


def get_bot():
    bot = TelegramClient(
        MemorySession(),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
        proxy=proxy,
    )
    return bot.start(bot_token=settings.TELEGRAM_BOT_TOKEN)


# TestNet
# def get_bot():
#     bot = TelegramClient(None, settings.BOT_API_ID, settings.BOT_API_HASH)
#     bot.session.set_dc(2, "149.154.167.40", 80)
#     return bot.start(bot_token=os.getenv("TEST_BOT_TOKEN"))
