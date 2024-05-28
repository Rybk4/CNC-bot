import logging
import os
import re
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from user import User

# Загрузка переменных окружения из файла .env
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')  # ID группы

# Настройка логирования
 

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
 

# Состояния для FSM
class Form(StatesGroup):
    city = State()
    full_name = State()
    phone_number = State()
    service_or_product = State()
    description = State()
    preferred_time = State()
    remarks = State()
    confirmation = State()

# Клавиатура с двумя кнопками /about и /reg
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton('/about'), KeyboardButton('/reg'))

# Обработчик команды /start
@dp.message_handler(commands=['start','help'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    await message.reply(f"Привет {user_name}, я бот, предназначенный для записи клиентов. Чтобы вы хотели узнать?", reply_markup=main_menu)

# Обработчик команды /about
@dp.message_handler(commands=['about'])
async def about(message: types.Message):
    await message.reply("Компания CNC. Более 1.5 года на рынке. Поставка IT-оборудования а также услуг. Наш сайт: http://cnc.kz Whatsapp: 77081904643 Почта: dchakmin2@mail.ru	Ввод с клавиатуры")

# Обработчик команды /reg
@dp.message_handler(commands=['reg'])
async def reg_start(message: types.Message):
    await Form.city.set()
    await message.reply("Ваш город?", reply_markup=ReplyKeyboardRemove())

# Обработчик команды /get_chat_id
@dp.message_handler(commands=['get_chat_id'])
async def get_chat_id(message: types.Message):
    chat_id = message.chat.id
    await message.reply(f"Chat ID: {chat_id}")

# Обработчик состояния города
@dp.message_handler(state=Form.city)
async def process_city(message: types.Message, state: FSMContext):
    city = message.text
    if len(city) < 2:
        await message.reply("ooops!!")
        await message.reply("Пожалуйста, введите корректное название города.")
        return
    async with state.proxy() as data:
        data['user'] = User()
        data['user'].city = city
    await Form.next()
    await message.reply("Ваше ФИО?")


# Обработчик состояния ФИО
@dp.message_handler(state=Form.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    full_name = message.text.strip().split()

    # Проверка, что введено три слова и каждое слово состоит как минимум из двух символов
    if len(full_name) != 3 or any(len(name) < 2 for name in full_name):
        await message.reply("ooops!!")
        await message.reply("Пожалуйста, введите корректное ФИО")
        return

    async with state.proxy() as data:
        data['user'].full_name = " ".join(full_name)
    await Form.next()
    await message.reply("Ваш номер телефона?")


# Обработчик состояния номера телефона
@dp.message_handler(state=Form.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    phone_number = message.text
    
    # Проверка на корректность введенного номера телефона
    if re.match(r'^\+?\d{11}$', phone_number):
        async with state.proxy() as data:
            data['user'].phone_number = phone_number
        # Клавиатура для выбора услуги или товара
        service_product_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        service_product_keyboard.add(KeyboardButton('Услуга'), KeyboardButton('Товар'))
        await Form.next()
        await message.reply("Это услуга или товар?", reply_markup=service_product_keyboard)
    else:
        await message.reply("Вы ввели что-то другое. Пожалуйста введите номер телефона.") # Просим пользователя ввести номер телефона заново
        await Form.phone_number.set()

# Обработчик состояния услуги или товара
@dp.message_handler(state=Form.service_or_product)
async def process_service_or_product(message: types.Message, state: FSMContext):
    service_or_product = message.text.strip().lower()

    # Проверка на корректность введенного значения
    if service_or_product in ['услуга', 'товар']:
        async with state.proxy() as data:
            data['user'].service_or_product = service_or_product.capitalize()
        await Form.next()
        await message.reply("Описание товара или услуги. В формате: полное наименование, характеристика, кол-во(шт).", reply_markup=ReplyKeyboardRemove())
    else:
        await message.reply("ooops!!")
        await message.reply("Пожалуйста, выберите 'Услуга' или 'Товар'.")
        # Просим пользователя выбрать снова
        service_product_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        service_product_keyboard.add(KeyboardButton('Услуга'), KeyboardButton('Товар'))
        await Form.service_or_product.set()
        await message.reply("Это услуга или товар?", reply_markup=service_product_keyboard)

# Обработчик состояния описания
@dp.message_handler(state=Form.description)
async def process_description(message: types.Message, state: FSMContext):
    description = message.text.strip()
    
    # Проверка на количество символов в описании (не менее 5)
    if len(description) >= 5:
        async with state.proxy() as data:
            data['user'].description = description

        # Клавиатура для выбора удобного времени
        time_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        time_keyboard.add(KeyboardButton('9:00 - 13:00'), KeyboardButton('14:00 - 18:00'))

        await message.reply("Удобный промежуток времени для звонка или сообщения с нашей стороны:", reply_markup=time_keyboard)
        await Form.next()
    else:
        await message.reply("ooops!!")
        await message.reply("Пожалуйста, введите описание снова.")
        # Просим пользователя ввести описание заново
        await Form.description.set()


# Обработчик состояния удобного времени
@dp.message_handler(state=Form.preferred_time)
async def process_preferred_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user'].preferred_time = message.text
    await Form.next()
    await message.reply("Есть ли у вас какие-либо примечания?", reply_markup=ReplyKeyboardRemove())

# Обработчик состояния примечаний
@dp.message_handler(state=Form.remarks)
async def process_remarks(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user'].remarks = message.text
        user_data = data['user']

    # Клавиатура для отправки или отмены заявки
    confirm_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    confirm_keyboard.add(KeyboardButton('Отправить'), KeyboardButton('Отменить'))

    await message.reply(f"Ваша заявка:\n\n{user_data}\n\nОтправить или отменить?", reply_markup=confirm_keyboard)
    await Form.confirmation.set()

# Обработчик подтверждения заявки
@dp.message_handler(lambda message: message.text in ["Отправить", "Отменить"], state=Form.confirmation)
async def process_confirmation(message: types.Message, state: FSMContext):
    if message.text == "Отправить":
        async with state.proxy() as data:
            user_data = data['user']
            try:
                await bot.send_message(GROUP_ID, f"Новая заявка:\n\n{user_data}")
            except Exception as e:
                logging.error(f"Failed to send message to group: {e}")
        await message.reply("Как только менеджер рассмотрит вашу заявку, он с вами свяжется.", reply_markup=main_menu)
    else:
        await message.reply("Заявка отменена.", reply_markup=main_menu)
    await state.finish()

# Обработчик текстовых сообщений
@dp.message_handler(content_types=types.ContentType.TEXT)
async def process_text(message: types.Message):
    text = message.text.lower()
    if text == "/about" or text == "/reg" or text == "/start" or text == "/help":
        return
    else:
        # Отправляем список доступных команд
        await message.reply("Для работы с ботом используйте следующие команды:\n"
                            "/start - Начать работу с ботом\n"
                            "/about - Узнать о компании\n"
                            "/reg - Заполнить заявку\n"
                            "/help - Показать доступные команды")

# Обработчик картинок
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def process_photo(message: types.Message):
    # Выполняем команду /help
    await send_welcome(message)

if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
