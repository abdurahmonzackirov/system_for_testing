from aiogram.fsm.state import State, StatesGroup

class Reg(StatesGroup):
    name = State()
    phone_number = State()