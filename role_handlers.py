from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import db

role_router = Router()

class RoleManagement(StatesGroup):
    select_user = State()
    select_role = State()
    action = State()

@role_router.callback_query(F.data == "manage_roles")
async def manage_roles(call: CallbackQuery, state: FSMContext):
    users = await db.get_all_users()
    if not users:
        await call.message.answer("❌ Foydalanuvchilar topilmadi")
        return
    
    kb = []
    for user in users[:10]:  # Show first 10 users
        kb.append([InlineKeyboardButton(
            text=f"{user['name']} ({user['telegram_id']})",
            callback_data=f"select_user_{user['telegram_id']}"
        )])
    kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")])
    
    await call.message.edit_text(
        "👥 Foydalanuvchini tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
    await state.set_state(RoleManagement.select_user)

@role_router.callback_query(F.data.startswith("select_user_"), RoleManagement.select_user)
async def select_user_for_role(call: CallbackQuery, state: FSMContext):
    user_id = int(call.data.split("_")[2])
    user_info = await db.get_user_info(user_id)
    
    current_roles = [r['name'] for r in user_info['roles']]
    roles = await db.db.fetch("SELECT name, description FROM roles")
    
    kb = []
    for role in roles:
        status = "✅" if role['name'] in current_roles else "⭕"
        kb.append([InlineKeyboardButton(
            text=f"{status} {role['name']}: {role['description']}",
            callback_data=f"toggle_role_{user_id}_{role['name']}"
        )])
    kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="manage_roles")])
    
    user = user_info['user']
    await call.message.edit_text(
        f"👤 <b>{user['name']}</b>\n"
        f"🆔 ID: {user['telegram_id']}\n"
        f"📅 Ro'yxatga olish: {user['created_at']}\n\n"
        f"Rollari: {', '.join(current_roles) if current_roles else 'Yo\'q'}\n\n"
        f"Rol qo'shish/olib tashlash:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )
    await state.update_data(selected_user_id=user_id)

@role_router.callback_query(F.data.startswith("toggle_role_"))
async def toggle_user_role(call: CallbackQuery):
    parts = call.data.split("_")
    user_id = int(parts[2])
    role_name = "_".join(parts[3:])  # Handle multi-word role names
    
    user_roles = await db.get_user_roles(user_id)
    current_role_names = [r['name'] for r in user_roles]
    
    if role_name in current_role_names:
        await db.remove_user_role(user_id, role_name)
        action = "✅ Olib tashlandi"
    else:
        success = await db.add_user_role(user_id, role_name)
        action = "✅ Qo'shildi" if success else "❌ Xato"
    
    await call.answer(f"{role_name}: {action}", show_alert=False)
    
    # Refresh the display
    user_info = await db.get_user_info(user_id)
    current_roles = [r['name'] for r in user_info['roles']]
    roles = await db.db.fetch("SELECT name, description FROM roles")
    
    kb = []
    for role in roles:
        status = "✅" if role['name'] in current_roles else "⭕"
        kb.append([InlineKeyboardButton(
            text=f"{status} {role['name']}: {role['description']}",
            callback_data=f"toggle_role_{user_id}_{role['name']}"
        )])
    kb.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="manage_roles")])
    
    user = user_info['user']
    await call.message.edit_text(
        f"👤 <b>{user['name']}</b>\n"
        f"🆔 ID: {user['telegram_id']}\n"
        f"📅 Ro'yxatga olish: {user['created_at']}\n\n"
        f"Rollari: {', '.join(current_roles) if current_roles else 'Yo\'q'}\n\n"
        f"Rol qo'shish/olib tashlash:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )

@role_router.callback_query(F.data == "view_roles")
async def view_all_roles(call: CallbackQuery):
    roles = await db.db.fetch("SELECT name, description, permissions FROM roles")
    
    text = "📋 <b>Barcha Rollari:</b>\n\n"
    for role in roles:
        text += f"<b>👤 {role['name'].upper()}</b>\n"
        text += f"   📝 {role['description']}\n"
        text += f"   🔑 Ruxsatlar: {role['permissions']}\n\n"
    
    kb = [[InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")]]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="HTML")
