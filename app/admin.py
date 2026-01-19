from aiogram import Router, F, Bot
from aiogram.filters import StateFilter, CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.custom_filters import AdminProtect, ADMINS

import app.database.requests as rq
import app.keyboards as kb


admin = Router()


@admin.message(CommandStart(), AdminProtect())
async def admin_start(message: Message):
    await message.answer("👋 Добро пожаловать, админ!", reply_markup=kb.admin_kb)
    
    
@admin.message(F.text == '👤 Добавить администратора', AdminProtect())
async def add_admin_handler(message: Message, state: FSMContext):
    await message.answer("👤 Введите Telegram ID нового администратора:")
    await state.set_state('adding_admin')
    
    
@admin.message(StateFilter('adding_admin'), AdminProtect())
async def save_admin(message: Message, state: FSMContext):
    tg_id = int(message.text)
    existing_admin = await rq.get_admin(tg_id)
    if existing_admin:
        await message.answer(f"⚠️ Пользователь с TG ID \"{tg_id}\" уже является администратором.")
    else:
        await rq.add_admin(tg_id)
        await message.answer(f"✅ Пользователь с TG ID \"{tg_id}\" успешно добавлен в администраторы.")
        ADMINS.append(tg_id)  # Обновляем список админов в памяти
    await state.clear()


@admin.message(F.text == '❌ Удалить администратора', AdminProtect())
async def delete_admin_handler(message: Message, state: FSMContext):
    await message.answer("🗑️ Введите Telegram ID администратора для удаления:")
    await state.set_state('deleting_admin')


@admin.message(StateFilter('deleting_admin'), AdminProtect())
async def remove_admin(message: Message, state: FSMContext):
    tg_id = int(message.text)
    existing_admin = await rq.get_admin(tg_id)
    admins = await rq.get_admins()
    if not existing_admin:
        await message.answer(f"⚠️ Пользователь с TG ID \"{tg_id}\" не является администратором.")
    else:
        await rq.delete_admin(tg_id)
        await message.answer(f"✅ Пользователь с TG ID \"{tg_id}\" успешно удалён из администраторов.")
        for admin in admins:
            await message.send_copy(chat_id=admin.tg_id, text=f"⚠️ Администратор с TG ID \"{tg_id}\" был удалён из списка администраторов.")
        ADMINS.remove(tg_id)  # Обновляем список админов в памяти
    await state.clear()


@admin.message(F.text == '📚 Добавить предмет', AdminProtect())
async def add_subject(message: Message, state: FSMContext):
    await message.answer("📚 Введите название предмета:\n📋 Внизу перечислены список уже существующих предметов:", reply_markup=await kb.get_subjects())
    await state.set_state('adding_subject')


@admin.message(StateFilter('adding_subject'), AdminProtect())
async def save_subject(message: Message, state: FSMContext, bot: Bot):
    subject_name = message.text
    await rq.add_subject(name=subject_name)
    await message.answer(f"✅ Предмет '{subject_name}' успешно добавлен!")
    await state.clear()
    users = await rq.get_users()
    for user in users:
        try:
            await bot.send_message(chat_id=user.tg_id, text=f'╔════════════════════════════════╗\n║  🚀 <b>ГОРЯЧИЕ НОВОСТИ!</b> 🚀  ║\n╚════════════════════════════════╝\n\n✨ <i>Специально для вас!</i> ✨\n\n📚 <b>Новый предмет:</b>\n   <code>{subject_name}</code>\n\n🎯 Спешите добавить в закладки!\n💡 Не пропустите интересный контент!\n\n⚡ <b>Начните изучение прямо сейчас!</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', parse_mode='HTML')
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {user.tg_id}: {e}")
            
            
@admin.callback_query(F.data == 'empty_data', AdminProtect())
async def empty_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("⚠️ Пожалуйста, введите тему вручную. Этот кнопочный ответ предназначен только для отображения существующих тем.")
            
            
@admin.message(F.text == '🗑️ Удалить предмет', AdminProtect())
async def delete_subject(message: Message, state: FSMContext):
    await message.answer("🗑️ Введите название предмета для удаления:\n📋 Внизу перечислены список уже существующих предметов:", reply_markup=await kb.get_subjects())
    await state.set_state('deleting_subject')


@admin.message(StateFilter('deleting_subject'), AdminProtect())
async def remove_subject(message: Message, state: FSMContext):
    subject_name = message.text
    subjects = await rq.get_subjects()
    subject_to_delete = None
    admins = await rq.get_admins()
    for subject in subjects:
        if subject.name == subject_name:
            subject_to_delete = subject
            break
    if subject_to_delete:
        await rq.delete_subject(subject_to_delete.id)
        await message.answer(f"✅ Предмет '{subject_name}' успешно удалён!")
        for admin in admins:
            await message.send_copy(chat_id=admin.tg_id, text=f"⚠️ Предмет \"{subject_name}\" был удалён из базы данных.")
    else:
        await message.answer(f"⚠️ Предмет '{subject_name}' не найден.")
    await state.clear()


@admin.message(F.text == '📖 Добавить тему', AdminProtect())
async def add_theme(message: Message, state: FSMContext):
    await message.answer("📚 Выберите ID предмета:", reply_markup=await kb.subjects_id())
    await state.set_state('adding_theme')


@admin.callback_query(F.data.startswith('subject_'), StateFilter('adding_theme'), AdminProtect())
async def save_theme(callback: CallbackQuery, state: FSMContext):
    theme_id = callback.data.split('_')[1]
    await state.update_data(theme_id=theme_id)
    await callback.answer()
    await callback.message.answer('📖 Введите название темы:\n📋 Внизу перечислены список уже существующих тем по этому предмету:', reply_markup=await kb.themes_by_subject(theme_id))
    await state.set_state('theme_name')
    

@admin.message(StateFilter('theme_name'), AdminProtect())
async def save_theme_name(message: Message, state: FSMContext):
    theme_name = message.text
    await state.update_data(theme_name=theme_name)
    await message.answer('📝 Введите описание темы:')
    await state.set_state('theme_description')
    

@admin.message(StateFilter('theme_description'), AdminProtect())
async def save_theme_description(message: Message, state: FSMContext, bot: Bot):
    theme_description = message.text
    data = await state.get_data()
    theme_id = data['theme_id']
    theme_name = data['theme_name']
    
    await rq.add_theme(subject_id=theme_id, name=theme_name, description=theme_description)
    await message.answer(f"✅ Тема '{theme_name}' успешно добавлена!")
    await state.clear()
    
    users = await rq.get_users()
    for user in users:
        try:
            await bot.send_message(chat_id=user.tg_id, text=f'╔════════════════════════════════╗\n║  ⭐ <b>НОВАЯ ТЕМА!</b> ⭐  ║\n╚════════════════════════════════╝\n\n🎓 <i>Добавлен свежий материал!</i> 🎓\n\n📖 <b>Новая тема:</b>\n   <code>{theme_name}</code>\n\n📝 <b>Описание:</b>\n<i>{theme_description}</i>\n\n🚀 Начните обучение сейчас!\n💪 Расширяйте свои знания!\n\n⚡ <b>Уровень мастерства ждёт вас!</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', parse_mode='HTML')
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {user.tg_id}: {e}")
            
            
@admin.message(F.text == '🗑️ Удалить тему', AdminProtect())
async def delete_theme(message: Message, state: FSMContext):
    await message.answer("🗑️ Введите название темы для удаления:\n📋 Внизу перечислены список уже существующих тем:", reply_markup=await kb.get_themes())
    await state.set_state('deleting_theme')


@admin.message(StateFilter('deleting_theme'), AdminProtect())
async def remove_theme(message: Message, state: FSMContext):
    theme_name = message.text
    themes = await rq.get_themes()
    theme_to_delete = None
    admins = await rq.get_admins()
    for theme in themes:
        if theme.name == theme_name:
            theme_to_delete = theme
            break
    if theme_to_delete:
        await rq.delete_theme(theme_to_delete.id)
        await message.answer(f"✅ Тема '{theme_name}' успешно удалена!")
        for admin in admins:
            await message.send_copy(chat_id=admin.tg_id, text=f"⚠️ Тема \"{theme_name}\" была удалёна из базы данных.")
    else:
        await message.answer(f"⚠️ Тема '{theme_name}' не найдена.")
    await state.clear()


@admin.message(F.text == '❓ Добавить вопрос', AdminProtect())
async def add_question(message: Message, state: FSMContext):
    await message.answer("📚 Выберите ID предмета для вопроса:", reply_markup=await kb.subjects_id())
    await state.set_state('question_subject_id')

@admin.callback_query(F.data.startswith('subject_'), StateFilter('question_subject_id'), AdminProtect())
async def save_question_subject_id(callback: CallbackQuery, state: FSMContext):
    subject_id = callback.data.split('_')[1]
    
    await state.update_data(subject_id=subject_id)
    await callback.answer()
    await callback.message.answer("📖 Выберите ID темы для вопроса:\n📋 Внизу перечислены список уже существующих тем по этому предмету:", reply_markup=await kb.get_themes_by_subject(subject_id))
    await state.set_state('question_theme_id')


@admin.callback_query(F.data.startswith('theme_'), StateFilter('question_theme_id'), AdminProtect())
async def save_question_theme_id(callback: CallbackQuery, state: FSMContext):
    theme_id = callback.data.split('_')[1]
    
    await callback.answer()
    await state.update_data(theme_id=theme_id)
    await callback.message.answer('❓ Введите название вопроса:\n📋 Внизу перечислены список уже существующих вопросов по этой теме:', reply_markup=await kb.tests_by_theme(theme_id))
    await state.set_state('question_name')
    

@admin.message(StateFilter('question_name'), AdminProtect())
async def save_question_name(message: Message, state: FSMContext):
    question_name = message.text
    
    await state.update_data(question_name=question_name)
    await message.answer('❓ Введите текст вопроса:')
    await state.set_state('question_text')
    

@admin.message(StateFilter('question_text'), AdminProtect())
async def save_question_text(message: Message, state: FSMContext):
    question_text = message.text
    
    await state.update_data(question_text=question_text)
    await message.answer('🅰️ Введите вариант ответа А:')
    await state.set_state('answer_a')


@admin.message(StateFilter('answer_a'), AdminProtect())
async def save_answer_a(message: Message, state: FSMContext):
    answer_a = message.text
    await state.update_data(answer_a=answer_a)
    await message.answer('🅱️ Введите вариант ответа Б:')
    await state.set_state('answer_b')
    
    
@admin.message(StateFilter('answer_b'), AdminProtect())
async def save_answer_b(message: Message, state: FSMContext):
    answer_b = message.text
    await state.update_data(answer_b=answer_b)
    await message.answer('🆎 Введите вариант ответа В:')
    await state.set_state('answer_c')
    
    
@admin.message(StateFilter('answer_c'), AdminProtect())
async def save_answer_c(message: Message, state: FSMContext):
    answer_c = message.text
    await state.update_data(answer_c=answer_c)
    await message.answer('⓰ Введите вариант ответа Г:')
    await state.set_state('answer_d')
    
    
@admin.message(StateFilter('answer_d'), AdminProtect())
async def save_answer_d(message: Message, state: FSMContext):
    answer_d = message.text
    await state.update_data(answer_d=answer_d)
    await message.answer('⭐ Введите количество баллов за вопрос:')
    await state.set_state('question_points')
    
    
@admin.message(StateFilter('question_points'), AdminProtect())
async def save_question_points(message: Message, state: FSMContext):
    question_points = int(message.text)
    await state.update_data(question_points=question_points)
    await message.answer('✅ Введите правильный ответ (А, Б, В или Г):')
    await state.set_state('correct_answer')
    
    
@admin.message(StateFilter('correct_answer'), AdminProtect())
async def save_correct_answer(message: Message, state: FSMContext, bot: Bot):
    correct_answer = message.text
    data = await state.get_data()
    
    subject_id = data['subject_id']
    theme_id = data['theme_id']
    question_name = data['question_name']
    question_text = data['question_text']
    answer_a = data['answer_a']
    answer_b = data['answer_b']
    answer_c = data['answer_c']
    answer_d = data['answer_d']
    question_points = data['question_points']
    
    await rq.add_test(
        theme_id=theme_id,
        subject_id=subject_id,
        name=question_name,
        question=question_text,
        answer1=answer_a,
        answer2=answer_b,
        answer3=answer_c,
        answer4=answer_d,
        point=question_points,
        correct_answer=correct_answer
    )
    
    await message.answer(f"✅ Вопрос '{question_name}' успешно добавлен!")
    await state.clear()
    
    subject = await rq.get_subject(subject_id=subject_id)
    theme = await rq.get_theme(theme_id)
    
    users = await rq.get_users()
    for user in users:
        try:
            await bot.send_message(chat_id=user.tg_id, text=f'╔════════════════════════════════╗\n║  🧠 <b>НОВЫЙ ВОПРОС!</b> 🧠  ║\n╚════════════════════════════════╝\n\n📚 <b>Предмет:</b>\n<code>{subject.name}</code>\n\n📖 <b>Тема:</b>\n<code>{theme.name}</code>\n\n💡 Новый вопрос готов для тестирования!\n\n🚀 <b>Проверьте свои знания!</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', parse_mode='HTML')
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {user.tg_id}: {e}")
            
            
@admin.message(F.text == '🗑️ Удалить вопрос', AdminProtect())
async def delete_question(message: Message, state: FSMContext):
    await message.answer("🗑️ Введите название вопроса для удаления:\n📋 Внизу перечислены список уже существующих вопросов:", reply_markup=await kb.get_tests())
    await state.set_state('deleting_question')


@admin.message(StateFilter('deleting_question'), AdminProtect())
async def remove_question(message: Message, state: FSMContext):
    question_name = message.text
    tests = await rq.get_tests()
    test_to_delete = None
    admins = await rq.get_admins()
    for test in tests:
        if test.name == question_name:
            test_to_delete = test
            break
    if test_to_delete:
        await rq.delete_test(test_to_delete.id)
        await message.answer(f"✅ Вопрос '{question_name}' успешно удалён!")
        for admin in admins:
            await message.send_copy(chat_id=admin.tg_id, text=f"⚠️ Вопрос \"{question_name}\" был удалён из базы данных.")
    else:
        await message.answer(f"⚠️ Вопрос '{question_name}' не найден.")
    await state.clear()