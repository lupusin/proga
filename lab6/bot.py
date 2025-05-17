import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
router = Router()

# Состояния FSM для управления валютами
class CurrencyStates(StatesGroup):
    waiting_currency_name = State()
    waiting_rate = State()
    waiting_rate_new = State()
    waiting_currency_to_delete = State()
    waiting_currency_to_update = State()

# Состояния FSM для конвертации валюты
class ConvertStates(StatesGroup):
    waiting_currency_name = State()
    waiting_amount = State()

# Инициализация бота
bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

def check_currency_exists(currency_name: str) -> bool:
    response = requests.get('http://localhost:5002/currencies')
    if response.status_code == 200:
        currencies = response.json()
        return any(curr['name'] == currency_name for curr in currencies)
    return False

# Команда /start
@router.message(Command("start"))
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/manage_currency")],
            [KeyboardButton(text="/get_currencies")],
            [KeyboardButton(text="/convert")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите команду:", reply_markup=markup)

# Обработка /manage_currency
@router.message(Command("manage_currency"))
async def manage_currency(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить валюту")],
            [KeyboardButton(text="Удалить валюту")],
            [KeyboardButton(text="Изменить курс")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите действие:", reply_markup=markup)

# Добавление валюты
@router.message(F.text == "Добавить валюту")
async def add_currency_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CurrencyStates.waiting_currency_name)

@router.message(CurrencyStates.waiting_currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    if check_currency_exists(message.text):
        await message.answer("Данная валюта уже существует!")
        await state.clear()
        return
    
    await state.update_data(currency_name=message.text)
    await message.answer("Введите курс к рублю:")
    await state.set_state(CurrencyStates.waiting_rate)

@router.message(CurrencyStates.waiting_rate)
async def process_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text)
        data = await state.get_data()
        
        response = requests.post(
            'http://localhost:5001/load',
            json={'currency_name': data['currency_name'], 'rate': rate}
        )
        if response.status_code == 200:
            await message.answer(f"Валюта {data['currency_name']} успешно добавлена!")
        else:
            await message.answer("Ошибка при добавлении!")
    
    except ValueError:
        await message.answer("Некорректный курс!")
    
    await state.clear()

# Удаление валюты
@router.message(F.text == "Удалить валюту")
async def delete_currency_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты для удаления:")
    await state.set_state(CurrencyStates.waiting_currency_to_delete)

@router.message(CurrencyStates.waiting_currency_to_delete)
async def process_delete_currency(message: types.Message, state: FSMContext):
    currency_name = message.text
    
    response = requests.post(
        'http://localhost:5001/delete',
        json={'currency_name': currency_name}
    )
    if response.status_code == 200:
        await message.answer(f"Валюта {currency_name} удалена!")
    else:
        await message.answer("Валюта не найдена!")
    
    await state.clear()

# Изменение курса
@router.message(F.text == "Изменить курс")
async def update_currency_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyStates.waiting_currency_to_update)

@router.message(CurrencyStates.waiting_currency_to_update)
async def process_currency_to_update(message: types.Message, state: FSMContext):
    currency_name = message.text
    if not check_currency_exists(currency_name):
        await message.answer("Валюта не найдена!")
        await state.clear()
        return
    
    await state.update_data(currency_name=currency_name)
    await message.answer("Введите новый курс:")
    await state.set_state(CurrencyStates.waiting_rate_new)

@router.message(CurrencyStates.waiting_rate_new)
async def process_currency_rate_new(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text)
        data = await state.get_data()
        
        response = requests.post(
            'http://localhost:5001/update_currency',
            json={'currency_name': data['currency_name'], 'rate': rate}
        )
        if response.status_code == 200:
            await message.answer(f"Валюта {data['currency_name']} успешно обновлена!")
        else:
            await message.answer("Ошибка при обновлении!")
    
    except ValueError:
        await message.answer("Некорректный курс!")
    
    await state.clear()

# Команда /get_currencies
@router.message(Command("get_currencies"))
async def get_currencies(message: types.Message):
    response = requests.get('http://localhost:5002/currencies')
    if response.status_code == 200:
        currencies = response.json()
        response_text = "\n".join(
            [f"{curr['name']}: {curr['rate']} руб." 
             for curr in currencies]
        ) or "Нет доступных валют"
        await message.answer(response_text)
    else:
        await message.answer("Ошибка получения данных")

# Конвертация валюты
@router.message(Command("convert"))
async def convert_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ConvertStates.waiting_currency_name)

@router.message(ConvertStates.waiting_currency_name)
async def process_convert_currency(message: types.Message, state: FSMContext):
    if not check_currency_exists(message.text):
        await message.answer("Валюта не найдена!")
        await state.clear()
        return
    
    await state.update_data(currency=message.text)
    await message.answer("Введите сумму:")
    await state.set_state(ConvertStates.waiting_amount)

@router.message(ConvertStates.waiting_amount)
async def process_convert_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        data = await state.get_data()
        
        response = requests.get(
            'http://localhost:5002/convert',
            params={'currency': data['currency'], 'amount': amount}
        )
        if response.status_code == 200:
            result = response.json().get('result', 0)
            await message.answer(f"Результат: {result:.2f} руб.")
        else:
            await message.answer("Ошибка конвертации!")
    
    except ValueError:
        await message.answer("Некорректная сумма!")
    
    await state.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())