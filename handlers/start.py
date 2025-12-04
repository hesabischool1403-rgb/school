from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.states import AdminStates
from keyboards.reply import get_role_keyboard, get_manager_menu

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "سلام! شما مدیر هستید، معلم یا دانش‌آموز؟",
        reply_markup=get_role_keyboard()
    )
    await state.set_state(AdminStates.selecting_role)

@router.message(AdminStates.selecting_role)
async def select_role(message: Message, state: FSMContext):
    if message.text == "مدیر":
        await message.answer("خوش آمدید مدیر!", reply_markup=get_manager_menu())
        await state.set_state(AdminStates.manager_menu)
    else:
        await message.answer("این بخش هنوز فعال نیست.")
        await state.clear()