from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.keyboards.inline import get_user_menu, get_user_data_menu
from src.services.access_service import AccessService

router = Router()


class UserDataStates(StatesGroup):
    """User data FSM states"""
    waiting_for_weight = State()
    waiting_for_height = State()
    waiting_for_age = State()
    waiting_for_goal = State()
    waiting_for_target_weight = State()
    waiting_for_workout_data = State()


@router.callback_query(F.data == "my_data")
async def show_user_data(callback: CallbackQuery, db):
    """Show user data menu"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify access
    if not await access_service.check_access(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Get user data
    user_data = await db.get_user_data(user_id)
    
    if not user_data:
        text = "📊 Мои данные\n\n"
        text += "У вас еще нет сохраненных данных.\n"
        text += "Добавьте информацию о себе для получения персональных рекомендаций."
    else:
        text = "📊 Мои данные\n\n"
        text += f"⚖️ Вес: {user_data.get('weight', 'не указан')} кг\n"
        text += f"📏 Рост: {user_data.get('height', 'не указан')} см\n"
        text += f"🎂 Возраст: {user_data.get('age', 'не указан')} лет\n"
        text += f"🎯 Цель: {user_data.get('goal', 'не указана')}\n"
        text += f"🎯 Целевой вес: {user_data.get('target_weight', 'не указан')} кг\n"
    
    await callback.message.edit_text(text, reply_markup=get_user_data_menu())
    await callback.answer()


@router.callback_query(F.data == "add_weight")
async def add_weight_start(callback: CallbackQuery, state: FSMContext):
    """Start adding weight"""
    await callback.message.edit_text(
        "⚖️ Введите ваш текущий вес в килограммах:\n\n"
        "Например: 75.5",
        reply_markup=None
    )
    await state.set_state(UserDataStates.waiting_for_weight)
    await callback.answer()


@router.message(UserDataStates.waiting_for_weight)
async def add_weight_finish(message: Message, state: FSMContext, db):
    """Save weight"""
    try:
        weight = float(message.text.replace(',', '.'))
        
        if weight <= 0 or weight > 300:
            await message.answer(
                "❌ Некорректное значение веса.\n"
                "Введите вес от 1 до 300 кг:"
            )
            return
        
        user_id = message.from_user.id
        await db.update_user_data(user_id, weight=weight)
        
        await message.answer(
            f"✅ Вес сохранен: {weight} кг",
            reply_markup=get_user_data_menu()
        )
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Некорректный формат.\n"
            "Введите число (например: 75.5):"
        )


@router.callback_query(F.data == "add_height")
async def add_height_start(callback: CallbackQuery, state: FSMContext):
    """Start adding height"""
    await callback.message.edit_text(
        "📏 Введите ваш рост в сантиметрах:\n\n"
        "Например: 175",
        reply_markup=None
    )
    await state.set_state(UserDataStates.waiting_for_height)
    await callback.answer()


@router.message(UserDataStates.waiting_for_height)
async def add_height_finish(message: Message, state: FSMContext, db):
    """Save height"""
    try:
        height = int(message.text)
        
        if height <= 0 or height > 250:
            await message.answer(
                "❌ Некорректное значение роста.\n"
                "Введите рост от 1 до 250 см:"
            )
            return
        
        user_id = message.from_user.id
        await db.update_user_data(user_id, height=height)
        
        await message.answer(
            f"✅ Рост сохранен: {height} см",
            reply_markup=get_user_data_menu()
        )
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Некорректный формат.\n"
            "Введите целое число (например: 175):"
        )


@router.callback_query(F.data == "add_age")
async def add_age_start(callback: CallbackQuery, state: FSMContext):
    """Start adding age"""
    await callback.message.edit_text(
        "🎂 Введите ваш возраст в годах:\n\n"
        "Например: 25",
        reply_markup=None
    )
    await state.set_state(UserDataStates.waiting_for_age)
    await callback.answer()


@router.message(UserDataStates.waiting_for_age)
async def add_age_finish(message: Message, state: FSMContext, db):
    """Save age"""
    try:
        age = int(message.text)
        
        if age <= 0 or age > 120:
            await message.answer(
                "❌ Некорректное значение возраста.\n"
                "Введите возраст от 1 до 120 лет:"
            )
            return
        
        user_id = message.from_user.id
        await db.update_user_data(user_id, age=age)
        
        await message.answer(
            f"✅ Возраст сохранен: {age} лет",
            reply_markup=get_user_data_menu()
        )
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Некорректный формат.\n"
            "Введите целое число (например: 25):"
        )


@router.callback_query(F.data == "add_goal")
async def add_goal_start(callback: CallbackQuery, state: FSMContext):
    """Start adding goal"""
    await callback.message.edit_text(
        "🎯 Введите вашу цель:\n\n"
        "Например:\n"
        "• Набрать мышечную массу\n"
        "• Похудеть\n"
        "• Поддерживать форму\n"
        "• Набрать вес",
        reply_markup=None
    )
    await state.set_state(UserDataStates.waiting_for_goal)
    await callback.answer()


@router.message(UserDataStates.waiting_for_goal)
async def add_goal_finish(message: Message, state: FSMContext, db):
    """Save goal"""
    goal = message.text.strip()
    
    if len(goal) < 3 or len(goal) > 200:
        await message.answer(
            "❌ Цель должна содержать от 3 до 200 символов.\n"
            "Попробуйте еще раз:"
        )
        return
    
    user_id = message.from_user.id
    await db.update_user_data(user_id, goal=goal)
    
    await message.answer(
        f"✅ Цель сохранена: {goal}",
        reply_markup=get_user_data_menu()
    )
    await state.clear()


@router.callback_query(F.data == "add_target_weight")
async def add_target_weight_start(callback: CallbackQuery, state: FSMContext):
    """Start adding target weight"""
    await callback.message.edit_text(
        "🎯 Введите ваш целевой вес в килограммах:\n\n"
        "Например: 80",
        reply_markup=None
    )
    await state.set_state(UserDataStates.waiting_for_target_weight)
    await callback.answer()


@router.message(UserDataStates.waiting_for_target_weight)
async def add_target_weight_finish(message: Message, state: FSMContext, db):
    """Save target weight"""
    try:
        target_weight = float(message.text.replace(',', '.'))
        
        if target_weight <= 0 or target_weight > 300:
            await message.answer(
                "❌ Некорректное значение целевого веса.\n"
                "Введите вес от 1 до 300 кг:"
            )
            return
        
        user_id = message.from_user.id
        await db.update_user_data(user_id, target_weight=target_weight)
        
        await message.answer(
            f"✅ Целевой вес сохранен: {target_weight} кг",
            reply_markup=get_user_data_menu()
        )
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Некорректный формат.\n"
            "Введите число (например: 80):"
        )


@router.callback_query(F.data == "add_workout")
async def add_workout_start(callback: CallbackQuery, state: FSMContext):
    """Start adding workout data"""
    await callback.message.edit_text(
        "💪 Введите данные о тренировке:\n\n"
        "Формат: упражнение - вес - повторения\n\n"
        "Например:\n"
        "Жим лежа - 80 кг - 8 повторений\n"
        "Приседания - 100 кг - 10 повторений",
        reply_markup=None
    )
    await state.set_state(UserDataStates.waiting_for_workout_data)
    await callback.answer()


@router.message(UserDataStates.waiting_for_workout_data)
async def add_workout_finish(message: Message, state: FSMContext, db):
    """Save workout data"""
    workout_data = message.text.strip()
    
    if len(workout_data) < 5 or len(workout_data) > 500:
        await message.answer(
            "❌ Данные о тренировке должны содержать от 5 до 500 символов.\n"
            "Попробуйте еще раз:"
        )
        return
    
    user_id = message.from_user.id
    await db.add_workout_record(user_id, workout_data)
    
    await message.answer(
        "✅ Данные о тренировке сохранены",
        reply_markup=get_user_data_menu()
    )
    await state.clear()


@router.callback_query(F.data == "view_workouts")
async def view_workouts(callback: CallbackQuery, db):
    """View workout history"""
    user_id = callback.from_user.id
    access_service = AccessService(db)
    
    # Verify access
    if not await access_service.check_access(user_id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Get workout records
    workouts = await db.get_workout_records(user_id, limit=10)
    
    if not workouts:
        text = "💪 История тренировок\n\n"
        text += "У вас еще нет записей о тренировках."
    else:
        text = "💪 История тренировок\n\n"
        text += f"Последние {len(workouts)} записей:\n\n"
        
        for i, workout in enumerate(workouts, 1):
            date = workout['created_at'].split()[0]
            text += f"{i}. {date}\n{workout['workout_data']}\n\n"
    
    await callback.message.edit_text(text, reply_markup=get_user_data_menu())
    await callback.answer()