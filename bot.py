import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from pars import entry
from aiofiles import os

logging.basicConfig(level=logging.INFO)
with open("token.txt", "r") as token_file:
    token = token_file.readline()
API_TOKEN = token

bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Searcher(StatesGroup):
    name = State()
    age = State()
    gender = State()
    city_selection = State()
    quantity_selection = State()
    sending_data = State()
    one_more_thing = State()


@dp.message_handler(state='*', commands='help')
async def Help(message: types.Message):
    await message.reply(
        "Этот бот поможет вам собрать информацию о скидкх в интернет магазине Магнит (https://magnit.ru/). "
        "Для запуска бота напишите команду /start или выберете ее в меню. "
        "Если вы хотите отключить или перезапустить бота напишите команду /cancel (в меню она также доступна).\n \n"
        "Не отправляйте запросы на скидки слишком часто, вас могут забанить на сайте магнита. "
        "Если это все же произошло перезапустите роутер, бан пропадет. "
        "Если вы отправили большой запрос подожите немного, боту нужно время, чтобы собрать информацию о скидках. "
    )


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await Searcher.name.set()

    await message.reply("Как вас зовут?")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)

    await state.finish()

    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Searcher.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await Searcher.next()
    await message.reply("Сколько вам лет?")


@dp.message_handler(lambda message: not message.text.isdigit(), state=Searcher.age)
async def process_age_invalid(message: types.Message):
    return await message.reply("Возраст должежен быть числом.\nСколько вам лет? (только целое число)")


@dp.message_handler(lambda message: message.text.isdigit(), state=Searcher.age)
async def process_age(message: types.Message, state: FSMContext):
    await Searcher.next()
    await state.update_data(age=int(message.text))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Дора", "Мейби-Бейби")
    markup.add("Другое")
    await message.reply("Дора или Мейби-Бейби?", reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ["Дора", "Мейби-Бейби"], state=Searcher.gender)
async def process_gender_invalid(message: types.Message):
    return await message.reply("Вы неправы, попробуйте еще раз")


@dp.message_handler(state=Searcher.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['хрень'] = message.text

        markup = types.ReplyKeyboardRemove()

        if int(data['age']) < 18:
            await bot.send_message(
                message.chat.id,
                md.text(
                    md.text('Приятно познакомиться,', md.bold(data['name'])),
                    md.text('Возраст:', md.code(data['age'])),
                    md.text('Ваш выбор:', data['хрень']),
                    md.text('Перейдем все же к поиску товаров, вам нет 18 лет, так что алкоголь вам не доступен'),
                    sep='\n',
                ),
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await bot.send_message(
                message.chat.id,
                md.text(
                    md.text('Прияьно познакомиться,', md.bold(data['name'])),
                    md.text('Возраст:', md.code(data['age'])),
                    md.text('Вы выбрали:', data['хрень']),
                    md.text('Перейдем все же к поиску товаров'),
                    sep='\n',
                ),
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN,
            )

        await Searcher.next()
        start_buttons = ['Москва', 'Санкт-Петербург', 'Челябинск', 'Новосибирск', 'Краснодар']
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(*start_buttons)
        await message.answer('Пожалуйста, выберете город', reply_markup=keyboard)


@dp.message_handler(state=Searcher.city_selection)
async def chose_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
        data['chat_id'] = message.chat.id
    await Searcher.next()
    await message.reply("Сколько товаров хотите посмотреть?")


@dp.message_handler(lambda message: (not message.text.isdigit() or int(message.text) < 1 or int(message.text) > 2000),
                    state=Searcher.quantity_selection)
async def process_age_invalid(message: types.Message):
    return await message.reply("Количество должно задаваться числом от 1 до 2000.\nСколько товаров хотите посмотреть? "
                               "(только цифры)")


@dp.message_handler(lambda message: (message.text.isdigit() and 1 < int(message.text) < 2000),
                    state=Searcher.quantity_selection)
async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['quantity'] = message.text
    await Searcher.next()
    await state.update_data(quantity=int(message.text))

    await message.answer('Подождите несколько секунд...')
    cities = {
        'Москва': '1',
        'Санкт-Петербург': '2',
        'Челябинск': '3',
        'Новосибирск': '4',
        'Краснодар': '5',
    }

    async with state.proxy() as data:
        age = data['age']
        quantity = data['quantity']
        city_code = cities.get(data['city'])
        chat_id = data['chat_id']

    await send_data(city_code=city_code, chat_id=chat_id, age=age, quantity=quantity)

    await message.reply("Можете запросить товары других городов")

    await Searcher.previous()


async def send_data(city_code='', chat_id='', age=20, quantity=50):
    file = await entry(city_path=city_code, age=age, quantity=quantity)
    await bot.send_document(chat_id=chat_id, document=open(file, 'rb'))
    await os.remove(file)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
