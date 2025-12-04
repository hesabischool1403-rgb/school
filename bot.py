import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# توکن باتت رو اینجا بگذار
bot = telebot.TeleBot('8445025503:AAHVcaodMF0T3keffr_CGjVc6Es1gUL3c9c')

# دیکشنری برای ذخیره وضعیت کاربرها (state)
user_states = {}
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('مدیر'), KeyboardButton('دانش‌آموز'), KeyboardButton('معلم'))
    bot.send_message(message.chat.id, "سلام! شما مدیر هستید، دانش‌آموز یا معلم؟", reply_markup=markup)
    user_states[message.chat.id] = 'select_role'

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'select_role')
def select_role(message):
    if message.text == 'مدیر':
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('ایجاد مدرسه جدید'), KeyboardButton('مدرسه دارم'))
        bot.send_message(message.chat.id, "خوش آمدید مدیر! گزینه مورد نظر را انتخاب کنید:", reply_markup=markup)
        user_states[message.chat.id] = 'manager_options'
    elif message.text in ['دانش‌آموز', 'معلم']:
        bot.send_message(message.chat.id, "این بخش هنوز پیاده‌سازی نشده. بعداً اضافه می‌شود.")
        del user_states[message.chat.id]  # پایان
    else:
        bot.send_message(message.chat.id, "لطفاً یکی از گزینه‌ها را انتخاب کنید.")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'manager_options')
def manager_options(message):
    if message.text == 'ایجاد مدرسه جدید':
        bot.send_message(message.chat.id, "اسم کلاس‌هایی که دارید را بنویسید. مثلاً: دهم برق - دهم کامپیوتر - دهم معماری\nبا خط تیره (-) جدا کنید.")
        user_states[message.chat.id] = 'get_classes'
    elif message.text == 'مدرسه دارم':
        bot.send_message(message.chat.id, "این بخش هنوز پیاده‌سازی نشده. بعداً اضافه می‌شود.")
        del user_states[message.chat.id]
    else:
        bot.send_message(message.chat.id, "لطفاً یکی از گزینه‌ها را انتخاب کنید.")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'get_classes')
def get_classes(message):
    classes = [cls.strip() for cls in message.text.split('-')]  # جدا کردن با dash و تمیز کردن
    user_data[message.chat.id] = {'classes': classes}
    print(f"کلاس‌ها: {classes}")  # برای تست، بعداً می‌تونی به دیتابیس ذخیره کنی
    bot.send_message(message.chat.id, f"کلاس‌ها ذخیره شد: {', '.join(classes)}\nحالا اسم معلم‌ها را بفرستید. هر معلم در یک خط جدا:\nنام - نام خانوادگی - شماره تلفن - کد ملی\nمثال:\nعلی - احمدی - 09121234567 - 1234567890\nمریم - محمدی - 09351234567 - 0987654321")
    user_states[message.chat.id] = 'get_teachers'

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'get_teachers')
def get_teachers(message):
    teachers = []
    for line in message.text.split('\n'):
        if line.strip():
            parts = [part.strip() for part in line.split('-')]
            if len(parts) == 4:
                teachers.append({'name': parts[0], 'family': parts[1], 'phone': parts[2], 'national_id': parts[3]})
            else:
                bot.send_message(message.chat.id, "فرمت اشتباه! لطفاً دوباره بفرستید.")
                return
    user_data[message.chat.id]['teachers'] = teachers
    print(f"معلم‌ها: {teachers}")  # برای تست
    bot.send_message(message.chat.id, "اطلاعات معلم‌ها ذخیره شد. فرآیند ایجاد مدرسه تمام شد!")
    del user_states[message.chat.id]  # پایان

# شروع بات
bot.polling()