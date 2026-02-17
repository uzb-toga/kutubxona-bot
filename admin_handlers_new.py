from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

import db
from keyboards import admin_kb
from states import AdminLogin, AddBook, EditBook

admin_router = Router()

@admin_router.callback_query(F.data == "admin")
async def admin_login(call: CallbackQuery, state: FSMContext):
    await call.message.answer("🔑 Admin parol:")
    await state.set_state(AdminLogin.password)
    await call.answer()

@admin_router.message(AdminLogin.password)
async def admin_check(msg: Message, state: FSMContext):
    from config import ADMIN_PASSWORD
    if msg.text == ADMIN_PASSWORD:
        await db.db.execute("UPDATE users SET is_admin=TRUE WHERE telegram_id=$1", msg.from_user.id)
        await msg.answer("👑 Admin bo'ldingiz! 🎉", reply_markup=admin_kb)
        await state.clear()
    else:
        await msg.answer("❌ Noto'g'ri parol ❌")

@admin_router.callback_query(F.data == "add_book")
async def add_book(call: CallbackQuery, state: FSMContext):
    await call.message.answer("📌 Kitob kodi (yagona):")
    await state.set_state(AddBook.code)
    await call.answer()

@admin_router.message(AddBook.code)
async def ab1(msg: Message, state: FSMContext):
    await state.update_data(code=msg.text)
    await msg.answer("📖 Kitob nomi:")
    await state.set_state(AddBook.name)

@admin_router.message(AddBook.name)
async def ab2(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("✍️ Muallif ismi:")
    await state.set_state(AddBook.author)

@admin_router.message(AddBook.author)
async def ab3(msg: Message, state: FSMContext):
    await state.update_data(author=msg.text)
    await msg.answer("💰 Narx ($):")
    await state.set_state(AddBook.price)

@admin_router.message(AddBook.price)
async def ab4(msg: Message, state: FSMContext):
    try:
        data = await state.get_data()
        price = float(msg.text)
        await db.db.execute(
            "INSERT INTO books (code,name,author,price) VALUES ($1,$2,$3,$4)",
            data["code"], data["name"], data["author"], price
        )
        await msg.answer(f"✅ Kitob qo'shildi!\n📖 {data['name']}\n✍️ {data['author']}\n💰 {price}$", reply_markup=admin_kb)
        await state.clear()
    except Exception as e:
        await msg.answer(f"❌ Xato: {str(e)}")

# Admin: view all books
@admin_router.callback_query(F.data == "view_books")
async def view_books(call: CallbackQuery):
    books_list = await db.get_all_books()
    if not books_list:
        await call.message.edit_text("❌ Kitoblar topilmadi", reply_markup=admin_kb)
        await call.answer()
        return
    
    text = f"📚 Jami {len(books_list)} ta kitob\n\n"
    kb = []
    
    # Show first 30 books with edit/delete options
    for b in books_list[:30]:
        text += f"📖 {b['name']} ({b['author']}) - {b['price']}$\n"
        kb.append([
            InlineKeyboardButton(text=f"✏️ {b['name']}", callback_data=f"edit_book_{b['code']}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"delete_book_{b['code']}")
        ])
    
    kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")])
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await call.answer()

# Edit book
@admin_router.callback_query(F.data.startswith("edit_book_"))
async def edit_book_start(call: CallbackQuery, state: FSMContext):
    code = call.data.replace("edit_book_", "")
    book = await db.get_book_by_code(code)
    if not book:
        await call.answer("❌ Kitob topilmadi", show_alert=True)
        return
    
    await state.update_data(edit_code=code)
    text = f"📝 Tahrir\n\n📖 {book['name']}\n✍️ {book['author']}\n💰 {book['price']}$\n\nQanday o'zgartirmoqchi?"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Nomini o'zgartir", callback_data="edit_name")],
        [InlineKeyboardButton(text="✍️ Muallifni o'zgartir", callback_data="edit_author")],
        [InlineKeyboardButton(text="💰 Narxni o'zgartir", callback_data="edit_price")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="view_books")]
    ])
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()

@admin_router.callback_query(F.data == "edit_name")
async def edit_name_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("📖 Yangi nomni kiriting:")
    await state.set_state(EditBook.name)
    await call.answer()

@admin_router.message(EditBook.name)
async def edit_name_save(msg: Message, state: FSMContext):
    data = await state.get_data()
    code = data['edit_code']
    book = await db.get_book_by_code(code)
    await db.update_book(code, msg.text, book['author'], book['price'])
    await msg.answer(f"✅ Nomi o'zgartirildi: {msg.text}", reply_markup=admin_kb)
    await state.clear()

@admin_router.callback_query(F.data == "edit_author")
async def edit_author_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("✍️ Yangi muallif nomini kiriting:")
    await state.set_state(EditBook.author)
    await call.answer()

@admin_router.message(EditBook.author)
async def edit_author_save(msg: Message, state: FSMContext):
    data = await state.get_data()
    code = data['edit_code']
    book = await db.get_book_by_code(code)
    await db.update_book(code, book['name'], msg.text, book['price'])
    await msg.answer(f"✅ Muallif o'zgartirildi: {msg.text}", reply_markup=admin_kb)
    await state.clear()

@admin_router.callback_query(F.data == "edit_price")
async def edit_price_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("💰 Yangi narxni kiriting ($):")
    await state.set_state(EditBook.price)
    await call.answer()

@admin_router.message(EditBook.price)
async def edit_price_save(msg: Message, state: FSMContext):
    try:
        data = await state.get_data()
        code = data['edit_code']
        book = await db.get_book_by_code(code)
        price = float(msg.text)
        await db.update_book(code, book['name'], book['author'], price)
        await msg.answer(f"✅ Narx o'zgartirildi: {price}$", reply_markup=admin_kb)
        await state.clear()
    except ValueError:
        await msg.answer("❌ Noto'g'ri narx! Raqam kiriting.")

# Delete book
@admin_router.callback_query(F.data.startswith("delete_book_"))
async def delete_book(call: CallbackQuery):
    code = call.data.replace("delete_book_", "")
    book = await db.get_book_by_code(code)
    await db.delete_book(code)
    await call.answer(f"✅ '{book['name']}' o'chirildi", show_alert=True)
    await view_books(call)

# Back button
@admin_router.callback_query(F.data == "back")
async def back_to_admin(call: CallbackQuery):
    await call.message.edit_text("👑 Admin Panel", reply_markup=admin_kb)
    await call.answer()
