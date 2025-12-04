from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_role_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("مدیر"), KeyboardButton("معلم"), KeyboardButton("دانش‌آموز"))
    return kb

def get_manager_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("ایجاد مدرسه جدید"), KeyboardButton("مدرسه دارم"))
    kb.add(KeyboardButton("🔙 بازگشت"))
    return kb