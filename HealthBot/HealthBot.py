import asyncio
import logging
import json
import sys
import time

from aiogram import Bot, Dispatcher, html, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types.bot_command import BotCommand
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.input_file import URLInputFile

from Config import BOT_TOKEN

NEW_INFO_BOT_COMMAND = BotCommand(command="new_info", description="Ввести дані за сьогодні")
STATISTICS_BOT_COMMAND = BotCommand(command="statistic", description="Показати статистику")
ADVICE_BOT_COMMAND = BotCommand(command="advice", description="Вивести поради для покращення стану")
RESET_BOT_COMMAND = BotCommand(command="reset", description="Скинути прогрес")

NEW_INFO_COMMAND = Command("new_info")
STATISTICS_COMMAND = Command("statistic")
ADVICE_COMMAND = Command("advice")
RESET_COMMAND = Command("reset")
SECRET_COMMAND = Command("secret")

class HealthInfo(StatesGroup):
    hours_sleep = State()
    glass_water = State()
    activity_minutes = State()
    well_being = State()

DATA_FILE = "data.json"
TOKEN = BOT_TOKEN

dp = Dispatcher()
router = Router()

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        pass
except FileNotFoundError:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("{}")


@router.message(CommandStart(), StateFilter("*"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Вітаю в боті для слідкуванням за здоров'ям {html.bold(message.from_user.full_name)}!")



@router.message(NEW_INFO_COMMAND, StateFilter("*"))
async def cmd_new_info(message: Message, state: FSMContext):
    await state.clear()
    data = load_data()
    user_id = str(message.from_user.id)
    time_now = int(time.time())
    try:
        last_time = data[user_id]["last_time"]
        if time_now - last_time < 64800:
            await message.answer("⏰ На жаль час, після введення останніх даних не пройшов! Повертайтеся завтра!", reply_markup=ReplyKeyboardRemove())
            return
    except Exception:
        pass
    await state.set_state(HealthInfo.hours_sleep)
    await message.answer("🛌 Введіть години сну:", reply_markup=ReplyKeyboardRemove())

@router.message(HealthInfo.hours_sleep)
async def info_hours_sleep(message: Message, state: FSMContext):
    try:
        val = int((message.text or "").strip())
        if val <= 0:
            await message.answer("❌ Ви не ввели правильно число.")
            return
        if val > 24:
            await message.answer("❌ Ви не могли спати більше ніж триває день! Введіть реальні години.")
            return
    except (ValueError, TypeError):
        await message.answer("❌ Ви не ввели число. Спробуйте ще раз.")
        return
    await state.update_data(hours_sleep=val)
    await state.set_state(HealthInfo.glass_water)
    await message.answer("💧 Введіть скільки ви випили за сьогодні склянок води:")

@router.message(HealthInfo.glass_water)
async def info_glass_water(message: Message, state: FSMContext):
    try:
        val = int((message.text or "").strip())
        if val <= 0:
            await message.answer("❌ Ви не ввели правильно число.")
            return
        if val > 40:
            await message.answer("❌ Це смертельна доза! Введіть реальну кількість.")
            return
    except (ValueError, TypeError):
        await message.answer("❌ Ви не ввели число. Спробуйте ще раз.")
        return
    await state.update_data(glass_water=val)
    await state.set_state(HealthInfo.activity_minutes)
    await message.answer("🏃 Скільки сьогодні у вас було активності (хвилин):")

@router.message(HealthInfo.activity_minutes)
async def info_activity_minutes(message: Message, state: FSMContext):
    try:
        val = int((message.text or "").strip())
        if val <= 0:
            await message.answer("❌ Ви не ввели правильно число.")
            return
        if val > 420:
            await message.answer("❌ Це занадто багато (небезпечно). Введіть реальний час.")
            return
    except (ValueError, TypeError):
        await message.answer("❌ Ви не ввели число. Спробуйте ще раз.")
        return
    await state.update_data(activity_minutes=val)
    await state.set_state(HealthInfo.well_being)
    await message.answer("🙆 Ваше самопочуття (від 1 до 10):")

@router.message(HealthInfo.well_being)
async def info_well_being(message: Message, state: FSMContext):
    try:
        val = int((message.text or "").strip())
        if not (1 <= val <= 10):
            await message.answer("❌ Число має бути від 1 до 10.")
            return
    except (ValueError, TypeError):
        await message.answer("❌ Введіть число від 1 до 10.")
        return

    await state.update_data(well_being=val)
    data = await state.get_data()
    user_id = str(message.from_user.id)

    hours_sleep = int(data["hours_sleep"])
    glass_water = int(data["glass_water"])
    activity_minutes = int(data["activity_minutes"])
    well_being_val = int(data["well_being"])

    if 8 <= hours_sleep <= 12:
        sleep_score = 1.0
    elif hours_sleep < 8:
        sleep_score = (hours_sleep - 1) / 7
    else:
        sleep_score = (24 - hours_sleep) / 12

    if 8 <= glass_water <= 19:
        water_score = 1.0
    elif glass_water < 8:
        water_score = (glass_water - 1) / 7
    else:
        water_score = (40 - glass_water) / 21

    if 40 <= activity_minutes <= 200:
        activity_score = 1.0
    elif activity_minutes < 40:
        activity_score = (activity_minutes - 1) / 39
    else:
        activity_score = (420 - activity_minutes) / 220

    if 5 <= well_being_val <= 10:
        well_being_score = 1.0
    else:
        well_being_score = (well_being_val - 1) / 4

    HI = int(((sleep_score + water_score + activity_score + well_being_score) / 4) * 10)

    new_data = load_data()

    try:
        new_data[user_id] = {"early_hours_sleep": new_data[user_id].get("hours_sleep"),
                  "early_glass_water": new_data[user_id].get("glass_water"),
                  "early_activity_minutes": new_data[user_id].get("activity_minutes"),
                  "early_well_being_val": new_data[user_id].get("well_being_val"),
                  "hours_sleep": hours_sleep,
                  "glass_water": glass_water,
                  "activity_minutes": activity_minutes,
                  "well_being_val": well_being_val,
                  "last_time": int(time.time()),
                  "HI": new_data[user_id]["HI"]}
        new_data[user_id]["HI"].append(HI)
        save_data(data=new_data)
    except Exception:
        new_data[user_id] = {"early_hours_sleep": None,
                             "early_glass_water": None,
                             "early_activity_minutes": None,
                             "early_well_being_val": None,
                             "hours_sleep": hours_sleep,
                             "glass_water": glass_water,
                             "activity_minutes": activity_minutes,
                             "well_being": well_being_val,
                             "last_time": int(time.time()),
                             "HI": []}
        new_data[user_id]["HI"].append(HI)
        save_data(data=new_data)

    @router.message(STATISTICS_COMMAND, StateFilter("*"))
    async def statistic(message: Message, state: FSMContext):
        await state.clear()
        user_id = str(message.from_user.id)
        data = load_data()
        try:
            idcheck = data[user_id]
            if data[user_id]["early_hours_sleep"] is None:
                await message.answer("📊 Статистика за останній день:\n"
                                     f"🛌 Ви спали годин: {data[user_id]["hours_sleep"]},\n"
                                     f"💧 Ви випили склянок води: {data[user_id]["glass_water"]},\n"
                                     f"🏃 У вас було хвилин активностей: {data[user_id]["activity_minutes"]},\n"
                                     f"🙆 Ваше самопочуття: {data[user_id]["well_being"]}/10.\n"
                                     f"\n"
                                     f"📅 Ви користуєтесь програмою 1 день.")
            else:
                average = sum(data[user_id]["HI"]) // len(data[user_id]["HI"])
                if average.is_integer():
                    result = int(average)
                else:
                    result = round(average, 1)
                await message.answer("📊 Статистика за передостанній день:\n"
                                     f"🛌 Ви спали годин: {data[user_id]["early_hours_sleep"]},\n"
                                     f"💧 Ви випили склянок води: {data[user_id]["early_glass_water"]},\n"
                                     f"🏃 У вас було хвилин активностей: {data[user_id]["early_activity_minutes"]},\n"
                                     f"🙆 Ваше самопочуття: {data[user_id]["early_well_being"]}/10.\n"
                                     f"\n"
                                     "📊 Статистика за останній день:\n"
                                     f"🛌 Ви спали годин: {data[user_id]["hours_sleep"]},\n"
                                     f"💧 Ви випили склянок води: {data[user_id]["glass_water"]},\n"
                                     f"🏃 У вас було хвилин активностей: {data[user_id]["activity_minutes"]},\n"
                                     f"🙆 Ваше самопочуття: {data[user_id]["well_being"]}/10.\n"
                                     f"\n"
                                     f"📅 Ви користуєтесь програмою {len(data[user_id]["HI"])} днів,\n"
                                     f"💕 Ваш Health Index (HI) становить {result}")
        except Exception:
            await message.answer("❌ У вас ще немає статистики.")
            return

    @router.message(ADVICE_COMMAND, StateFilter("*"))
    async def cmd_advice(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("💡 Тут будуть поради.")

    @router.message(RESET_COMMAND, StateFilter("*"))
    async def cmd_reset(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("🔄 Прогрес скинуто.")
    await message.answer("✅ Дані збережено!", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@router.message(SECRET_COMMAND, StateFilter("*"))
async def send_from_url(message: Message):
    pic = URLInputFile("https://preview.redd.it/big-monke-flips-you-off-what-u-do-v0-861gk9gqka0c1.png?auto=webp&s=4ffd6a12783c45e1a56bb7c19a57ead83aaa4f33")
    await message.answer_photo(pic)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(
        [
            NEW_INFO_BOT_COMMAND,
            STATISTICS_BOT_COMMAND,
            ADVICE_BOT_COMMAND,
            RESET_BOT_COMMAND,
        ]
    )
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())














