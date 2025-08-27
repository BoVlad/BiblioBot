import asyncio
import logging
import json
import sys
import time

from random import shuffle
from aiogram import Bot, Dispatcher, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types.bot_command import BotCommand
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.input_file import URLInputFile

from Config import BOT_TOKEN

HELP_BOT_COMMAND = BotCommand(command="help", description="Допомога в боті")
RESET_BOT_COMMAND = BotCommand(command="reset", description="Скинути прогрес")
NEW_INFO_BOT_COMMAND = BotCommand(command="new_info", description="Ввести дані за сьогодні")
STATISTICS_BOT_COMMAND = BotCommand(command="statistic", description="Показати статистику")
ADVICE_BOT_COMMAND = BotCommand(command="advice", description="Вивести поради для покращення стану")


HELP_COMMAND = Command("help")
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

class ResetConfirm(StatesGroup):
    confirm = State()

DATA_FILE = "data.json"
TOKEN = BOT_TOKEN
ALL_SYMBOLS = [
    'a','b','c','d','e','f','g','h','i','j','k','l','m',
    'n','p','q','r','s','t','u','v','w','x','y','z',
    'A','B','C','D','E','F','G','H','I','J','K','L','M',
    'N','P','Q','R','S','T','U','V','W','X','Y','Z',
    '1','2','3','4','5','6','7','8','9'
]

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


@router.message(STATISTICS_COMMAND, StateFilter("*"))
async def statistic(message: Message, state: FSMContext):
    await state.clear()
    user_id = str(message.from_user.id)
    data = load_data()
    try:
        idcheck = data[user_id]
        if data[user_id]["early_hours_sleep"] is None:
            await message.answer("📊 Статистика за останній день:\n"
                                 "\n"
                                 f"🛌 Ви спали годин: {data[user_id]["hours_sleep"]},\n"
                                 f"💧 Ви випили склянок води: {data[user_id]["glass_water"]},\n"
                                 f"🏃 У вас було хвилин активностей: {data[user_id]["activity_minutes"]},\n"
                                 f"🙆 Ваше самопочуття: {data[user_id]["well_being"]}/10.\n"
                                 "\n"
                                 "\n"
                                 f"📅 Ви користуєтесь програмою 1 день.")
        else:
            average = round(sum(data[user_id]["HI"]) / len(data[user_id]["HI"]), 1)
            await message.answer("📊 Статистика за передостанній день:\n"
                                 "\n"
                                 f"🛌 Ви спали годин: {data[user_id]["early_hours_sleep"]},\n"
                                 f"💧 Ви випили склянок води: {data[user_id]["early_glass_water"]},\n"
                                 f"🏃 У вас було хвилин активностей: {data[user_id]["early_activity_minutes"]},\n"
                                 f"🙆 Ваше самопочуття: {data[user_id]["early_well_being"]}/10.\n"
                                 "\n"
                                 "\n"
                                 "📊 Статистика за останній день:\n"
                                 "\n"
                                 f"🛌 Ви спали годин: {data[user_id]["hours_sleep"]},\n"
                                 f"💧 Ви випили склянок води: {data[user_id]["glass_water"]},\n"
                                 f"🏃 У вас було хвилин активностей: {data[user_id]["activity_minutes"]},\n"
                                 f"🙆 Ваше самопочуття: {data[user_id]["well_being"]}/10.\n"
                                 "\n"
                                 "\n"
                                 f"📅 Ви користуєтесь програмою {len(data[user_id]["HI"])} днів,\n"
                                 f"💕 Ваш Health Index (HI) становить {average}")
    except Exception:
        await message.answer("❌ У вас ще немає статистики.")
        return

@router.message(ADVICE_COMMAND, StateFilter("*"))
async def cmd_advice(message: Message, state: FSMContext):
    await state.clear()
    user_id = str(message.from_user.id)
    data = load_data()
    try:
        idcheck = data[user_id]
        if data[user_id]["early_hours_sleep"] is None:
            hours_sleep = data[user_id]["hours_sleep"]
            glass_water = data[user_id]["glass_water"]
            activity_minutes = data[user_id]["activity_minutes"]
            well_being = data[user_id]["well_being"]
            if hours_sleep < 8:
                hours_sleep_text = "🛌❌ Ви спали замало, треба спати більше!"
            if 8 <= hours_sleep <= 12:
                hours_sleep_text = "🛌✅ Ваш сон в нормі! "
            if hours_sleep > 12:
                hours_sleep_text = "🛌❌ Ви спали забагато, треба спати менше!"
            if glass_water < 7:
                glass_water_text = "💧❌ Ви випили замало, треба пити більше!"
            if 7 <= glass_water <= 19:
                glass_water_text = "💧✅ Ваш водний баланс в нормі!"
            if glass_water > 19:
                glass_water_text = "💧❌ Ви випили забагато, треба пити менше!"
            if activity_minutes < 40:
                activity_minutes_text = "🏃❌ Ваших активних занятть замало, активнічайте більше!"
            if 40 <= activity_minutes <= 200:
                activity_minutes_text = "🏃✅ Кількість вашої активності в нормі!"
            if activity_minutes > 200:
                activity_minutes_text = "🏃❌ Ваших активних занятть забагато, активнічайте менше!"
            if well_being < 5:
                well_being_text = "🙆❌ Ви себе погано почуваєте! Якщо морально, то підійміть собі настрій 🤗. Якщо фізично - сходіть до лікаря 🏥."
            if 5 <= well_being <= 10:
                well_being_text = "🙆✅ Ви себе добре почуваєте! Це дуже круто!"
            await message.answer("📊 Поради за останній день:\n"
                                 "\n"
                                 f"{hours_sleep_text}\n"
                                 f"{glass_water_text}\n"
                                 f"{activity_minutes_text}\n"
                                 f"{well_being_text}")
            return


        else:
            hours_sleep = data[user_id]["hours_sleep"]
            glass_water = data[user_id]["glass_water"]
            activity_minutes = data[user_id]["activity_minutes"]
            well_being = data[user_id]["well_being"]

            early_hours_sleep = data[user_id]["early_hours_sleep"]
            early_glass_water = data[user_id]["early_glass_water"]
            early_activity_minutes = data[user_id]["early_activity_minutes"]
            early_well_being = data[user_id]["early_well_being"]

            if early_hours_sleep < 8:
                early_hours_sleep_text = "🛌❌ Ви спали замало, треба спати більше!"
            if 8 <= early_hours_sleep <= 12:
                early_hours_sleep_text = "🛌✅ Ваш сон в нормі! "
            if early_hours_sleep > 12:
                early_hours_sleep_text = "🛌❌ Ви спали забагато, треба спати менше!"
            if early_glass_water < 7:
                early_glass_water_text = "💧❌ Ви випили замало, треба пити більше!"
            if 7 <= early_glass_water <= 19:
                early_glass_water_text = "💧✅ Ваш водний баланс в нормі!"
            if early_glass_water > 19:
                early_glass_water_text = "💧❌ Ви випили забагато, треба пити менше!"
            if early_activity_minutes < 40:
                early_activity_minutes_text = "🏃❌ Ваших активних занятть замало, активнічайте більше!"
            if 40 <= early_activity_minutes <= 200:
                early_activity_minutes_text = "🏃✅ Кількість вашої активності в нормі!"
            if early_activity_minutes > 200:
                early_activity_minutes_text = "🏃❌ Ваших активних занятть забагато, активнічайте менше!"
            if early_well_being < 5:
                early_well_being_text = "🙆❌ Ви себе погано почуваєте! Якщо морально, то підійміть собі настрій 🤗."
            if 5 <= early_well_being <= 10:
                early_well_being_text = "🙆✅ Ви себе добре почуваєте! Це дуже круто!"

            if hours_sleep < 8:
                hours_sleep_text = "🛌❌ Ви спали замало, треба спати більше!"
            if 8 <= hours_sleep <= 12:
                hours_sleep_text = "🛌✅ Ваш сон в нормі! "
            if hours_sleep > 12:
                hours_sleep_text = "🛌❌ Ви спали забагато, треба спати менше!"
            if glass_water < 7:
                glass_water_text = "💧❌ Ви випили замало, треба пити більше!"
            if 7 <= glass_water <= 19:
                glass_water_text = "💧✅ Ваш водний баланс в нормі!"
            if glass_water > 19:
                glass_water_text = "💧❌ Ви випили забагато, треба пити менше!"
            if activity_minutes < 40:
                activity_minutes_text = "🏃❌ Ваших активних занятть замало, активнічайте більше!"
            if 40 <= activity_minutes <= 200:
                activity_minutes_text = "🏃✅ Кількість вашої активності в нормі!"
            if activity_minutes > 200:
                activity_minutes_text = "🏃❌ Ваших активних занятть забагато, активнічайте менше!"
            if well_being < 5:
                well_being_text = "🙆❌ Ви себе погано почуваєте! Якщо морально, то підійміть собі настрій 🤗. Якщо фізично - сходіть до лікаря 🏥."
            if 5 <= well_being <= 10:
                well_being_text = "🙆✅ Ви себе добре почуваєте! Це дуже круто!"

            early_average = round(sum(data[user_id]["HI"][:-1]) / len(data[user_id]["HI"][:-1]), 1)
            average = round(sum(data[user_id]["HI"]) / len(data[user_id]["HI"]), 1)

            if early_average < average:
                avarage_text = "📈 Ваш Health Index (HI) за останній день покращився! Так тримати!"
            if early_average > average:
                avarage_text = "📉 Ваш Health Index (HI) за останній день зменшився! Це погано, його треба підвищувати!"
            if early_average == average:
                avarage_text = "➖ Ваш Health Index (HI) за останні дні такий самий! Не погано і не добре!"

            await message.answer("📊 Поради за передостанній день:\n"
                                 "\n"
                                 f"{early_hours_sleep_text}\n"
                                 f"{early_glass_water_text}\n"
                                 f"{early_activity_minutes_text}\n"
                                 f"{early_well_being_text}\n"
                                 "\n"
                                 "\n"
                                 "📊 Поради за останній день:\n"
                                 "\n"
                                 f"{hours_sleep_text}\n"
                                 f"{glass_water_text}\n"
                                 f"{activity_minutes_text}\n"
                                 f"{well_being_text}\n"
                                 "\n"
                                 "\n"
                                 "📊 Підведемо підсумки:\n"
                                 "\n"
                                 f"{avarage_text}")
            return
    except Exception:
        await message.answer("❌ Ви ще не ввели дані хоча би один раз. Введіть дані що би подивитися поради!")



@router.message(SECRET_COMMAND, StateFilter("*"))
async def cmd_secret_command(message: Message, state: FSMContext):
    await state.clear()
    pic = URLInputFile("https://preview.redd.it/big-monke-flips-you-off-what-u-do-v0-861gk9gqka0c1.png?auto=webp&s=4ffd6a12783c45e1a56bb7c19a57ead83aaa4f33")
    await message.answer_photo(pic)


@router.message(HELP_COMMAND, StateFilter("*"))
async def cmd_secret_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Допомога:\n"
                         "\n"
                         "• /new_info - це команда для вводу нових даних. Вводьте дані кожен день для відслідковування вашого здоров'я!\n"
                         "• /statistic - це команда для відображення статистики. Введіть дані хоча б один раз, щоб дивитися статистику.\n"
                         "• /advice - це команда для відображення порад щодо покращення вашого рівня здоров'я. Введіть дані хоча б один раз, щоб дивитися поради.\n"
                         "• /reset - це команда для онулення всіх записів. Введіть дані хоча б один раз, щоб онулити всі записи.")


@router.message(RESET_COMMAND, StateFilter("*"))
async def cmd_reset(message: Message, state: FSMContext):
    await state.clear()
    user_id = str(message.from_user.id)
    data = load_data()
    try:
        idcheck = data[user_id]
        letters_shuffle = ""
        for i in range (6):
            shuffle(ALL_SYMBOLS)
            shuffle(ALL_SYMBOLS)
            shuffle(ALL_SYMBOLS)
            letters_shuffle = letters_shuffle + ALL_SYMBOLS[1]
        await state.update_data(letters_shuffle=letters_shuffle)
        await state.set_state(ResetConfirm.confirm)
        await message.answer(f"❗ Щоб видалити всю інформацію введіть (так само): {letters_shuffle}")
    except Exception:
        await message.answer("❌ Про вас ще немає записів")

@router.message(ResetConfirm.confirm)
async def reset_confirm(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    data = load_data()
    user_data = await state.get_data()
    letters_shuffle = user_data.get("letters_shuffle")
    if message.text == letters_shuffle:
        del data[user_id]
        save_data(data=data)
        await message.answer("✅ Дані успішно видалено!")
        await state.clear()
    else:
        await message.answer("✅ Видалення даних успішно скасоване!")
        await state.clear()




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
                  "early_well_being": new_data[user_id].get("well_being"),
                  "hours_sleep": hours_sleep,
                  "glass_water": glass_water,
                  "activity_minutes": activity_minutes,
                  "well_being": well_being_val,
                  "last_time": int(time.time()),
                  "HI": new_data[user_id]["HI"]}
        new_data[user_id]["HI"].append(HI)
        save_data(data=new_data)
    except Exception:
        new_data[user_id] = {"early_hours_sleep": None,
                             "early_glass_water": None,
                             "early_activity_minutes": None,
                             "early_well_being": None,
                             "hours_sleep": hours_sleep,
                             "glass_water": glass_water,
                             "activity_minutes": activity_minutes,
                             "well_being": well_being_val,
                             "last_time": int(time.time()),
                             "HI": []}
        new_data[user_id]["HI"].append(HI)
        save_data(data=new_data)
    await message.answer("✅ Дані успішно збережено!", reply_markup=ReplyKeyboardRemove())
    await state.clear()




async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(
        [
            HELP_BOT_COMMAND,
            NEW_INFO_BOT_COMMAND,
            STATISTICS_BOT_COMMAND,
            ADVICE_BOT_COMMAND,
            RESET_BOT_COMMAND,
        ]
    )
    dp.include_router(router)
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())














