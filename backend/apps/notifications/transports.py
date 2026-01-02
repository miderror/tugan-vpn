import asyncio
import logging
from typing import List, Optional, Union

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from asgiref.sync import async_to_sync
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramTransport:
    def __init__(self):
        self.bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.bot.session:
            await self.bot.session.close()

    async def _send_single_async(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None,
    ) -> bool:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
                return True

            except TelegramRetryAfter as e:
                if e.retry_after > 10:
                    logger.warning(
                        f"RateLimit > 10s ({e.retry_after}s) for {chat_id}. Drop."
                    )
                    return False

                if attempt == max_retries - 1:
                    logger.warning(f"RateLimit max retries for {chat_id}. Drop.")
                    return False

                logger.warning(
                    f"RateLimit: {chat_id}, wait={e.retry_after}s, try={attempt + 1}"
                )
                await asyncio.sleep(e.retry_after)

            except TelegramForbiddenError:
                logger.info(f"Blocked: {chat_id}")
                return False

            except Exception as e:
                logger.error(f"SendErr: {chat_id} - {e}")
                return False

        return False

    async def _send_batch_async(self, chat_ids: List[int], text: str) -> int:
        semaphore = asyncio.Semaphore(25)
        success_count = 0

        async def worker(chat_id):
            nonlocal success_count
            async with semaphore:
                if await self._send_single_async(chat_id, text):
                    success_count += 1
                await asyncio.sleep(0.04)

        tasks = [worker(cid) for cid in chat_ids]
        if tasks:
            await asyncio.gather(*tasks)

        return success_count

    def send_single(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None,
    ) -> bool:
        async def _wrapper():
            async with self:
                return await self._send_single_async(chat_id, text, reply_markup)

        return async_to_sync(_wrapper)()

    def send_batch(self, chat_ids: List[int], text: str) -> int:
        async def _wrapper():
            async with self:
                return await self._send_batch_async(chat_ids, text)

        return async_to_sync(_wrapper)()
