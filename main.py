import asyncio
import logging
import sys




import requests
import requests
from bs4 import BeautifulSoup

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from reques import check, check_misto_vul, check_kyiv, kyiv_done, list_kyiv_bud, get_id

# Bot token can be obtained via https://t.me/BotFather
TOKEN = '6861510096:AAEyv-Nq1guUYOri9ZuDMXFSpLoo6EXWmic'

class Kharkiv(StatesGroup):
    position = State()
    vul = State()
    nom = State()

class Kyiv(StatesGroup):
    id = State()
    vul = State()
    nom = State()


class MyCallback(CallbackData, prefix='my'):
    name: str
    id: int


def create_electrotime():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Kharkiv',
        callback_data=MyCallback(name='Kharkiv', id='1')
    )
    builder.button(
        text='Kyiv',
        callback_data=MyCallback(name='Kyiv', id='1')

    )
    return builder.as_markup()



dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привіт, {html.bold(message.from_user.full_name)}!\n"
                         f"Виберіть місто/область", reply_markup=create_electrotime())
@dp.callback_query(MyCallback.filter(F.name == 'Kyiv'))
async def kyiv_enegry(query: CallbackQuery, state: FSMContext):
    await state.set_state(Kyiv.vul)
    await query.message.answer("Введіть вулицю")

@dp.message(Kyiv.vul)
async def kyiv_vul(message: Message, state: FSMContext):
    await state.update_data(vul=message.text)
    data = await state.get_data()
    b = check_kyiv(data['vul'])
    bud = ', '.join(list_kyiv_bud(check_kyiv(data['vul'])))
    if b and list_kyiv_bud(b):
        await state.set_state(Kyiv.nom)
        await message.answer('Введіть номер будинку:')
        await message.answer(bud)
    else:
        await message.answer("Введіть ще раз")

@dp.message(Kyiv.nom)
async def kyiv_nom(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text in list_kyiv_bud(check_kyiv(data['vul'])):
        await state.update_data(nom=message.text)
        await message.answer(kyiv_done(
            f'https://api.yasno.com.ua/api/v1/electricity-outages-schedule/houses?region=kiev&street_id={message.text}'))
    else:
        await message.answer("Введіть ще раз")


@dp.callback_query(MyCallback.filter(F.name == 'Kharkiv'))
async def kharkiv_enegry(query: CallbackQuery, state: FSMContext):
    await state.set_state(Kharkiv.position)
    await query.message.answer("Введіть населенний пункт/Місто")
@dp.message(Kharkiv.position)
async def kharkiv_pos(message: Message, state: FSMContext):
    await state.update_data(position=message.text)
    responce = requests.get(f'https://kharkiv.energy-ua.info/select/{message.text}/')
    if responce.status_code == 200:
        await state.set_state(Kharkiv.vul)
        await message.answer("Введіть назву вулиці")
    else:
        await message.answer("Такого населеного пункту не існує!\n"
                             "Введіть ще раз!")



vull = []
@dp.message(Kharkiv.vul)
async def kh_vul(message: Message, state: FSMContext):
    await state.update_data(vul=message.text.title().replace(' ', '%20'))
    data = await state.get_data()
    print(message.text.replace(' ', '%20'))
    responce = requests.get(f'https://kharkiv.energy-ua.info/select/{data['position']}/')
    if responce.status_code == 200:
        if check_misto_vul(f'https://kharkiv.energy-ua.info/select/{data['position']}/', message.text):
            # await message.answer(f'https://kharkiv.energy-ua.info/grafik/{data['position']}/{data['vul']}/')
            responce = requests.get(f'https://kharkiv.energy-ua.info/select/{data['position']}/{data['vul']}/')
            page = responce.text
            soup = BeautifulSoup(page, "html.parser")
            lists = list()
            block = soup.find('div', class_ ='row nums_block')
            if block:
                for a_tag in block.find_all('a'):
                    # concatenated_text += a_tag.text(strip=True) + ' '
                    lists.append(a_tag.get_text(strip=True))
                list_all = ', '.join(lists)

                await state.set_state(Kharkiv.nom)
                await message.answer(f'Список н-будинків в наявності: {list_all}')
                await message.answer("Введіть номер будинку:")

            else:
                await message.answer(check(f'https://kharkiv.energy-ua.info/select/{data['position']}/{data['vul']}/'))
        else:
            await message.answer('Такої вул не існує')

@dp.message(Kharkiv.nom)
async def khrakiv_nom(message: Message, state: FSMContext):
    await state.update_data(nom=message.text.replace('/', '%23fract%23'))
    data = await state.get_data()
    text = f"https://kharkiv.energy-ua.info/grafik/{data['position']}/{data['vul']}/{data['nom']}"
    print(text)
    await message.answer(check(text))





async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())