
import asyncio
import logging
from datetime import datetime
import requests
import psycopg2
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import os
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")


conn = psycopg2.connect(dbname="finance_bot", user="postgres", password="password", host="localhost")
cursor = conn.cursor()


logging.basicConfig(level=logging.INFO)


bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())


class Register(StatesGroup):
    name = State()

class AddOperation(StatesGroup):
    type_operation = State()
    sum = State()
    date = State()
    payment_method = State()
class ViewOperations(StatesGroup):
    currency = State()

@dp.message(Command("reg"))
async def cmd_register(message: Message, state: FSMContext):
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if cursor.fetchone():
        await message.answer("Вы уже зарегистрированы.")
    else:
        await message.answer("Введите ваш логин:")
        await state.set_state(Register.name)

@dp.message(Register.name)
async def process_name(message: Message, state: FSMContext):
    cursor.execute("INSERT INTO users (name, chat_id) VALUES (%s, %s)", (message.text, message.chat.id))
    conn.commit()
    await state.clear()
    await message.answer("Регистрация прошла успешно!")


@dp.message(Command("add_operation"))
async def cmd_add_operation(message: Message, state: FSMContext):
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if not cursor.fetchone():
        await message.answer("Вы не зарегистрированы. Используйте /reg.")
        return
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="РАСХОД")], [KeyboardButton(text="ДОХОД")]], resize_keyboard=True)
    await message.answer("Выберите тип операции:", reply_markup=kb)
    await state.set_state(AddOperation.type_operation)

@dp.message(AddOperation.type_operation)
async def process_type(message: Message, state: FSMContext):
    await state.update_data(type_operation=message.text)
    await message.answer("Введите сумму операции:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddOperation.sum)

@dp.message(AddOperation.sum)
async def process_sum(message: Message, state: FSMContext):
    try:
        float(message.text)
    except ValueError:
        await message.answer("Введите корректную сумму.")
        return
    await state.update_data(sum=message.text)
    await message.answer("Введите дату операции (в формате ГГГГ-ММ-ДД):")
    await state.set_state(AddOperation.date)

@dp.message(AddOperation.date)
async def process_date(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%Y-%m-%d")
    except ValueError:
        await message.answer("Неверный формат даты. Попробуйте еще раз.")
        return
    await state.update_data(date=message.text)

    data = await state.get_data()
    if data["type_operation"] == "РАСХОД":
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="НАЛИЧНЫЕ")], [KeyboardButton(text="КАРТА")]], resize_keyboard=True)
        await message.answer("Выберите способ оплаты:", reply_markup=kb)
        await state.set_state(AddOperation.payment_method)
    else:
        cursor.execute("INSERT INTO operations (date, sum, chat_id, type_operation, payment_method) VALUES (%s, %s, %s, %s, %s)",
                       (data["date"], data["sum"], message.chat.id, data["type_operation"], None))
        conn.commit()
        await message.answer("Операция добавлена!")
        await state.clear()

@dp.message(AddOperation.payment_method)
async def process_payment(message: Message, state: FSMContext):
    await state.update_data(payment_method=message.text)
    data = await state.get_data()
    cursor.execute("INSERT INTO operations (date, sum, chat_id, type_operation, payment_method) VALUES (%s, %s, %s, %s, %s)",
                   (data["date"], data["sum"], message.chat.id, data["type_operation"], data["payment_method"]))
    conn.commit()
    await message.answer("Операция добавлена!", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


currency_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="RUB"), KeyboardButton(text="USD"), KeyboardButton(text="EUR")]
    ],
    resize_keyboard=True
)
@dp.message(Command("operations"))
async def cmd_operations(message: Message, state: FSMContext):
    # 1-2: Проверка регистрации
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if not cursor.fetchone():
        await message.answer("Вы не зарегистрированы. Используйте /reg.")
        return    
    # 3: Предложить выбрать валюту
    await message.answer("Выберите валюту для просмотра операций:", reply_markup=currency_kb)
    await state.set_state(ViewOperations.currency)

@dp.message(ViewOperations.currency)
async def process_currency(message: Message, state: FSMContext):
    currency = message.text
    if currency not in ["RUB", "USD", "EUR"]:
        await message.answer("Пожалуйста, выберите одну из кнопок: RUB, USD или EUR.", reply_markup=currency_kb)
        return
    # 5: Получить курс, если нужно
    rate = 1.0
    if currency in ["USD", "EUR"]:
        resp = requests.get('http://localhost:5000/rate', params={"currency": currency})
        if resp.status_code != 200:
            await message.answer("Не удалось получить курс валют. Попробуйте позже.")
            await state.clear()
            return
        rate = resp.json().get("rate", 1.0)
    # 6: Получить операции из БД
    cursor.execute(
        "SELECT date, sum, type_operation, payment_method FROM operations WHERE chat_id = %s",
        (message.chat.id,)
    )
    rows = cursor.fetchall()
    # 7: Конвертация и формирование текста
    text = f"<b>Операции в {currency}</b>\n"
    for (date, amount, op_type, pay_method) in rows:
        converted = float(amount) * rate
        text += f"{date} | {op_type} | {converted:.2f} {currency}"
        if op_type == "РАСХОД" and pay_method:
            text += f" | {pay_method}"
        text += "\n"
    # 8: Отправка пользователю
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

import requests
resp = requests.get("http://127.0.0.1:5000/rate", params={"currency": "USD"})
print(resp.status_code, resp.text)
# Run bot
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
