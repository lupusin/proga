import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение токена из переменной окружения
API_TOKEN = '7669247301:AAHSnwIBN9yzQ6EmSpxaPmRXzYt2JQIp_XM'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)  # Теперь передаем только storage

# Словарь для хранения курсов валют
currency_rates = {}

# Состояния FSM
class CurrencyStates(StatesGroup):
    waiting_for_currency_name = State()
    waiting_for_currency_rate = State()
    waiting_for_convert_currency = State()
    waiting_for_convert_amount = State()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply(
        "Привет! Я бот для конвертации валют.\n"
        "Доступные команды:\n"
        "/save_currency — сохранить курс валюты\n"
        "/convert — конвертировать валюту в рубли"
    )

# Обработчик команды /save_currency
@dp.message(Command("save_currency"))
async def cmd_save_currency(message: Message, state: FSMContext):
    await message.reply("Введите название валюты (например, USD, EUR):")
    await state.set_state(CurrencyStates.waiting_for_currency_name)

# Обработчик ввода названия валюты
@dp.message(CurrencyStates.waiting_for_currency_name)
async def process_currency_name(message: Message, state: FSMContext):
    currency_name = message.text.upper()
    await state.update_data(currency_name=currency_name)
    await message.reply(f"Введите курс {currency_name} к рублю (например, 75.5):")
    await state.set_state(CurrencyStates.waiting_for_currency_rate)

# Обработчик ввода курса валюты
@dp.message(CurrencyStates.waiting_for_currency_rate)
async def process_currency_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text)
        if rate <= 0:
            raise ValueError("Курс должен быть положительным числом!")
        
        data = await state.get_data()
        currency_name = data['currency_name']
        currency_rates[currency_name] = rate
        
        await message.reply(f"Курс {currency_name} сохранён: 1 {currency_name} = {rate} RUB")
        await state.clear()
    except ValueError:
        await message.reply("Ошибка! Введите корректное число (например, 75.5).")

# Обработчик команды /convert
@dp.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext):
    if not currency_rates:
        await message.reply("Нет сохранённых валют. Сначала используйте /save_currency.")
        return
    
    await message.reply(
        "Введите название валюты для конвертации:\n"
        f"Доступные валюты: {', '.join(currency_rates.keys())}"
    )
    await state.set_state(CurrencyStates.waiting_for_convert_currency)

# Обработчик ввода валюты для конвертации
@dp.message(CurrencyStates.waiting_for_convert_currency)
async def process_convert_currency(message: Message, state: FSMContext):
    currency_name = message.text.upper()
    if currency_name not in currency_rates:
        await message.reply("Ошибка! Валюта не найдена. Попробуйте ещё раз.")
        return
    
    await state.update_data(currency_name=currency_name)
    await message.reply(f"Введите сумму в {currency_name} для конвертации в рубли:")
    await state.set_state(CurrencyStates.waiting_for_convert_amount)

# Обработчик ввода суммы для конвертации
@dp.message(CurrencyStates.waiting_for_convert_amount)
async def process_convert_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной!")
        
        data = await state.get_data()
        currency_name = data['currency_name']
        rate = currency_rates[currency_name]
        result = amount * rate
        
        await message.reply(f"{amount} {currency_name} = {result:.2f} RUB")
        await state.clear()
    except ValueError:
        await message.reply("Ошибка! Введите корректное число (например, 100).")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())