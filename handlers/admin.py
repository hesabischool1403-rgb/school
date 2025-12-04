from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.states import AdminStates
from database import init_db
import aiosqlite

router = Router()

@router.message(AdminStates.manager_menu, F.text == "ایجاد مدرسه جدید")
async def create_school_start(message: Message, state: FSMContext):
    await message.answer("اسم کلاس‌ها رو با خط تیره (-) جدا کنید:\nمثال: دهم برق - دهم کامپیوتر - یازدهم معماری")
    await state.set_state(AdminStates.entering_classes)

@router.message(AdminStates.entering_classes)
async def get_classes(message: Message, state: FSMContext):
    classes = [c.strip() for c in message.text.split("-") if c.strip()]
    await state.update_data(classes=classes)

    await message.answer(
        "کلاس‌ها ذخیره شد!\n"
        "حالا معلم‌ها رو بفرستید. هر معلم در یک خط:\n"
        "نام - نام خانوادگی - شماره تلفن - کد ملی\n"
        "مثال:\n"
        "علی - احمدی - 09121234567 - 1234567890"
    )
    await state.set_state(AdminStates.entering_teachers)

@router.message(AdminStates.entering_teachers)
async def get_teachers(message: Message, state: FSMContext):
    teachers = []
    for line in message.text.strip().split("\n"):
        parts = [p.strip() for p in line.split("-")]
        if len(parts) == 4:
            teachers.append({
                "first_name": parts[0],
                "last_name": parts[1],
                "phone": parts[2],
                "national_id": parts[3]
            })

    data = await state.get_data()
    classes = data.get("classes", [])

    # ذخیره در دیتابیس
    async with aiosqlite.connect("school.db") as db:
        await db.execute("INSERT INTO schools (admin_id, name) VALUES (?, ?)",
                        (message.from_user.id, "مدرسه جدید"))
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        school_id = (await cursor.fetchone())[0]

        for cls in classes:
            await db.execute("INSERT INTO classes (school_id, name) VALUES (?, ?)", (school_id, cls))
        for t in teachers:
            await db.execute("INSERT INTO teachers (school_id, first_name, last_name, phone, national_id) VALUES (?, ?, ?, ?, ?)",
                           (school_id, t["first_name"], t["last_name"], t["phone"], t["national_id"]))
        await db.commit()

    await message.answer("مدرسه با موفقیت ایجاد شد! می‌تونید بعداً دانش‌آموز اضافه کنید.")
    await state.clear()