from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    selecting_role = State()
    manager_menu = State()
    creating_school = State()
    entering_classes = State()
    entering_teachers = State()