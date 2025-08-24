import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = "8262210991:AAErFbn7pDta0x1TjnbekFrYTZ_MVNnVjr8"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

DATA_FILE = "datatest.json"


# Загружаем данные из файла
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# Сохраняем данные в файл
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {"messages": 0}

    save_data(data)
    await message.answer("Привет! Я запомню твои данные 😉")


@dp.message()
async def counter(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {"messages": 0}

    data[user_id]["messages"] += 1
    save_data(data)

    await message.answer(f"Ты написал сообщений: {data[user_id]['messages']}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())