from aiogram.filters import Command  #Для бота
from aiogram.types.bot_command import BotCommand  #Для користувача

NEW_INFO_BOT_COMMAND = BotCommand(command="new_info", description="Запустити бота")
STATISTICS_BOT_COMMAND = BotCommand(command="statistic", description="Показати список книг")
ADVICE_BOT_COMMAND = BotCommand(command="advice", description="Додати книгу")
RESET_BOT_COMMAND = BotCommand(command="reset", description="Додати книгу")

NEW_INFO_COMMAND = Command("new_info")
STATISTICS_COMMAND = Command("statistic")
ADVICE_COMMAND = Command("advice")
RESET_COMMAND = Command("reset")