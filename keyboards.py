from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu(is_admin=False):
    kb = [
        [InlineKeyboardButton(text="📚 Kitoblar", callback_data="books")],
        [InlineKeyboardButton(text="🔍 Qidirish", callback_data="search")],
        [InlineKeyboardButton(text="🛒 Savat", callback_data="cart")],
        [InlineKeyboardButton(text="👤 Profil", callback_data="profile")]
    ]
    kb.append([
        InlineKeyboardButton(
            text="👑 Admin Panel" if is_admin else "👑 Admin",
            callback_data="admin_panel" if is_admin else "admin"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=kb)

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Kitob qo‘shish", callback_data="add_book")],
    [InlineKeyboardButton(text="📚 Barcha kitoblar", callback_data="view_books")],
    [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")]
])
