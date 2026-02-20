from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from src.keyboards.inline import get_main_menu, get_user_menu, get_admin_menu
from src.services.access_service import AccessService

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, db):
    """Handle /start command"""
    user_id = message.from_user.id
    access_service = AccessService(db)
    
    # Check if user has access
    has_access = await access_service.check_access(user_id)
    
    if not has_access:
        await message.answer(
            "🔒 Доступ к боту ограничен\n\n"
            "Ваша заявка отправлена администратору.\n"
            "Ожидайте подтверждения доступа.",
            reply_markup=None
        )
        return
    
    # Show appropriate menu based on user role
    is_admin = await access_service.is_admin(user_id)
    
    if is_admin:
        await message.answer(
            "👑 Добро пожаловать, Администратор!\n\n"
            "Выберите действие:",
            reply_markup=get_admin_menu()
        )
    else:
        await message.answer(
            "👋 Добро пожаловать в бот для диеты!\n\n"
            "Здесь вы можете:\n"
            "• Добавить свои данные (вес, рост, цели)\n"
            "• Записывать силовые показатели\n"
            "• Получать рекомендации от ИИ-диетолога\n\n"
            "Выберите действие:",
            reply_markup=get_user_menu()
        )


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, db, state: FSMContext):
    """Show main menu"""
    await state.clear()
    
    user_id = callback.from_user.id
    access_service = AccessService(db)
    is_admin = await access_service.is_admin(user_id)
    
    if is_admin:
        await callback.message.edit_text(
            "👑 Главное меню администратора\n\n"
            "Выберите действие:",
            reply_markup=get_admin_menu()
        )
    else:
        await callback.message.edit_text(
            "📋 Главное меню\n\n"
            "Выберите действие:",
            reply_markup=get_user_menu()
        )
    
    await callback.answer()


@router.callback_query(F.data == "user_menu")
async def show_user_menu(callback: CallbackQuery, state: FSMContext):
    """Show user menu (for admin accessing user features)"""
    await state.clear()
    
    await callback.message.edit_text(
        "📋 Пользовательское меню\n\n"
        "Выберите действие:",
        reply_markup=get_user_menu()
    )
    
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, db, state: FSMContext):
    """Cancel current action and return to main menu"""
    await state.clear()
    
    user_id = callback.from_user.id
    access_service = AccessService(db)
    is_admin = await access_service.is_admin(user_id)
    
    if is_admin:
        await callback.message.edit_text(
            "❌ Действие отменено\n\n"
            "Выберите действие:",
            reply_markup=get_admin_menu()
        )
    else:
        await callback.message.edit_text(
            "❌ Действие отменено\n\n"
            "Выберите действие:",
            reply_markup=get_user_menu()
        )
    
    await callback.answer()