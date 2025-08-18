from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

class BookCallBack(CallbackData, prefix="book"):
    id: int

def books_keyboard_markup(book_list: list[dict]) -> InlineKeyboardMarkup:
    keyboard = []
    for i, book in enumerate(book_list):
        keyboard.append([
            InlineKeyboardButton(
                text=book["name"],
                callback_data = BookCallBack(id=i).pack()
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
