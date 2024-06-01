from telebot.async_telebot import AsyncTeleBot
from telebot.async_telebot import types
import config
from db_handler import DbHandler
import static
import requests
import json
import asyncio

# Ініціалізуємо асинхронного бота з використанням токену від BotFather
bot = AsyncTeleBot(config.TELEGRAM_TOKEN)


@bot.message_handler(commands=["start"])
async def receive_start(message):
    # Встановлюємо стан користувача як S_FREE при отриманні команди "start"
    db.set_state(message.chat.id, static.States.S_FREE.value)
    # Відправляємо привітальне повідомлення користувачеві.
    await bot.send_message(message.chat.id, static.welcome_msg, reply_markup=get_keyboard())


@bot.message_handler(commands=["config"])
async def receive_config(message):
    # Встановлюємо стан користувача як S_ENTER_AMOUNT при отриманні команди "config"
    db.set_state(message.chat.id, static.States.S_ENTER_AMOUNT.value)
    # Відправляємо повідомлення з проханням ввести кількість фотографій.
    await bot.send_message(message.chat.id, static.enter_number_msg)


def get_imgs_links(query, per_page=1, color="", orientation=""):
    params = {"query": query, "client_id": config.UNSPLASH_TOKEN,
              "per_page": per_page, "color": color, "orientation": orientation}
    # Отримуємо посилання на зображення за допомогою запиту до API Unsplash
    # та серіалізуємо відповідь у JSON
    resp = (requests
            .get(config.UNSPLASH_URL, params=params)
            .json(cls=json.JSONDecoder))

    # Отримуємо посилання на завантаження зображень з відповіді API
    links = [img['links']['download'] for img in resp['results']]
    return links


def get_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    command_btn = types.InlineKeyboardButton("Configure", callback_data="config")
    keyboard.add(command_btn)
    return keyboard


@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    if call.data == "config":
        await bot.answer_callback_query(call.id)
        await receive_config(call.message)


async def send_pictures(links, chat):
    # Відправляємо користувачеві повідомлення про те, що фотографії готові
    await bot.send_message(chat.id, "Here is your photos")
    for l in links:
        # Відправляємо кожне посилання на зображення окремо
        await bot.send_message(chat.id, f"{l}")
    # Встановлюємо стан користувача як S_FREE після відправки фотографій
    db.set_state(chat.id, static.States.S_FREE.value)
    # Відправляємо користувачеві повідомлення про можливість продовження
    await bot.send_message(chat.id, static.continue_msg, parse_mode="MarkdownV2", reply_markup=get_keyboard())


@bot.message_handler(content_types=["text"],
                     func=lambda message: db.get_current_state(message.chat.id) == static.States.S_FREE.value)
async def receive_prompt(message):
    # Отримуємо посилання на зображення за текстом повідомлення користувача
    links = get_imgs_links(message.text)
    # Відправляємо користувачеві фотографії.
    await send_pictures(links, message.chat)


@bot.message_handler(content_types=["text"],
                     func=lambda message: db.get_current_state(
                         message.chat.id) == static.States.S_ENTER_AMOUNT.value)
async def receive_photos_amount(message):
    text = message.text
    # Перевіряємо, чи введений текст є числом.
    if not text.isdigit():
        # Відправляємо повідомлення про некоректне введення, якщо текст не є числом
        await bot.send_message(message.chat.id, static.incorrect_number_msg)
        return
    number = int(message.text)
    chat_id = message.chat.id
    # Встановлюємо кількість фотографій для користувача
    db.set_column_value(chat_id, "pictures_amount", number)
    # Встановлюємо стан користувача як S_SEND_PIC.
    db.set_state(chat_id, static.States.S_ENTER_COLOR.value)
    # Відправляємо повідомлення з проханням ввести запит на зображення
    await bot.send_message(message.chat.id, static.enter_color_msg)


@bot.message_handler(content_types=["text"],
                     func=lambda message: db.get_current_state(
                         message.chat.id) == static.States.S_ENTER_COLOR.value)
async def receive_photos_color(message):
    text = message.text
    # Перевіряємо, чи введений текст є числом.
    chat_id = message.chat.id
    # Встановлюємо кількість фотографій для користувача
    db.set_column_value(chat_id, "color", text)
    # Встановлюємо стан користувача як S_ENTER_ORIENTATION.
    db.set_state(chat_id, static.States.S_ENTER_ORIENTATION.value)
    # Відправляємо повідомлення з проханням ввести запит на зображення
    await bot.send_message(message.chat.id, static.enter_orientation_msg)


@bot.message_handler(content_types=["text"],
                     func=lambda message: db.get_current_state(
                         message.chat.id) == static.States.S_ENTER_ORIENTATION.value)
async def receive_photos_orientation(message):
    text = message.text
    # Перевіряємо, чи введений текст є числом.
    chat_id = message.chat.id
    # Встановлюємо кількість фотографій для користувача
    db.set_column_value(chat_id, "orientation", text)
    # Встановлюємо стан користувача як S_ENTER_ORIENTATION.
    db.set_state(chat_id, static.States.S_SEND_PIC.value)
    # Відправляємо повідомлення з проханням ввести запит на зображення
    await bot.send_message(message.chat.id, static.enter_prompt_after_number_msg)


@bot.message_handler(content_types=["text"],
                     func=lambda message: db.get_current_state(
                         message.chat.id) == static.States.S_SEND_PIC.value)
async def send_required_pics(message):
    query = message.text
    chat_id = message.chat.id
    # Отримуємо кількість фотографій, яку бажає отримати користувач
    amount = int(db.get_column_value(chat_id, "pictures_amount"))
    color = db.get_column_value(chat_id, "color")
    orientation = db.get_column_value(chat_id, "orientation")
    # Отримуємо посилання на зображення за запитом і кількістю
    links = get_imgs_links(query, per_page=amount, color=color, orientation=orientation)
    # Відправляємо користувачеві фотографії
    await send_pictures(links, message.chat)


if __name__ == '__main__':
    print("Preparing database...")
    # Ініціалізуємо обробник бази даних і налаштовуємо її
    db = DbHandler(config.DB_FILE)
    db.prepare_db()
    print("Starting BOT...")
    # Запускаємо бота асинхронно з нескінченним опитуванням
    asyncio.run(bot.infinity_polling())
    print("Bot started")
