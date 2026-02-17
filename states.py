from aiogram.fsm.state import StatesGroup, State

class Register(StatesGroup):
    name = State()

class AdminLogin(StatesGroup):
    password = State()

class AddBook(StatesGroup):
    code = State()
    name = State()
    author = State()
    price = State()

class EditBook(StatesGroup):
    name = State()
    author = State()
    price = State()

class Search(StatesGroup):
    query = State()
