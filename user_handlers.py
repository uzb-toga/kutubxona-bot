from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError

import db
from keyboards import main_menu
from states import Register, Search

user_router = Router()

@user_router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    user = await db.db.fetchrow("SELECT * FROM users WHERE telegram_id=$1", msg.from_user.id)
    if not user:
        try:
            await msg.answer("👤 Ismingizni kiriting:")
        except TelegramForbiddenError:
            return
        await state.set_state(Register.name)
    else:
        try:
            await msg.answer("📚 Kutubxona botiga xush kelibsiz!", reply_markup=main_menu(await db.check_admin(msg.from_user.id)))
        except TelegramForbiddenError:
            return

@user_router.message(Register.name)
async def reg(msg: Message, state: FSMContext):
    await db.db.execute(
        "INSERT INTO users (telegram_id, name) VALUES ($1,$2)",
        msg.from_user.id, msg.text
    )
    user = await db.db.fetchrow("SELECT telegram_id,name,is_admin,created_at FROM users WHERE telegram_id=$1", msg.from_user.id)
    info = (
        f"✅ Ro‘yxatdan o‘tdingiz\n\n"
        f"👤 Ism: {user['name']}\n"
        f"🆔 ID: {user['telegram_id']}\n"
        f"👑 Admin: {'Ha' if user['is_admin'] else 'Yo‘q'}\n"
        f"📅 Ro‘yxatga olish: {user['created_at']}"
    )
    try:
        await msg.answer(info, reply_markup=main_menu(await db.check_admin(msg.from_user.id)))
    except TelegramForbiddenError:
        return
    await state.clear()


@user_router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    user = await db.db.fetchrow("SELECT telegram_id,name,is_admin,created_at FROM users WHERE telegram_id=$1", call.from_user.id)
    if not user:
        try:
            await call.message.answer("❌ Siz ro‘yxatdan o‘tmagansiz. /start bilan ro‘yxatdan o‘ting.")
        except TelegramForbiddenError:
            await call.answer()
            return
        await call.answer()
        return
    info = (
        f"👤 Sizning profil\n\n"
        f"Ism: {user['name']}\n"
        f"ID: {user['telegram_id']}\n"
        f"Admin: {'Ha' if user['is_admin'] else 'Yo‘q'}\n"
        f"Ro‘yxatga olish: {user['created_at']}"
    )
    try:
        await call.message.edit_text(info, reply_markup=main_menu(await db.check_admin(call.from_user.id)))
        await call.answer()
    except TelegramForbiddenError:
        return

@user_router.callback_query(F.data == "books")
async def books(call: CallbackQuery):
    books = await db.db.fetch("SELECT code,name FROM books ORDER BY created_at DESC")
    kb = [[InlineKeyboardButton(text=b["name"], callback_data=f"book_{b['code']}" )] for b in books]
    kb.append([InlineKeyboardButton(text="🔎 Qidirish", callback_data="search")])
    kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")])
    try:
        await call.message.edit_text("📚 Kitoblar:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    except TelegramForbiddenError:
        return

@user_router.callback_query(F.data.startswith("book_"))
async def book_details(call: CallbackQuery):
    code = call.data.replace("book_", "")
    book = await db.get_book_by_code(code)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Savatga qo‘shish", callback_data=f"add_to_cart_{code}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="books")]
    ])
    try:
        await call.message.edit_text(f"📖 {book['name']}\n👤 {book['author']}\n💰 {book['price']}$", reply_markup=kb)
    except TelegramForbiddenError:
        return

@user_router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(call: CallbackQuery, state: FSMContext):
    code = call.data.replace("add_to_cart_", "")
    book = await db.get_book_by_code(code)
    cart = (await state.get_data()).get("cart", [])
    cart.append(code)
    await state.update_data(cart=cart)
    try:
        await call.answer(f"✅ {book['name']} qo‘shildi ({book['price']}$)", show_alert=True)
    except TelegramForbiddenError:
        return

@user_router.callback_query(F.data == "cart")
async def view_cart(call: CallbackQuery, state: FSMContext):
    cart = (await state.get_data()).get("cart", [])
    if not cart:
        try:
            await call.message.answer("🧺 Savatingiz bo'sh", reply_markup=main_menu(await db.check_admin(call.from_user.id)))
            await call.answer()
        except TelegramForbiddenError:
            return
        return
    books = await db.get_books_by_codes(cart)
    text = "🛒 Savat:\n"
    kb_rows = []
    total = 0
    for b in books:
        text += f"{b['name']} — {b['price']}$\n"
        kb_rows.append([InlineKeyboardButton(text=f"❌ {b['name']}", callback_data=f"remove_{b['code']}")])
        total += float(b['price'])
    kb_rows.append([InlineKeyboardButton(text=f"✅ To'lov ({total}$)", callback_data="checkout")])
    kb_rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")])
    try:
        await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    except TelegramForbiddenError:
        return

@user_router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(call: CallbackQuery, state: FSMContext):
    code = call.data.replace("remove_", "")
    data = await state.get_data()
    cart = data.get("cart", [])
    if code in cart:
        cart.remove(code)
    await state.update_data(cart=cart)
    try:
        await call.answer("❌ O'chirildi", show_alert=True)
    except TelegramForbiddenError:
        return
    await view_cart(call, state)

@user_router.callback_query(F.data == "checkout")
async def checkout(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])
    if not cart:
        try:
            await call.answer("Savat bo'sh", show_alert=True)
        except TelegramForbiddenError:
            return
        return
    books = await db.get_books_by_codes(cart)
    total = sum(float(b['price']) for b in books)
    await db.create_order(call.from_user.id, total, cart)
    await state.update_data(cart=[])
    try:
        await call.answer(f"✅ Buyurtma qabul qilindi. Jami: {total}$", show_alert=True)
        await call.message.edit_text("✅ Buyurtma yakunlandi. Rahmat!")
    except TelegramForbiddenError:
        return

@user_router.callback_query(F.data == "search")
async def search_start(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.answer("🔎 Qidiruv so'rovini kiriting:")
    except TelegramForbiddenError:
        return
    await state.set_state(Search.query)

@user_router.message(Search.query)
async def search_query(msg: Message, state: FSMContext):
    q = msg.text
    books = await db.search_books(q)
    if not books:
        try:
            await msg.answer("❌ Natija topilmadi")
        except TelegramForbiddenError:
            return
    else:
        kb = [[InlineKeyboardButton(text=b['name'], callback_data=f"book_{b['code']}")] for b in books]
        kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")])
        try:
            await msg.answer("🔎 Natijalar:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        except TelegramForbiddenError:
            return
    await state.clear()
