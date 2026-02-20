from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.keyboards.inline import get_user_menu, get_diet_ai_menu
from src.services.access_service import AccessService
from src.services.mistral_service import MistralService
from src.config.settings import settings

router = Router()


class DietAIStates(StatesGroup):
    """Diet AI FSM states"""
    waiting_for_question = State()


@router.callback_query(F.data == "diet_ai")
async def show_diet_ai_menu(callback: CallbackQuery, db):
    """Show diet AI menu"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify access
    if not await access_service.check_access(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Get user's AI request count
    request_count = await db.get_ai_request_count(user_id)
    remaining = settings.MAX_REQUESTS_PER_USER - request_count
    
    text = "🤖 ИИ-Диетолог\n\n"
    text += "Задайте вопрос нашему ИИ-диетологу на базе Mistral AI.\n\n"
    text += f"📊 Использовано запросов: {request_count}/{settings.MAX_REQUESTS_PER_USER}\n"
    text += f"✅ Осталось запросов: {remaining}\n\n"
    
    if remaining > 0:
        text += "Нажмите кнопку ниже, чтобы задать вопрос."
    else:
        text += "⚠️ Вы исчерпали лимит запросов."
    
    await callback.message.edit_text(text, reply_markup=get_diet_ai_menu(remaining > 0))
    await callback.answer()


@router.callback_query(F.data == "ask_ai")
async def ask_ai_start(callback: CallbackQuery, state: FSMContext, db):
    """Start asking AI"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify access
    if not await access_service.check_access(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Check request limit
    request_count = await db.get_ai_request_count(user_id)
    if request_count >= settings.MAX_REQUESTS_PER_USER:
        await callback.answer("❌ Вы исчерпали лимит запросов", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🤖 Задайте ваш вопрос ИИ-диетологу:\n\n"
        "Например:\n"
        "• Какой рацион мне подходит для набора массы?\n"
        "• Сколько калорий мне нужно потреблять?\n"
        "• Какие продукты лучше есть перед тренировкой?\n\n"
        "Напишите ваш вопрос:",
        reply_markup=None
    )
    await state.set_state(DietAIStates.waiting_for_question)
    await callback.answer()


@router.message(DietAIStates.waiting_for_question)
async def ask_ai_finish(message: Message, state: FSMContext, db):
    """Process AI question"""
    user_id = message.from_user.id
    question = message.text.strip()
    
    # Validate question length
    if len(question) < 10:
        await message.answer(
            "❌ Вопрос слишком короткий.\n"
            "Пожалуйста, опишите ваш вопрос подробнее (минимум 10 символов):"
        )
        return
    
    if len(question) > 1000:
        await message.answer(
            "❌ Вопрос слишком длинный.\n"
            "Пожалуйста, сократите ваш вопрос (максимум 1000 символов):"
        )
        return
    
    # Check request limit again
    request_count = await db.get_ai_request_count(user_id)
    if request_count >= settings.MAX_REQUESTS_PER_USER:
        await message.answer(
            "❌ Вы исчерпали лимит запросов",
            reply_markup=get_user_menu()
        )
        await state.clear()
        return
    
    # Show processing message
    processing_msg = await message.answer("⏳ Обрабатываю ваш запрос...")
    
    try:
        # Get user data for context
        user_data = await db.get_user_data(user_id)
        
        # Initialize Mistral service
        mistral_service = MistralService()
        
        # Get AI response
        response = await mistral_service.get_diet_advice(question, user_data)
        
        # Increment request count
        await db.increment_ai_request_count(user_id)
        
        # Get updated count
        new_count = await db.get_ai_request_count(user_id)
        remaining = settings.MAX_REQUESTS_PER_USER - new_count
        
        # Delete processing message
        await processing_msg.delete()
        
        # Send response
        response_text = f"🤖 Ответ ИИ-диетолога:\n\n{response}\n\n"
        response_text += f"📊 Осталось запросов: {remaining}/{settings.MAX_REQUESTS_PER_USER}"
        
        await message.answer(
            response_text,
            reply_markup=get_diet_ai_menu(remaining > 0)
        )
        
        await state.clear()
        
    except Exception as e:
        # Delete processing message
        await processing_msg.delete()
        
        await message.answer(
            f"❌ Ошибка при обработке запроса:\n{str(e)}\n\n"
            "Попробуйте еще раз позже.",
            reply_markup=get_user_menu()
        )
        await state.clear()


@router.callback_query(F.data == "ai_history")
async def show_ai_history(callback: CallbackQuery, db):
    """Show AI request history"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify access
    if not await access_service.check_access(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Get AI request history
    history = await db.get_ai_history(user_id, limit=5)
    
    if not history:
        text = "📜 История запросов к ИИ\n\n"
        text += "У вас еще нет запросов к ИИ-диетологу."
    else:
        text = "📜 История запросов к ИИ\n\n"
        text += f"Последние {len(history)} запросов:\n\n"
        
        for i, record in enumerate(history, 1):
            date = record['created_at'].split()[0]
            question = record['question'][:50] + "..." if len(record['question']) > 50 else record['question']
            text += f"{i}. {date}\n❓ {question}\n\n"
    
    # Get request count
    request_count = await db.get_ai_request_count(user_id)
    remaining = settings.MAX_REQUESTS_PER_USER - request_count
    
    text += f"\n📊 Всего запросов: {request_count}/{settings.MAX_REQUESTS_PER_USER}\n"
    text += f"✅ Осталось: {remaining}"
    
    await callback.message.edit_text(text, reply_markup=get_diet_ai_menu(remaining > 0))
    await callback.answer()