from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.keyboards.inline import get_admin_menu, get_pending_users_keyboard, get_user_action_keyboard
from src.services.access_service import AccessService

router = Router()


class AdminStates(StatesGroup):
    """Admin FSM states"""
    waiting_for_user_id = State()


@router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery, db):
    """Show admin panel"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify admin access
    if not await access_service.is_admin(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👑 Панель администратора\n\n"
        "Выберите действие:",
        reply_markup=get_admin_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "pending_users")
async def show_pending_users(callback: CallbackQuery, db):
    """Show list of users waiting for access"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify admin access
    if not await access_service.is_admin(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Get pending users
    pending = await access_service.get_pending_users()
    
    if not pending:
        await callback.message.edit_text(
            "📋 Заявки на доступ\n\n"
            "Нет ожидающих заявок",
            reply_markup=get_admin_menu()
        )
        await callback.answer()
        return
    
    keyboard = get_pending_users_keyboard(pending)
    
    text = "📋 Заявки на доступ\n\n"
    text += f"Всего заявок: {len(pending)}\n\n"
    text += "Выберите пользователя для управления:"
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("user_"))
async def show_user_actions(callback: CallbackQuery, db):
    """Show actions for specific user"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify admin access
    if not await access_service.is_admin(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Extract target user ID
    target_user_id = int(callback.data.split("_")[1])
    
    # Get user info
    user_info = await access_service.get_user_info(target_user_id)
    
    if not user_info:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    status_emoji = "✅" if user_info['has_access'] else "⏳"
    status_text = "Доступ разрешен" if user_info['has_access'] else "Ожидает доступа"
    
    text = f"👤 Информация о пользователе\n\n"
    text += f"ID: {target_user_id}\n"
    text += f"Статус: {status_emoji} {status_text}\n"
    
    if user_info.get('username'):
        text += f"Username: @{user_info['username']}\n"
    
    text += f"\nВыберите действие:"
    
    keyboard = get_user_action_keyboard(target_user_id, user_info['has_access'])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: CallbackQuery, db):
    """Approve user access"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify admin access
    if not await access_service.is_admin(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Extract target user ID
    target_user_id = int(callback.data.split("_")[1])
    
    # Grant access
    success = await access_service.grant_access(target_user_id)
    
    if success:
        await callback.answer("✅ Доступ разрешен", show_alert=True)
        
        # Try to notify user
        try:
            bot = callback.bot
            await bot.send_message(
                target_user_id,
                "🎉 Ваша заявка одобрена!\n\n"
                "Теперь вы можете пользоваться ботом.\n"
                "Нажмите /start для начала работы."
            )
        except Exception:
            pass
        
        # Return to pending users list
        await show_pending_users(callback, db)
    else:
        await callback.answer("❌ Ошибка при выдаче доступа", show_alert=True)


@router.callback_query(F.data.startswith("revoke_"))
async def revoke_user(callback: CallbackQuery, db):
    """Revoke user access"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify admin access
    if not await access_service.is_admin(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Extract target user ID
    target_user_id = int(callback.data.split("_")[1])
    
    # Revoke access
    success = await access_service.revoke_access(target_user_id)
    
    if success:
        await callback.answer("🚫 Доступ отозван", show_alert=True)
        
        # Try to notify user
        try:
            bot = callback.bot
            await bot.send_message(
                target_user_id,
                "🔒 Ваш доступ к боту был отозван администратором."
            )
        except Exception:
            pass
        
        # Return to admin panel
        await show_admin_panel(callback, db)
    else:
        await callback.answer("❌ Ошибка при отзыве доступа", show_alert=True)


@router.callback_query(F.data == "all_users")
async def show_all_users(callback: CallbackQuery, db):
    """Show all users with access"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify admin access
    if not await access_service.is_admin(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Get all users with access
    users = await access_service.get_all_users()
    
    if not users:
        await callback.message.edit_text(
            "👥 Все пользователи\n\n"
            "Нет пользователей с доступом",
            reply_markup=get_admin_menu()
        )
        await callback.answer()
        return
    
    text = "👥 Все пользователи с доступом\n\n"
    text += f"Всего пользователей: {len(users)}\n\n"
    
    for user in users[:10]:  # Show first 10 users
        username = f"@{user['username']}" if user.get('username') else "Без username"
        text += f"• ID: {user['user_id']} - {username}\n"
    
    if len(users) > 10:
        text += f"\n... и еще {len(users) - 10} пользователей"
    
    await callback.message.edit_text(text, reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery, db):
    """Show bot statistics"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify admin access
    if not await access_service.is_admin(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Get statistics
    stats = await access_service.get_stats()
    
    text = "📊 Статистика бота\n\n"
    text += f"👥 Всего пользователей: {stats['total_users']}\n"
    text += f"✅ С доступом: {stats['approved_users']}\n"
    text += f"⏳ Ожидают доступа: {stats['pending_users']}\n"
    text += f"🤖 Всего запросов к ИИ: {stats['total_ai_requests']}\n"
    
    await callback.message.edit_text(text, reply_markup=get_admin_menu())
    await callback.answer()