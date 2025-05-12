import os
import logging
import psycopg2
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Загрузка переменных из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_CONFIG = {
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": 5432,
    "database": "laba5proga"
}

# Логирование
logging.basicConfig(level=logging.INFO)

# Подключение к БД
conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = True
cursor = conn.cursor()

# FSM
class CurrencyFSM(StatesGroup):
    name = State()
    rate = State()
    delete_name = State()
    update_name = State()
    update_rate = State()
    convert_name = State()
    convert_amount = State()


def is_admin(chat_id):
    cursor.execute("SELECT 1 FROM admins WHERE chat_id = %s", (str(chat_id),))
    return cursor.fetchone() is not None

# Создание бота и диспетчера
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# Команда /start
@dp.message(Command("start"))
async def start_cmd(message: Message):
    if is_admin(message.from_user.id):
        commands = ["/start", "/manage_currency", "/get_currencies", "/convert"]
    else:
        commands = ["/start", "/get_currencies", "/convert"]
    await message.answer("Меню команд:\n" + "\n".join(commands))

# Команда /manage_currency
@dp.message(Command("manage_currency"))
async def manage_currency(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Нет доступа к команде.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить валюту", callback_data="add_currency"),
         InlineKeyboardButton(text="Удалить валюту", callback_data="delete_currency"),
         InlineKeyboardButton(text="Изменить курс валюты", callback_data="update_currency")]
    ])
    await message.answer("Выберите действие:", reply_markup=kb)

# Кнопка: Добавить валюту
@dp.callback_query(F.data == "add_currency")
async def cb_add_currency(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название валюты:")
    await state.set_state(CurrencyFSM.name)

@dp.message(CurrencyFSM.name)
async def input_currency_name(message: Message, state: FSMContext):
    name = message.text.strip().upper()
    cursor.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (name,))
    if cursor.fetchone():
        await message.answer("Данная валюта уже существует.")
        await state.clear()
        return
    await state.update_data(name=name)
    await message.answer("Введите курс к рублю:")
    await state.set_state(CurrencyFSM.rate)

@dp.message(CurrencyFSM.rate)
async def input_currency_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text.replace(',', '.'))
        data = await state.get_data()
        cursor.execute("INSERT INTO currencies(currency_name, rate) VALUES (%s, %s)", (data['name'], rate))
        await message.answer(f"Валюта {data['name']} успешно добавлена.")
    except ValueError:
        await message.answer("Введите корректное число.")
    await state.clear()

# Кнопка: Удалить валюту
@dp.callback_query(F.data == "delete_currency")
async def cb_delete_currency(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название валюты:")
    await state.set_state(CurrencyFSM.delete_name)

@dp.message(CurrencyFSM.delete_name)
async def delete_currency(message: Message, state: FSMContext):
    name = message.text.strip().upper()
    cursor.execute("DELETE FROM currencies WHERE currency_name = %s", (name,))
    await message.answer("Валюта удалена (если существовала).")
    await state.clear()

# Кнопка: Изменить курс
@dp.callback_query(F.data == "update_currency")
async def cb_update_currency(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название валюты:")
    await state.set_state(CurrencyFSM.update_name)

@dp.message(CurrencyFSM.update_name)
async def input_update_name(message: Message, state: FSMContext):
    name = message.text.strip().upper()
    await state.update_data(name=name)
    await message.answer("Введите новый курс к рублю:")
    await state.set_state(CurrencyFSM.update_rate)

@dp.message(CurrencyFSM.update_rate)
async def input_update_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text.replace(',', '.'))
        data = await state.get_data()
        cursor.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (rate, data['name']))
        await message.answer("Курс обновлён.")
    except ValueError:
        await message.answer("Введите корректное число.")
    await state.clear()

# Команда /get_currencies
@dp.message(Command("get_currencies"))
async def get_currencies(message: Message):
    cursor.execute("SELECT currency_name, rate FROM currencies")
    rows = cursor.fetchall()
    if not rows:
        await message.answer("Список валют пуст.")
        return
    text = "\n".join([f"{name}: {rate}" for name, rate in rows])
    await message.answer("Список валют:\n" + text)

# Команда /convert
@dp.message(Command("convert"))
async def convert_start(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyFSM.convert_name)

@dp.message(CurrencyFSM.convert_name)
async def convert_input_currency(message: Message, state: FSMContext):
    name = message.text.strip().upper()
    cursor.execute("SELECT rate FROM currencies WHERE currency_name = %s", (name,))
    result = cursor.fetchone()
    if not result:
        await message.answer("Валюта не найдена.")
        await state.clear()
        return
    rate = result[0]
    await state.update_data(name=name, rate=rate)
    await message.answer("Введите сумму:")
    await state.set_state(CurrencyFSM.convert_amount)

@dp.message(CurrencyFSM.convert_amount)
async def convert_input_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        data = await state.get_data()
        rub = amount * float(data['rate'])
        await message.answer(f"{amount} {data['name']} = {rub:.2f} RUB")
    except ValueError:
        await message.answer("Введите корректную сумму.")
    await state.clear()

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
