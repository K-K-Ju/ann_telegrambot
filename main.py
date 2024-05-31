from telebot.async_telebot import AsyncTeleBot
import config
from db_handler import DbHandler
import static
import requests
import json
import asyncio

bot = AsyncTeleBot(config.TELEGRAM_TOKEN)


@bot.message_handler(commands=["start"])
async def receive_start(message):
    db.set_value(message.chat.id, config.States.S_FREE.value)
    await bot.send_message(message.chat.id, static.welcome_msg)


@bot.message_handler(commands=["config"])
async def receive_config(message):
    db.set_value(message.chat.id, config.States.S_ENTER_AMOUNT.value)
    await bot.send_message(message.chat.id, static.enter_number_msg)


def get_imgs_links(query, per_page=1):
    params = {"query": query, "client_id": config.UNSPLASH_TOKEN, "per_page": per_page}
    resp = (requests
            .get(config.UNSPLASH_URL, params=params)
            .json(cls=json.JSONDecoder))

    links = [img['links']['download'] for img in resp['results']]
    return links


async def send_pictures(links, chat):
    await bot.send_message(chat.id, "Here is your photos")
    for l in links:
        await bot.send_message(chat.id, f"{l}")
    db.set_value(chat.id, config.States.S_FREE.value)
    await bot.send_message(chat.id, static.continue_msg, parse_mode="MarkdownV2")


@bot.message_handler(content_types=["text"],
                     func=lambda message: db.get_current_state(message.chat.id) == config.States.S_FREE.value)
async def receive_prompt(message):
    links = get_imgs_links(message.text)
    await send_pictures(links, message.chat)


@bot.message_handler(content_types=["text"],
                     func=lambda message: db.get_current_state(
                         message.chat.id) == config.States.S_ENTER_AMOUNT.value)
async def receive_number_of_photos(message):
    text = message.text
    if not text.isdigit():
        await bot.send_message(message.chat.id, static.incorrect_number_msg)
        return
    number = int(message.text)
    chat_id = message.chat.id
    db.set_column_value(chat_id, "pictures_amount", number)
    db.set_value(chat_id, config.States.S_SEND_PIC.value)
    await bot.send_message(message.chat.id, static.enter_prompt_after_number_msg)


@bot.message_handler(content_types=["text"],
                     func=lambda message: db.get_current_state(
                         message.chat.id) == config.States.S_SEND_PIC.value)
async def send_required_pics(message):
    query = message.text
    amount = int(db.get_column_value(message.chat.id, "pictures_amount"))
    links = get_imgs_links(query, per_page=amount)
    await send_pictures(links, message.chat)


if __name__ == '__main__':
    print("Preparing database...")
    db = DbHandler(config.DB_FILE)
    db.prepare_db()
    print("Starting BOT...")
    asyncio.run(bot.infinity_polling())
    print("Bot started")
