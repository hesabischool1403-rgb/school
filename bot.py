import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, ContextTypes
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# اتصال به گوگل شیت
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
client = gspread.authorize(creds)
sheet = client.open("school_database")

# شیت‌ها
admins_sheet = sheet.worksheet("مدیران")
teachers_sheet = sheet.worksheet("معلمان")
students_sheet = sheet.worksheet("دانشآموزان")
classes_sheet = sheet.worksheet("کلاسها")
attendance_sheet = sheet.worksheet("حضور_غیاب")
grades_sheet = sheet.worksheet("نمرات")

# توکن بات (از BotFather)
TOKEN = "8397695569:AAHS2Nyd1KXnPS0p4RsuETa53PUmvfoQSjE"  # اینجا توکن خودت رو بذار

# منوی اصلی
def main_menu(role):
    if role == "admin":
        keyboard = [
            [InlineKeyboardButton("کلاس جدید", callback_data="admin_newclass")],
            [InlineKeyboardButton("اضافه کردن دانش‌آموز", callback_data="admin_addstudent")],
            [InlineKeyboardButton("لیست کلاس‌ها", callback_data="admin_classes")]
        ]
    elif role == "teacher":
        keyboard = [
            [InlineKeyboardButton("حضور و غیاب", callback_data="teacher_attendance")],
            [InlineKeyboardButton("نمره‌دهی", callback_data="teacher_grade")],
            [InlineKeyboardButton("کارنامه کلاس", callback_data="teacher_report")]
        ]
    elif role == "student":
        keyboard = [[InlineKeyboardButton("کارنامه من", callback_data="student_report")]]
    else:
        keyboard = []
    return InlineKeyboardMarkup(keyboard)

# بررسی نقش کاربر
def get_role(user_id):
    if str(user_id) in admins_sheet.col_values(1): return "admin"
    if str(user_id) in teachers_sheet.col_values(1): return "teacher"
    if str(user_id) in students_sheet.col_values(1): return "student"
    return None

# استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    role = get_role(user.id)
    
    if not role:
        await update.message.reply_text("شما دسترسی ندارید!")
        return
    
    await update.message.reply_text(
        f"سلام {user.first_name}!\nنقش شما: {role}",
        reply_markup=main_menu(role)
    )

# --- مدیر ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_newclass":
        await query.edit_message_text("نام کلاس را بفرستید:")
        context.user_data['action'] = 'newclass_name'
    
    elif query.data == "admin_addstudent":
        await query.edit_message_text("نام، کلاس و آی‌دی والدین را بفرستید:\nمثال: علی,دهم,123456789")
        context.user_data['action'] = 'addstudent'

# --- معلم ---
async def teacher_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "teacher_attendance":
        # لیست دانش‌آموزان کلاس
        teacher_row = teachers_sheet.find(str(query.from_user.id))
        class_name = teachers_sheet.cell(teacher_row.row, 4).value
        students = students_sheet.get_all_records()
        students_in_class = [s for s in students if s['class'] == class_name]
        
        keyboard = []
        for s in students_in_class:
            keyboard.append([InlineKeyboardButton(f"{s['name']}", callback_data=f"attend_{s['user_id']}")])
        await query.edit_message_text("حضور و غیاب:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- دانش‌آموز ---
async def student_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    student = students_sheet.find(str(query.from_user.id))
    if not student:
        await query.edit_message_text("شما ثبت نشده‌اید!")
        return
    
    grades = [g for g in grades_sheet.get_all_records() if g['student_id'] == str(query.from_user.id)]
    text = "کارنامه شما:\n\n"
    for g in grades:
        text += f"{g['subject']}: {g['score']}\n"
    
    await query.edit_message_text(text or "نمره‌ای ثبت نشده!")

# هندلر دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith("admin_"):
        await admin_panel(update, context)
    elif data.startswith("teacher_"):
        await teacher_panel(update, context)
    elif data.startswith("student_"):
        await student_report(update, context)

# هندلر پیام متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    action = context.user_data.get('action')
    
    if action == 'newclass_name':
        classes_sheet.append_row([text, ""])
        await update.message.reply_text(f"کلاس {text} ساخته شد!")
        context.user_data['action'] = None
    
    elif action == 'addstudent':
        try:
            name, class_name, parent_id = text.split(',')
            students_sheet.append_row([update.message.from_user.id, update.message.from_user.username, name.strip(), class_name.strip(), parent_id.strip()])
            await update.message.reply_text("دانش‌آموز اضافه شد!")
        except:
            await update.message.reply_text("فرمت اشتباه! مثال: علی,دهم,123456789")
        context.user_data['action'] = None

# راه‌اندازی
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("بات در حال اجراست...")
app.run_polling()