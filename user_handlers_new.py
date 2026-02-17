from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import db
from keyboards import main_menu
from states import Register, Search

user_router = Router()

@user_router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    user = await db.db.fetchrow("SELECT * FROM users WHERE telegram_id=$1", msg.from_user.id)
    if not user:
        await msg.answer("👤 Ismingizni kiriting:")
        await state.set_state(Register.name)
    else:
        await msg.answer("📚 Kutubxona botiga xush kelibsiz! 🎉", reply_markup=main_menu(await db.check_admin(msg.from_user.id)))

@user_router.message(Register.name)
async def reg(msg: Message, state: FSMContext):
    await db.db.execute(
        "INSERT INTO users (telegram_id, name) VALUES ($1,$2)",
        msg.from_user.id, msg.text
    )
    user = await db.db.fetchrow("SELECT telegram_id,name,is_admin,created_at FROM users WHERE telegram_id=$1", msg.from_user.id)
    admin_status = "✅ Ha" if user['is_admin'] else "❌ Yo'q"
    info = (
        f"✅ Ro'yxatdan o'tdingiz!\n\n"
        f"👤 Ism: {user['name']}\n"
        f"🆔 ID: {user['telegram_id']}\n"
        f"👑 Admin: {admin_status}\n"
        f"📅 Ro'yxatga olish: {user['created_at'].strftime('%Y-%m-%d %H:%M')}"
    )
    await msg.answer(info, reply_markup=main_menu(await db.check_admin(msg.from_user.id)))
    await state.clear()


@user_router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    user = await db.db.fetchrow("SELECT telegram_id,name,is_admin,created_at FROM users WHERE telegram_id=$1", call.from_user.id)
    if not user:
        await call.message.answer("❌ Siz ro'yxatdan o'tmagansiz. /start bilan ro'yxatdan o'ting.")
        await call.answer()
        return
    cart_count = await db.db.fetchval("SELECT COUNT(*) FROM cart WHERE user_id=$1", call.from_user.id)
    admin_status = "✅ Ha" if user['is_admin'] else "❌ Yo'q"
    info = (
        f"👤 Sizning profil\n\n"
        f"Ism: {user['name']}\n"
        f"ID: {user['telegram_id']}\n"
        f"Admin: {admin_status}\n"
        f"🛒 Savat: {cart_count} ta\n"
        f"Ro'yxatga olish: {user['created_at'].strftime('%Y-%m-%d %H:%M')}"
    )
    await call.message.edit_text(info, reply_markup=main_menu(await db.check_admin(call.from_user.id)))
    await call.answer()

@user_router.callback_query(F.data == "books")
async def books(call: CallbackQuery):
    books_list = await db.db.fetch("SELECT code, name, author, price FROM books ORDER BY created_at DESC LIMIT 50")
    if not books_list:
        await call.message.edit_text("❌ Kitoblar topilmadi")
        return
    kb = [[InlineKeyboardButton(text=f"📖 {b['name']}", callback_data=f"book_{b['code']}" )] for b in books_list]
    kb.append([InlineKeyboardButton(text="🔎 Qidirish", callback_data="search")])
    kb.append([InlineKeyboardButton(text="📖 Barcha kitoblar", callback_data="all_books")])
    kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")])
    await call.message.edit_text("📚 Kitoblar (Oxirgi 50):", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@user_router.callback_query(F.data == "all_books")
async def all_books(call: CallbackQuery):
    books_list = await db.get_all_books()
    if not books_list:
        await call.message.edit_text("❌ Kitoblar topilmadi")
        return
    text = f"📚 Jami {len(books_list)} ta kitob bor\n\n"
    text += "Kitob ko'rish uchun \"Qidirish\" ishlatib ko'ring yoki oldingi menyudan tanlang."
    kb = [
        [InlineKeyboardButton(text="🔎 Qidirish", callback_data="search")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="books")]
    ]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@user_router.callback_query(F.data.startswith("book_"))
async def book_details(call: CallbackQuery):
    code = call.data.replace("book_", "")
    book = await db.get_book_by_code(code)
    if not book:
        await call.answer("❌ Kitob topilmadi", show_alert=True)
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Savatga qo'shish", callback_data=f"add_to_cart_{code}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="books")]
    ])
    text = f"📖 {book['name']}\n👤 Muallif: {book['author']}\n💰 Narx: {book['price']}$"
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()

@user_router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(call: CallbackQuery):
    code = call.data.replace("add_to_cart_", "")

    book = await db.get_book_by_code(code)
    if not book:
        await call.answer("❌ Kitob topilmadi", show_alert=True)
        return
    await db.add_to_cart(call.from_user.id, code)
    await call.answer(f"✅ '{book['name']}' qo'shildi! (💰 {book['price']}$)", show_alert=True)

@user_router.callback_query(F.data == "cart")
async def view_cart(call: CallbackQuery):
    cart_items = await db.get_cart(call.from_user.id)
    if not cart_items:
        await call.message.answer("🧺 Savatingiz bo'sh", reply_markup=main_menu(await db.check_admin(call.from_user.id)))
        await call.answer()
        return
    
    text = "🛒 Sizning savatingiz:\n\n"
    kb = []
    total = 0
    
    for item in cart_items:
        subtotal = item['quantity'] * item['price']
        text += f"📖 {item['name']}\n   👤 {item['author']}\n   💰 {item['price']}$ x {item['quantity']} = {subtotal}$\n\n"
        kb.append([InlineKeyboardButton(text=f"❌ {item['name']}", callback_data=f"remove_from_cart_{item['book_code']}")])
        kb.append([InlineKeyboardButton(text=f"➖ -1", callback_data=f"qty_minus_{item['book_code']}")])
        kb.append([InlineKeyboardButton(text=f"➕ +1", callback_data=f"qty_plus_{item['book_code']}")])
        total += subtotal
    
    text += f"\n{'='*40}\n💵 Jami: {total}$"
    kb.append([InlineKeyboardButton(text=f"✅ To'lov ({total}$)", callback_data="checkout")])
    kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")])
    
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await call.answer()

@user_router.callback_query(F.data.startswith("qty_minus_"))
async def qty_minus(call: CallbackQuery):
    code = call.data.replace("qty_minus_", "")
    cart_items = await db.get_cart(call.from_user.id)
    for item in cart_items:
        if item['book_code'] == code:
            new_qty = item['quantity'] - 1
            await db.update_cart_quantity(call.from_user.id, code, new_qty)
            break
    await view_cart(call)

@user_router.callback_query(F.data.startswith("qty_plus_"))
async def qty_plus(call: CallbackQuery):
    code = call.data.replace("qty_plus_", "")
    cart_items = await db.get_cart(call.from_user.id)
    for item in cart_items:
        if item['book_code'] == code:
            new_qty = item['quantity'] + 1
            await db.update_cart_quantity(call.from_user.id, code, new_qty)
            break
    await view_cart(call)

@user_router.callback_query(F.data.startswith("remove_from_cart_"))
async def remove_from_cart(call: CallbackQuery):
    code = call.data.replace("remove_from_cart_", "")
    await db.remove_from_cart(call.from_user.id, code)
    await call.answer("❌ Savatdan o'chirildi", show_alert=True)
    await view_cart(call)

@user_router.callback_query(F.data == "checkout")
async def checkout(call: CallbackQuery):
    cart_items = await db.get_cart(call.from_user.id)
    if not cart_items:
        await call.answer("Savat bo'sh", show_alert=True)
        return
    
    total = sum(item['quantity'] * item['price'] for item in cart_items)
    await db.create_order(call.from_user.id, total)
    await db.clear_cart(call.from_user.id)
    
    text = f"✅ Buyurtma qabul qilindi!\n\n"
    text += f"📦 Jami: {len(cart_items)} ta kitob\n"
    text += f"💵 Narx: {total}$\n\n"
    text += "Tez orada bilan aloqaga chiqamiz! 📞"
    
    kb = [[InlineKeyboardButton(text="🏠 Bosh menyuga", callback_data="back")]]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await call.answer("✅ Checkout tugallandi!", show_alert=True)

@user_router.callback_query(F.data == "search")
async def search_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("🔎 Qidiruv so'rovini kiriting (nomi yoki muallifni):")
    await state.set_state(Search.query)
    await call.answer()

@user_router.message(Search.query)
async def search_query(msg: Message, state: FSMContext):
    q = msg.text
    books_list = await db.search_books(q)
    if not books_list:
        await msg.answer("❌ Hech qanday natija topilmadi", reply_markup=main_menu(await db.check_admin(msg.from_user.id)))
    else:
        text = f"🔍 '{q}' bo'yicha {len(books_list)} ta natija:\n\n"
        kb = []
        for b in books_list[:30]:  # Limit to 30 results
            text += f"📖 {b['name']} - {b['price']}$\n"
            kb.append([InlineKeyboardButton(text=f"🛒 {b['name']}", callback_data=f"book_{b['code']}")])
        kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")])
        await msg.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.clear()

@user_router.callback_query(F.data == "back")
async def back_to_menu(call: CallbackQuery):
    await call.message.edit_text("📚 Kutubxona botiga xush kelibsiz! 🎉", reply_markup=main_menu(await db.check_admin(call.from_user.id)))
    await call.answer()
