from aiogram import Router, F, Bot
from aiogram.filters import StateFilter, CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from datetime import datetime

from app.custom_filters import AdminProtect, ADMINS

import app.database.requests as rq
import app.keyboards as kb

import pandas as pd
import os


admin = Router()


@admin.message(CommandStart(), AdminProtect())
async def admin_start(message: Message):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    await message.answer("👋 Добро пожаловать, админ!", reply_markup=kb.admin_kb)
    
    
@admin.message(F.text == '👤 Добавить администратора', AdminProtect())
async def add_admin_handler(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    await message.answer("👤 Введите Telegram ID нового администратора:")
    await state.set_state('adding_admin')
    
    
@admin.message(StateFilter('adding_admin'), AdminProtect())
async def save_admin(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
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
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    await message.answer("🗑️ Введите Telegram ID администратора для удаления:")
    await state.set_state('deleting_admin')


@admin.message(StateFilter('deleting_admin'), AdminProtect())
async def remove_admin(message: Message, state: FSMContext, bot: Bot):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    tg_id = int(message.text)
    existing_admin = await rq.get_admin(tg_id)
    admins = await rq.get_admins()
    if not existing_admin:
        await message.answer(f"⚠️ Пользователь с TG ID \"{tg_id}\" не является администратором.")
    else:
        await rq.delete_admin(tg_id)
        await message.answer(f"✅ Пользователь с TG ID \"{tg_id}\" успешно удалён из администраторов.")
        for admin in admins:
            await bot.send_message(chat_id=admin.tg_id, text=f"⚠️ Администратор с TG ID \"{tg_id}\" был удалён из списка администраторов.")
        ADMINS.remove(tg_id)  # Обновляем список админов в памяти
    await state.clear()


@admin.message(F.text == '📚 Добавить предмет', AdminProtect())
async def add_subject(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    await message.answer("📚 Введите название предмета:\n📋 Внизу перечислены список уже существующих предметов:", reply_markup=await kb.get_subjects())
    await state.set_state('adding_subject')


@admin.message(StateFilter('adding_subject'), AdminProtect())
async def save_subject(message: Message, state: FSMContext, bot: Bot):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
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
    now = datetime.now()
    print(f'Admin {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {callback.data}')
    await callback.answer()
    await callback.message.answer("⚠️ Пожалуйста, введите тему вручную. Этот кнопочный ответ предназначен только для отображения существующих тем.")
            
            
@admin.message(F.text == '🗑️ Удалить предмет', AdminProtect())
async def delete_subject(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    await message.answer("🗑️ Введите название предмета для удаления:\n📋 Внизу перечислены список уже существующих предметов:", reply_markup=await kb.get_subjects())
    await state.set_state('deleting_subject')


@admin.message(StateFilter('deleting_subject'), AdminProtect())
async def remove_subject(message: Message, state: FSMContext, bot: Bot):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
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
            await bot.send_message(chat_id=admin.tg_id, text=f"⚠️ Предмет \"{subject_name}\" был удалён из базы данных.")
    else:
        await message.answer(f"⚠️ Предмет '{subject_name}' не найден.")
    await state.clear()


@admin.message(F.text == '📖 Добавить тему', AdminProtect())
async def add_theme(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
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
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    theme_name = message.text
    await state.update_data(theme_name=theme_name)
    await message.answer('📝 Введите описание темы:')
    await state.set_state('theme_description')
    

@admin.message(StateFilter('theme_description'), AdminProtect())
async def save_theme_description(message: Message, state: FSMContext, bot: Bot):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
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
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    await message.answer("🗑️ Введите название темы для удаления:\n📋 Внизу перечислены список уже существующих тем:", reply_markup=await kb.get_themes())
    await state.set_state('deleting_theme')


@admin.message(StateFilter('deleting_theme'), AdminProtect())
async def remove_theme(message: Message, state: FSMContext, bot: Bot):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
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
            await bot.send_message(chat_id=admin.tg_id, text=f"⚠️ Тема \"{theme_name}\" была удалёна из базы данных.")
    else:
        await message.answer(f"⚠️ Тема '{theme_name}' не найдена.")
    await state.clear()


@admin.message(F.text == '❓ Добавить вопрос', AdminProtect())
async def add_question(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
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
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    question_name = message.text
    
    await state.update_data(question_name=question_name)
    await message.answer('❓ Введите текст вопроса:')
    await state.set_state('question_text')
    

@admin.message(StateFilter('question_text'), AdminProtect())
async def save_question_text(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    question_text = message.text
    
    await state.update_data(question_text=question_text)
    await message.answer('🅰️ Введите вариант ответа А:')
    await state.set_state('answer_a')


@admin.message(StateFilter('answer_a'), AdminProtect())
async def save_answer_a(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    answer_a = message.text
    await state.update_data(answer_a=answer_a)
    await message.answer('🅱️ Введите вариант ответа Б:')
    await state.set_state('answer_b')
    
    
@admin.message(StateFilter('answer_b'), AdminProtect())
async def save_answer_b(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    answer_b = message.text
    await state.update_data(answer_b=answer_b)
    await message.answer('🆎 Введите вариант ответа В:')
    await state.set_state('answer_c')
    
    
@admin.message(StateFilter('answer_c'), AdminProtect())
async def save_answer_c(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    answer_c = message.text
    await state.update_data(answer_c=answer_c)
    await message.answer('⓰ Введите вариант ответа Г:')
    await state.set_state('answer_d')
    
    
@admin.message(StateFilter('answer_d'), AdminProtect())
async def save_answer_d(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    answer_d = message.text
    await state.update_data(answer_d=answer_d)
    await message.answer('⭐ Введите количество баллов за вопрос:')
    await state.set_state('question_points')
    
    
@admin.message(StateFilter('question_points'), AdminProtect())
async def save_question_points(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    question_points = int(message.text)
    await state.update_data(question_points=question_points)
    await message.answer('✅ Введите правильный ответ (А, Б, В или Г):')
    await state.set_state('correct_answer')
    
    
@admin.message(StateFilter('correct_answer'), AdminProtect())
async def save_correct_answer(message: Message, state: FSMContext, bot: Bot):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
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
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    await message.answer("🗑️ Введите название вопроса для удаления:\n📋 Внизу перечислены список уже существующих вопросов:", reply_markup=await kb.get_tests())
    await state.set_state('deleting_question')


@admin.message(StateFilter('deleting_question'), AdminProtect())
async def remove_question(message: Message, state: FSMContext, bot: Bot):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
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
            await bot.send_message(chat_id=admin.tg_id, text=f"⚠️ Вопрос \"{question_name}\" был удалён из базы данных.")
    else:
        await message.answer(f"⚠️ Вопрос '{question_name}' не найден.")
    await state.clear()
    
    
# ===== ИМПОРТ ВОПРОСОВ =====

@admin.message(F.text == '📁 Импорт вопросов', AdminProtect())
async def start_questions_import(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    """Начало процесса массового импорта вопросов"""
    try:
        await message.answer(
            "📁 <b>МАССОВЫЙ ИМПОРТ ВОПРОСОВ</b>\n\n"
            "Отправьте Excel файл (.xlsx) с вопросами.\n\n"
            "<b>Формат файла (9 колонок):</b>\n"
            "• A: ID предмета (число)\n"
            "• B: Название предмета\n"
            "• C: ID темы (число)\n"
            "• D: Название темы\n"
            "• E: Название вопроса\n"
            "• F: Текст вопроса\n"
            "• G: Варианты (A|Б|В|Г через |)\n"
            "• H: Правильный ответ (А, Б, В или Г)\n"
            "• I: Баллы (число)\n\n"
            "⚠️ <b>Важно:</b>\n"
            "• Без заголовков - сразу данные\n"
            "• Предмет и тема должны существовать в БД\n"
            "• Варианты через символ | (вертикальная черта)",
            parse_mode='HTML'
        )
        
        # Создаём и отправляем пример файла
        example_file = await create_questions_example()
        await message.answer_document(
            FSInputFile(example_file),
            caption="📄 Пример файла для импорта вопросов"
        )
        os.remove(example_file)
        
        await state.set_state('importing_questions_file')
        
    except Exception as e:
        print(f"Ошибка в start_questions_import: {e}")
        await message.answer(f"❌ Произошла ошибка: {str(e)}")


@admin.message(StateFilter('importing_questions_file'), F.document, AdminProtect())
async def process_questions_file(message: Message, state: FSMContext, bot: Bot):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    """Обработка файла с вопросами"""
    file_path = None
    try:
        # Проверяем расширение файла
        if not message.document.file_name.endswith('.xlsx'):
            await message.answer("❌ Пожалуйста, отправьте файл в формате .xlsx")
            return
        
        # Скачиваем файл
        file = await bot.get_file(message.document.file_id)
        file_path = f"temp_questions_{message.from_user.id}.xlsx"
        await bot.download_file(file.file_path, file_path)
        
        # Читаем Excel (без заголовка)
        df = pd.read_excel(file_path, header=None)
        
        if df.empty:
            await message.answer("❌ Файл пустой!")
            return
        
        # Получаем все предметы и темы для проверки
        all_subjects = await rq.get_subjects()
        all_themes = await rq.get_themes()
        
        # Создаём словари для быстрого поиска
        subjects_dict = {s.id: s.name for s in all_subjects}
        themes_dict = {t.id: t for t in all_themes}
        
        # Добавляем в БД
        added = 0
        skipped = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Проверяем количество колонок
                if len(row) < 9:
                    errors.append(f"Строка {index+1}: недостаточно колонок (нужно 9)")
                    skipped += 1
                    continue
                
                # Извлекаем данные
                subject_id = int(row[0]) if pd.notna(row[0]) else None
                subject_name = str(row[1]).strip() if pd.notna(row[1]) else None
                theme_id = int(row[2]) if pd.notna(row[2]) else None
                theme_name = str(row[3]).strip() if pd.notna(row[3]) else None
                question_name = str(row[4]).strip() if pd.notna(row[4]) else None
                question_text = str(row[5]).strip() if pd.notna(row[5]) else None
                answers_raw = str(row[6]).strip() if pd.notna(row[6]) else None
                correct_answer = str(row[7]).strip().upper() if pd.notna(row[7]) else None
                points = int(row[8]) if pd.notna(row[8]) else 10
                
                # Валидация
                if not all([subject_id, theme_id, question_name, question_text, answers_raw, correct_answer]):
                    errors.append(f"Строка {index+1}: пропущены обязательные поля")
                    skipped += 1
                    continue
                
                # Проверяем существование предмета
                if subject_id not in subjects_dict:
                    errors.append(f"Строка {index+1}: предмет с ID {subject_id} не найден")
                    skipped += 1
                    continue
                
                # Проверяем существование темы
                if theme_id not in themes_dict:
                    errors.append(f"Строка {index+1}: тема с ID {theme_id} не найдена")
                    skipped += 1
                    continue
                
                # Проверяем соответствие темы предмету
                if themes_dict[theme_id].subject_id != subject_id:
                    errors.append(f"Строка {index+1}: тема {theme_id} не принадлежит предмету {subject_id}")
                    skipped += 1
                    continue
                
                # Разбиваем варианты ответов
                answers = [a.strip() for a in answers_raw.split('|')]
                if len(answers) != 4:
                    errors.append(f"Строка {index+1}: должно быть ровно 4 варианта ответа (через |)")
                    skipped += 1
                    continue
                
                # Проверяем правильный ответ
                if correct_answer not in ['А', 'Б', 'В', 'Г']:
                    errors.append(f"Строка {index+1}: правильный ответ должен быть А, Б, В или Г")
                    skipped += 1
                    continue
                
                # Проверяем, существует ли уже такой вопрос
                existing_tests = await rq.get_tests_by_theme_id(theme_id)
                exists = any(t.name == question_name for t in existing_tests)
                
                if exists:
                    skipped += 1
                    continue
                
                # Добавляем вопрос
                await rq.add_test(
                    theme_id=theme_id,
                    subject_id=subject_id,
                    name=question_name,
                    question=question_text,
                    answer1=answers[0],
                    answer2=answers[1],
                    answer3=answers[2],
                    answer4=answers[3],
                    point=points,
                    correct_answer=correct_answer
                )
                added += 1
                
            except Exception as e:
                errors.append(f"Строка {index+1}: ошибка обработки - {str(e)}")
                skipped += 1
        
        # Формируем отчёт
        report = (
            f"✅ <b>ИМПОРТ ЗАВЕРШЁН!</b>\n\n"
            f"📊 <b>Статистика:</b>\n"
            f"• Добавлено вопросов: {added}\n"
            f"• Пропущено/ошибки: {skipped}\n"
            f"• Всего обработано: {added + skipped}\n"
        )
        
        if errors:
            report += f"\n⚠️ <b>Ошибки ({len(errors)}):</b>\n"
            for error in errors[:5]:  # Показываем первые 5
                report += f"• {error}\n"
            if len(errors) > 5:
                report += f"• ... и ещё {len(errors) - 5}\n"
        
        await message.answer(report, parse_mode='HTML')
        
        # Уведомляем всех пользователей о новых вопросах
        if added > 0:
            users = await rq.get_users()
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.tg_id,
                        text=f'╔═══════════════════════════╗\n'
                             f'║  🧠 <b>НОВЫЙ ВОПРОС!</b> 🧠   ║\n'
                             f'╚═══════════════════════════╝\n\n'
                             f'💡 Добавлено новых вопросов: <b>{added}</b>\n\n'
                             f'🚀 <b>Проверьте свои знания!</b>\n\n'
                             f'━━━━━━━━━━━━━━━━━━━━━━━━━━━',
                        parse_mode='HTML'
                    )
                except Exception as e:
                    print(f"Ошибка отправки сообщения пользователю {user.tg_id}: {e}")
        
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке файла: {str(e)}")
        await state.clear()
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


async def create_questions_example():
    """Создаёт пример Excel файла для вопросов"""
    try:
        # Получаем реальные данные из БД для примера
        subjects = await rq.get_subjects()
        themes = await rq.get_themes()
        
        subjects_list = list(subjects) if subjects else []
        themes_list = list(themes) if themes else []
        
        # Если есть данные в БД, используем их
        if subjects_list and themes_list:
            subject = subjects_list[0]
            theme = next((t for t in themes_list if t.subject_id == subject.id), themes_list[0])
            
            data = {
                'subject_id': [subject.id, subject.id],
                'subject_name': [subject.name, subject.name],
                'theme_id': [theme.id, theme.id],
                'theme_name': [theme.name, theme.name],
                'question_name': ['Вопрос 1', 'Вопрос 2'],
                'question_text': [
                    'Какой результат даст 2+2?',
                    'Сколько будет 5*5?'
                ],
                'answers': [
                    '3|4|5|6',
                    '20|25|30|35'
                ],
                'correct_answer': ['Б', 'Б'],
                'points': [10, 10]
            }
        else:
            # Используем примерные данные
            data = {
                'subject_id': [1, 1],
                'subject_name': ['Математика', 'Математика'],
                'theme_id': [1, 1],
                'theme_name': ['Арифметика', 'Арифметика'],
                'question_name': ['Сложение', 'Умножение'],
                'question_text': [
                    'Какой результат даст 2+2?',
                    'Сколько будет 5*5?'
                ],
                'answers': [
                    '3|4|5|6',
                    '20|25|30|35'
                ],
                'correct_answer': ['Б', 'Б'],
                'points': [10, 10]
            }
        
        df = pd.DataFrame(data)
        
        filename = 'example_questions.xlsx'
        df.to_excel(filename, index=False, header=False)
        return filename
        
    except Exception as e:
        print(f"Ошибка создания примера: {e}")
        # Создаём минимальный пример при ошибке
        data = {
            'subject_id': [1, 1],
            'subject_name': ['Математика', 'Математика'],
            'theme_id': [1, 1],
            'theme_name': ['Арифметика', 'Арифметика'],
            'question_name': ['Сложение', 'Умножение'],
            'question_text': [
                'Какой результат даст 2+2?',
                'Сколько будет 5*5?'
            ],
            'answers': [
                '3|4|5|6',
                '20|25|30|35'
            ],
            'correct_answer': ['Б', 'Б'],
            'points': [10, 10]
        }
        df = pd.DataFrame(data)
        filename = 'example_questions.xlsx'
        df.to_excel(filename, index=False, header=False)
        return filename


# Отменить импорт
@admin.message(F.text == '❌ Отмена', StateFilter('importing_subjects_file', 'importing_themes_file', 'selecting_subject_for_import', 'importing_questions_file'), AdminProtect())
async def cancel_import(message: Message, state: FSMContext):
    now = datetime.now()
    print(f'Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    """Отмена импорта"""
    await state.clear()
    await message.answer("❌ Импорт отменён.", reply_markup=kb.admin_kb)