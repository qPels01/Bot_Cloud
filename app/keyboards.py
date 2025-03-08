from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, 
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Зарегистрироваться')]],                              
                            resize_keyboard= True,
                            input_field_placeholder="Нажмите на кнопку чтобы зарегистрироватсья.")

folders_choice = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text='Создать папку', callback_data='create_folder')],
    [InlineKeyboardButton(text='Выбрать папку', callback_data="choose_folder")]
])

async def available_folders(folders: list):
    keyboard = InlineKeyboardBuilder()
    for folder in folders:
        keyboard.add(InlineKeyboardButton(text=folder, callback_data=f'folder_{folder}'))
    return keyboard.adjust(1).as_markup()

