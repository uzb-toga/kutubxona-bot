from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

import db
from keyboards import admin_kb
from states import AdminLogin, AddBook

admin_router = Router()

@admin_router.callback_query(F.data == "admin")
async def admin_login(call: CallbackQuery, state: FSMContext):
    await call.message.answer("🔑 Admin parol:")
    await state.set_state(AdminLogin.password)

@admin_router.message(AdminLogin.password)
async def admin_check(msg: Message, state: FSMContext):
    from config import ADMIN_PASSWORD
    if msg.text == ADMIN_PASSWORD:
        await db.db.execute("UPDATE users SET is_admin=TRUE WHERE telegram_id=$1", msg.from_user.id)
        await msg.answer("👑 Admin bo‘ldingiz", reply_markup=admin_kb)
        await state.clear()
    else:
        await msg.answer("❌ Noto‘g‘ri parol")

@admin_router.callback_query(F.data == "add_book")
async def add_book(call: CallbackQuery, state: FSMContext):
    await call.message.answer("📌 Kod:")
    await state.set_state(AddBook.code)

@admin_router.message(AddBook.code)
async def ab1(msg: Message, state: FSMContext):
    await state.update_data(code=msg.text)
    await msg.answer("📖 Nomi:")
    await state.set_state(AddBook.name)

@admin_router.message(AddBook.name)
async def ab2(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("✍️ Muallif:")
    await state.set_state(AddBook.author)

@admin_router.message(AddBook.author)
async def ab3(msg: Message, state: FSMContext):
    await state.update_data(author=msg.text)
    await msg.answer("💰 Narx:")
    await state.set_state(AddBook.price)

@admin_router.message(AddBook.price)
async def ab4(msg: Message, state: FSMContext):
    data = await state.get_data()
    await db.db.execute(
        "INSERT INTO books (code,name,author,price) VALUES ($1,$2,$3,$4)",
        data["code"], data["name"], data["author"], float(msg.text)
    )
    await msg.answer("✅ Kitob qo‘shildi", reply_markup=admin_kb)
    await state.clear()

# Admin: view all books and delete
@admin_router.callback_query(F.data == "view_books")
async def view_books(call: CallbackQuery):
    books = await db.db.fetch("SELECT code,name,author,price FROM books ORDER BY created_at DESC")
    kb = [[InlineKeyboardButton(text=f"{b['name']} — {b['price']}$", callback_data=f"delete_book_{b['code']}")] for b in books]
    kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")])
    await call.message.edit_text("📚 Barcha kitoblar:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@admin_router.callback_query(F.data.startswith("delete_book_"))
async def delete_book(call: CallbackQuery):
    code = call.data.replace("delete_book_", "")
    await db.delete_book(code)
    await call.answer("✅ O'chirildi", show_alert=True)
    await view_books(call)
@admin_router.callback_query(F.data == "admin_panel")
async def admin_panel(call: CallbackQuery):
    kb = [
        [InlineKeyboardButton(text="➕ Kitob qo'shish", callback_data="add_book")],
        [InlineKeyboardButton(text="📚 Barcha kitoblar", callback_data="view_books")],
        [InlineKeyboardButton(text="👥 Rollri boshqarish", callback_data="manage_roles")],
        [InlineKeyboardButton(text="📋 Barcha rollari", callback_data="view_roles")],
        [InlineKeyboardButton(text="👨‍💼 Foydalanuvchilar", callback_data="view_users")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")]
    ]
    await call.message.edit_text("👑 <b>Admin Panel</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="HTML")

@admin_router.callback_query(F.data == "view_users")
async def view_users(call: CallbackQuery):
    users = await db.get_all_users()
    text = "👥 <b>Barcha Foydalanuvchilar:</b>\n\n"
    for user in users[:20]:
        status = "👑" if user['is_admin'] else "👤"
        text += f"{status} {user['name']} (ID: {user['telegram_id']})\n"
    
    kb = [[InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")]]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="HTML")

@admin_router.callback_query(F.data == "back")
async def go_back(call: CallbackQuery):
    from keyboards import admin_kb
    await call.message.edit_text("👑 Admin bo'ldingiz", reply_markup=admin_kb)