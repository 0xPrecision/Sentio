import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from app.config.settings import settings
from app.infra.db import get_session
from app.bot.middlewares.tenant_resolver import TenantResolver

bot = Bot(token=settings.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher()
dp.message.middleware(TenantResolver(get_session))

@dp.message(F.text == "/start")
async def start(m: Message, tenant_ctx=None):
    await m.answer("Добро пожаловать! Выберите услугу…")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
