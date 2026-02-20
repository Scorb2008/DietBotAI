from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu() -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👤 Мои данные", callback_data="my_data")
    )
    builder.row(
        InlineKeyboardButton(text="🤖 ИИ-Диетолог", callback_data="diet_ai")
    )
    
    return builder.as_markup()


def get_user_menu() -> InlineKeyboardMarkup:
    """Get user menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👤 Мои данные", callback_data="my_data")
    )
    builder.row(
        InlineKeyboardButton(text="🤖 ИИ-Диетолог", callback_data="diet_ai")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_admin_menu() -> InlineKeyboardMarkup:
    """Get admin menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📋 Заявки на доступ", callback_data="pending_users")
    )
    builder.row(
        InlineKeyboardButton(text="👥 Все пользователи", callback_data="all_users")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Пользовательское меню", callback_data="user_menu")
    )
    
    return builder.as_markup()


def get_pending_users_keyboard(users: list) -> InlineKeyboardMarkup:
    """Get keyboard with pending users"""
    builder = InlineKeyboardBuilder()
    
    for user in users:
        username = f"@{user['username']}" if user.get('username') else f"ID: {user['user_id']}"
        builder.row(
            InlineKeyboardButton(
                text=f"👤 {username}",
                callback_data=f"user_{user['user_id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")
    )
    
    return builder.as_markup()


def get_user_action_keyboard(user_id: int, has_access: bool) -> InlineKeyboardMarkup:
    """Get keyboard with user actions"""
    builder = InlineKeyboardBuilder()
    
    if has_access:
        builder.row(
            InlineKeyboardButton(text="🚫 Отозвать доступ", callback_data=f"revoke_{user_id}")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="✅ Разрешить доступ", callback_data=f"approve_{user_id}")
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="pending_users")
    )
    
    return builder.as_markup()


def get_user_data_menu() -> InlineKeyboardMarkup:
    """Get user data menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⚖️ Добавить вес", callback_data="add_weight"),
        InlineKeyboardButton(text="📏 Добавить рост", callback_data="add_height")
    )
    builder.row(
        InlineKeyboardButton(text="🎂 Добавить возраст", callback_data="add_age"),
        InlineKeyboardButton(text="🎯 Добавить цель", callback_data="add_goal")
    )
    builder.row(
        InlineKeyboardButton(text="🎯 Целевой вес", callback_data="add_target_weight")
    )
    builder.row(
        InlineKeyboardButton(text="💪 Добавить тренировку", callback_data="add_workout")
    )
    builder.row(
        InlineKeyboardButton(text="📜 История тренировок", callback_data="view_workouts")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_diet_ai_menu(can_ask: bool = True) -> InlineKeyboardMarkup:
    """Get diet AI menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    if can_ask:
        builder.row(
            InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_ai")
        )
    
    builder.row(
        InlineKeyboardButton(text="📜 История запросов", callback_data="ai_history")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()