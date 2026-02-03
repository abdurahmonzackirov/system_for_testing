from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from datetime import datetime
import pandas as pd
import os

from app.custom_filters import AdminProtect
import app.database.requests as rq
import app.keyboards as kb


bulk_import = Router()


# ===== ИМПОРТ ПРЕДМЕТОВ =====

@bulk_import.message(F.text == '📁 Импорт предметов', AdminProtect())
async def start_subjects_import(message: Message, state: FSMContext):
    """Начало процесса массового импорта предметов"""
    now = datetime.now()
    print(f"Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    
    await message.answer(
        "📁 <b>МАССОВЫЙ ИМПОРТ ПРЕДМЕТОВ</b>\n\n"
        "Отправьте Excel файл (.xlsx) с предметами.\n\n"
        "<b>Формат файла:</b>\n"
        "• Колонка A: Название предмета\n"
        "• Без заголовков - сразу данные\n\n"
        "<b>Пример:</b>\n"
        "Математика\n"
        "Физика\n"
        "Информатика\n"
        "Биология",
        parse_mode='HTML'
    )
    
    # Создаём и отправляем пример файла
    example_file = create_subjects_example()
    await message.answer_document(
        FSInputFile(example_file),
        caption="📄 Пример файла для импорта предметов"
    )
    os.remove(example_file)
    
    await state.set_state('importing_subjects_file')


@bulk_import.message(StateFilter('importing_subjects_file'), F.document, AdminProtect())
async def process_subjects_file(message: Message, state: FSMContext, bot: Bot):
    """Обработка файла с предметами"""
    now = datetime.now()
    print(f"Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: [DOCUMENT]")
    
    file_path = None
    try:
        # Проверяем расширение файла
        if not message.document.file_name.endswith('.xlsx'):
            await message.answer("❌ Пожалуйста, отправьте файл в формате .xlsx")
            return
        
        # Скачиваем файл
        file = await bot.get_file(message.document.file_id)
        file_path = f"temp_subjects_{message.from_user.id}.xlsx"
        await bot.download_file(file.file_path, file_path)
        
        # Читаем Excel (без заголовка)
        df = pd.read_excel(file_path, header=None)
        subjects = df[0].dropna().tolist()
        
        if not subjects:
            await message.answer("❌ Файл пустой или неправильного формата!")
            return
        
        # Добавляем в БД
        added = 0
        skipped = 0
        skipped_names = []
        
        for subject_name in subjects:
            subject_name = str(subject_name).strip()
            if not subject_name:
                continue
            
            # Проверяем, существует ли предмет
            all_subjects = await rq.get_subjects()
            existing = any(s.name == subject_name for s in all_subjects)
            
            if existing:
                skipped += 1
                skipped_names.append(subject_name)
                continue
            
            # Добавляем новый предмет
            await rq.add_subject(subject_name)
            added += 1
        
        # Формируем отчёт
        report = (
            f"✅ <b>ИМПОРТ ЗАВЕРШЁН!</b>\n\n"
            f"📊 <b>Статистика:</b>\n"
            f"• Добавлено: {added}\n"
            f"• Пропущено (уже существуют): {skipped}\n"
            f"• Всего обработано: {added + skipped}\n"
        )
        
        if skipped_names:
            report += f"\n⚠️ <b>Пропущенные предметы:</b>\n"
            for name in skipped_names[:5]:  # Показываем первые 5
                report += f"• {name}\n"
            if len(skipped_names) > 5:
                report += f"• ... и ещё {len(skipped_names) - 5}\n"
        
        await message.answer(report, parse_mode='HTML')
        
        # Уведомляем всех пользователей о новых предметах
        if added > 0:
            users = await rq.get_users()
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.tg_id,
                        text=f'╔═══════════════════════════╗\n'
                             f'║  🚀 <b>ГОРЯЧИЕ НОВОСТИ!</b> 🚀  ║\n'
                             f'╚═══════════════════════════╝\n\n'
                             f'✨ <i>Специально для вас!</i> ✨\n\n'
                             f'📚 <b>Добавлено {added} новых предметов!</b>\n\n'
                             f'🎯 Спешите изучить!\n'
                             f'💡 Не пропустите интересный контент!\n\n'
                             f'⚡ <b>Начните изучение прямо сейчас!</b>',
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


# ===== ИМПОРТ ТЕМ =====

@bulk_import.message(F.text == '📁 Импорт тем', AdminProtect())
async def start_themes_import(message: Message, state: FSMContext):
    """Начало процесса массового импорта тем"""
    now = datetime.now()
    print(f"Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    
    subjects = await rq.get_subjects()
    
    if not subjects:
        await message.answer("❌ Сначала добавьте предметы!")
        return
    
    await message.answer(
        "📚 <b>Шаг 1/2: Выберите предмет</b>\n\n"
        "Для какого предмета вы хотите импортировать темы?",
        reply_markup=await kb.subjects_id(),
        parse_mode='HTML'
    )
    
    await state.set_state('selecting_subject_for_import')


@bulk_import.callback_query(F.data.startswith('subject_'), StateFilter('selecting_subject_for_import'), AdminProtect())
async def subject_selected_for_import(callback: CallbackQuery, state: FSMContext):
    """Предмет выбран, запрашиваем файл с темами"""
    subject_id = int(callback.data.split('_')[1])
    subject = await rq.get_subject(subject_id=subject_id)
    
    if not subject:
        await callback.message.answer("❌ Предмет не найден!")
        await state.clear()
        await callback.answer()
        return
    
    await state.update_data(subject_id=subject_id, subject_name=subject.name)
    
    await callback.message.answer(
        f"📁 <b>МАССОВЫЙ ИМПОРТ ТЕМ</b>\n\n"
        f"📚 Предмет: <b>{subject.name}</b>\n\n"
        f"Отправьте Excel файл (.xlsx) с темами.\n\n"
        f"<b>Формат файла:</b>\n"
        f"• Колонка A: Название темы\n"
        f"• Колонка B: Описание темы (опционально)\n"
        f"• Без заголовков - сразу данные\n\n"
        f"<b>Пример:</b>\n"
        f"Введение в алгебру | Основные понятия алгебры\n"
        f"Линейные уравнения | Решение уравнений первой степени",
        parse_mode='HTML'
    )
    
    # Создаём и отправляем пример файла
    example_file = create_themes_example()
    await callback.message.answer_document(
        FSInputFile(example_file),
        caption="📄 Пример файла для импорта тем"
    )
    os.remove(example_file)
    
    await state.set_state('importing_themes_file')
    await callback.answer()


@bulk_import.message(StateFilter('importing_themes_file'), F.document, AdminProtect())
async def process_themes_file(message: Message, state: FSMContext, bot: Bot):
    """Обработка файла с темами"""
    now = datetime.now()
    print(f"Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: [DOCUMENT]")
    
    file_path = None
    try:
        data = await state.get_data()
        subject_id = data['subject_id']
        subject_name = data['subject_name']
        
        # Проверяем расширение файла
        if not message.document.file_name.endswith('.xlsx'):
            await message.answer("❌ Пожалуйста, отправьте файл в формате .xlsx")
            return
        
        # Скачиваем файл
        file = await bot.get_file(message.document.file_id)
        file_path = f"temp_themes_{message.from_user.id}.xlsx"
        await bot.download_file(file.file_path, file_path)
        
        # Читаем Excel (без заголовка)
        df = pd.read_excel(file_path, header=None)
        
        if df.empty:
            await message.answer("❌ Файл пустой!")
            return
        
        # Добавляем в БД
        added = 0
        skipped = 0
        skipped_names = []
        
        for index, row in df.iterrows():
            # Название темы из колонки A
            theme_name = str(row[0]).strip() if pd.notna(row[0]) else None
            
            if not theme_name:
                continue
            
            # Описание из колонки B (если есть)
            theme_description = str(row[1]).strip() if len(row) > 1 and pd.notna(row[1]) else "Описание будет добавлено позже."
            
            # Проверяем, существует ли тема
            existing_themes = await rq.get_themes_by_subject(subject_id)
            existing = any(t.name == theme_name for t in existing_themes)
            
            if existing:
                skipped += 1
                skipped_names.append(theme_name)
                continue
            
            # Добавляем новую тему
            await rq.add_theme(
                subject_id=subject_id,
                name=theme_name,
                description=theme_description
            )
            added += 1
        
        # Формируем отчёт
        report = (
            f"✅ <b>ИМПОРТ ЗАВЕРШЁН!</b>\n\n"
            f"📚 Предмет: <b>{subject_name}</b>\n\n"
            f"📊 <b>Статистика:</b>\n"
            f"• Добавлено тем: {added}\n"
            f"• Пропущено (уже существуют): {skipped}\n"
            f"• Всего обработано: {added + skipped}\n"
        )
        
        if skipped_names:
            report += f"\n⚠️ <b>Пропущенные темы:</b>\n"
            for name in skipped_names[:5]:
                report += f"• {name}\n"
            if len(skipped_names) > 5:
                report += f"• ... и ещё {len(skipped_names) - 5}\n"
        
        await message.answer(report, parse_mode='HTML')
        
        # Уведомляем всех пользователей о новых темах
        if added > 0:
            users = await rq.get_users()
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.tg_id,
                        text=f'╔═══════════════════════════╗\n'
                             f'║  ⭐ <b>НОВАЯ ТЕМА!</b> ⭐  ║\n'
                             f'╚═══════════════════════════╝\n\n'
                             f'🎓 <i>Добавлен свежий материал!</i> 🎓\n\n'
                             f'📚 <b>Предмет:</b> {subject_name}\n'
                             f'📖 <b>Новых тем:</b> {added}\n\n'
                             f'🚀 Начните обучение сейчас!\n'
                             f'💪 Расширяйте свои знания!\n\n'
                             f'⚡ <b>Уровень мастерства ждёт вас!</b>',
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


# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def create_subjects_example():
    """Создаёт пример Excel файла для предметов"""
    df = pd.DataFrame({
        'Название': [
            'Математика',
            'Физика',
            'Информатика',
            'Химия',
            'Биология'
        ]
    })
    
    filename = 'example_subjects.xlsx'
    df.to_excel(filename, index=False, header=False)
    return filename


def create_themes_example():
    """Создаёт пример Excel файла для тем"""
    df = pd.DataFrame({
        'Название': [
            'Введение в предмет',
            'Основные понятия',
            'Практические задания',
            'Контрольная работа'
        ],
        'Описание': [
            'Первое знакомство с предметом и его основами',
            'Изучение базовых терминов и определений',
            'Закрепление знаний на практике',
            'Проверка усвоенного материала'
        ]
    })
    
    filename = 'example_themes.xlsx'
    df.to_excel(filename, index=False, header=False)
    return filename


# Отменить импорт
@bulk_import.message(F.text == '❌ Отмена', StateFilter('importing_subjects_file', 'importing_themes_file', 'selecting_subject_for_import', 'importing_questions_file'), AdminProtect())
async def cancel_import(message: Message, state: FSMContext):
    """Отмена импорта"""
    now = datetime.now()
    print(f"Admin {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    await state.clear()
    await message.answer("❌ Импорт отменён.", reply_markup=kb.admin_kb)


@bulk_import.message(StateFilter('importing_subjects_file'), F.document, AdminProtect())
async def process_subjects_file(message: Message, state: FSMContext, bot: Bot):
    """Обработка файла с предметами"""
    file_path = None
    try:
        # Проверяем расширение файла
        if not message.document.file_name.endswith('.xlsx'):
            await message.answer("❌ Пожалуйста, отправьте файл в формате .xlsx")
            return
        
        # Скачиваем файл
        file = await bot.get_file(message.document.file_id)
        file_path = f"temp_subjects_{message.from_user.id}.xlsx"
        await bot.download_file(file.file_path, file_path)
        
        # Читаем Excel (без заголовка)
        df = pd.read_excel(file_path, header=None)
        subjects = df[0].dropna().tolist()
        
        if not subjects:
            await message.answer("❌ Файл пустой или неправильного формата!")
            return
        
        # Добавляем в БД
        added = 0
        skipped = 0
        skipped_names = []
        
        for subject_name in subjects:
            subject_name = str(subject_name).strip()
            if not subject_name:
                continue
            
            # Проверяем, существует ли предмет
            all_subjects = await rq.get_subjects()
            existing = any(s.name == subject_name for s in all_subjects)
            
            if existing:
                skipped += 1
                skipped_names.append(subject_name)
                continue
            
            # Добавляем новый предмет
            await rq.add_subject(subject_name)
            added += 1
        
        # Формируем отчёт
        report = (
            f"✅ <b>ИМПОРТ ЗАВЕРШЁН!</b>\n\n"
            f"📊 <b>Статистика:</b>\n"
            f"• Добавлено: {added}\n"
            f"• Пропущено (уже существуют): {skipped}\n"
            f"• Всего обработано: {added + skipped}\n"
        )
        
        if skipped_names:
            report += f"\n⚠️ <b>Пропущенные предметы:</b>\n"
            for name in skipped_names[:5]:  # Показываем первые 5
                report += f"• {name}\n"
            if len(skipped_names) > 5:
                report += f"• ... и ещё {len(skipped_names) - 5}\n"
        
        await message.answer(report, parse_mode='HTML')
        
        # Уведомляем всех пользователей о новых предметах
        if added > 0:
            users = await rq.get_users()
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.tg_id,
                        text=f'╔═══════════════════════════╗\n'
                             f'║  🚀 <b>ГОРЯЧИЕ НОВОСТИ!</b> 🚀  ║\n'
                             f'╚═══════════════════════════╝\n\n'
                             f'✨ <i>Специально для вас!</i> ✨\n\n'
                             f'📚 <b>Добавлено {added} новых предметов!</b>\n\n'
                             f'🎯 Спешите изучить!\n'
                             f'💡 Не пропустите интересный контент!\n\n'
                             f'⚡ <b>Начните изучение прямо сейчас!</b>',
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


# ===== ИМПОРТ ТЕМ =====

@bulk_import.message(F.text == '📁 Импорт тем', AdminProtect())
async def start_themes_import(message: Message, state: FSMContext):
    """Начало процесса массового импорта тем"""
    subjects = await rq.get_subjects()
    
    if not subjects:
        await message.answer("❌ Сначала добавьте предметы!")
        return
    
    await message.answer(
        "📚 <b>Шаг 1/2: Выберите предмет</b>\n\n"
        "Для какого предмета вы хотите импортировать темы?",
        reply_markup=await kb.subjects_id(),
        parse_mode='HTML'
    )
    
    await state.set_state('selecting_subject_for_import')


@bulk_import.callback_query(F.data.startswith('subject_'), StateFilter('selecting_subject_for_import'), AdminProtect())
async def subject_selected_for_import(callback: CallbackQuery, state: FSMContext):
    """Предмет выбран, запрашиваем файл с темами"""
    subject_id = int(callback.data.split('_')[1])
    subject = await rq.get_subject(subject_id=subject_id)
    
    if not subject:
        await callback.message.answer("❌ Предмет не найден!")
        await state.clear()
        await callback.answer()
        return
    
    await state.update_data(subject_id=subject_id, subject_name=subject.name)
    
    await callback.message.answer(
        f"📁 <b>МАССОВЫЙ ИМПОРТ ТЕМ</b>\n\n"
        f"📚 Предмет: <b>{subject.name}</b>\n\n"
        f"Отправьте Excel файл (.xlsx) с темами.\n\n"
        f"<b>Формат файла:</b>\n"
        f"• Колонка A: Название темы\n"
        f"• Колонка B: Описание темы (опционально)\n"
        f"• Без заголовков - сразу данные\n\n"
        f"<b>Пример:</b>\n"
        f"Введение в алгебру | Основные понятия алгебры\n"
        f"Линейные уравнения | Решение уравнений первой степени",
        parse_mode='HTML'
    )
    
    # Создаём и отправляем пример файла
    example_file = create_themes_example()
    await callback.message.answer_document(
        FSInputFile(example_file),
        caption="📄 Пример файла для импорта тем"
    )
    os.remove(example_file)
    
    await state.set_state('importing_themes_file')
    await callback.answer()


@bulk_import.message(StateFilter('importing_themes_file'), F.document, AdminProtect())
async def process_themes_file(message: Message, state: FSMContext, bot: Bot):
    """Обработка файла с темами"""
    file_path = None
    try:
        data = await state.get_data()
        subject_id = data['subject_id']
        subject_name = data['subject_name']
        
        # Проверяем расширение файла
        if not message.document.file_name.endswith('.xlsx'):
            await message.answer("❌ Пожалуйста, отправьте файл в формате .xlsx")
            return
        
        # Скачиваем файл
        file = await bot.get_file(message.document.file_id)
        file_path = f"temp_themes_{message.from_user.id}.xlsx"
        await bot.download_file(file.file_path, file_path)
        
        # Читаем Excel (без заголовка)
        df = pd.read_excel(file_path, header=None)
        
        if df.empty:
            await message.answer("❌ Файл пустой!")
            return
        
        # Добавляем в БД
        added = 0
        skipped = 0
        skipped_names = []
        
        for index, row in df.iterrows():
            # Название темы из колонки A
            theme_name = str(row[0]).strip() if pd.notna(row[0]) else None
            
            if not theme_name:
                continue
            
            # Описание из колонки B (если есть)
            theme_description = str(row[1]).strip() if len(row) > 1 and pd.notna(row[1]) else "Описание будет добавлено позже."
            
            # Проверяем, существует ли тема
            existing_themes = await rq.get_themes_by_subject(subject_id)
            existing = any(t.name == theme_name for t in existing_themes)
            
            if existing:
                skipped += 1
                skipped_names.append(theme_name)
                continue
            
            # Добавляем новую тему
            await rq.add_theme(
                subject_id=subject_id,
                name=theme_name,
                description=theme_description
            )
            added += 1
        
        # Формируем отчёт
        report = (
            f"✅ <b>ИМПОРТ ЗАВЕРШЁН!</b>\n\n"
            f"📚 Предмет: <b>{subject_name}</b>\n\n"
            f"📊 <b>Статистика:</b>\n"
            f"• Добавлено тем: {added}\n"
            f"• Пропущено (уже существуют): {skipped}\n"
            f"• Всего обработано: {added + skipped}\n"
        )
        
        if skipped_names:
            report += f"\n⚠️ <b>Пропущенные темы:</b>\n"
            for name in skipped_names[:5]:
                report += f"• {name}\n"
            if len(skipped_names) > 5:
                report += f"• ... и ещё {len(skipped_names) - 5}\n"
        
        await message.answer(report, parse_mode='HTML')
        
        # Уведомляем всех пользователей о новых темах
        if added > 0:
            users = await rq.get_users()
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.tg_id,
                        text=f'╔═══════════════════════════╗\n'
                             f'║  ⭐ <b>НОВАЯ ТЕМА!</b> ⭐  ║\n'
                             f'╚═══════════════════════════╝\n\n'
                             f'🎓 <i>Добавлен свежий материал!</i> 🎓\n\n'
                             f'📚 <b>Предмет:</b> {subject_name}\n'
                             f'📖 <b>Новых тем:</b> {added}\n\n'
                             f'🚀 Начните обучение сейчас!\n'
                             f'💪 Расширяйте свои знания!\n\n'
                             f'⚡ <b>Уровень мастерства ждёт вас!</b>',
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


# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def create_subjects_example():
    """Создаёт пример Excel файла для предметов"""
    df = pd.DataFrame({
        'Название': [
            'Математика',
            'Физика',
            'Информатика',
            'Химия',
            'Биология'
        ]
    })
    
    filename = 'example_subjects.xlsx'
    df.to_excel(filename, index=False, header=False)
    return filename


def create_themes_example():
    """Создаёт пример Excel файла для тем"""
    df = pd.DataFrame({
        'Название': [
            'Введение в предмет',
            'Основные понятия',
            'Практические задания',
            'Контрольная работа'
        ],
        'Описание': [
            'Первое знакомство с предметом и его основами',
            'Изучение базовых терминов и определений',
            'Закрепление знаний на практике',
            'Проверка усвоенного материала'
        ]
    })
    
    filename = 'example_themes.xlsx'
    df.to_excel(filename, index=False, header=False)
    return filename


# ===== ИМПОРТ ВОПРОСОВ =====

@bulk_import.message(F.text == '📁 Импорт вопросов', AdminProtect())
async def start_questions_import(message: Message, state: FSMContext):
    """Начало процесса массового импорта вопросов"""
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
    example_file = await create_questions_example()  # ДОБАВИЛ await ТУТ!
    await message.answer_document(
        FSInputFile(example_file),
        caption="📄 Пример файла для импорта вопросов"
    )
    os.remove(example_file)
    
    await state.set_state('importing_questions_file')


@bulk_import.message(StateFilter('importing_questions_file'), F.document, AdminProtect())
async def process_questions_file(message: Message, state: FSMContext, bot: Bot):
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
    # Получаем реальные данные из БД для примера
    subjects = await rq.get_subjects()
    themes = await rq.get_themes()
    
    # Если есть данные в БД, используем их
    if subjects and themes:
        subject = list(subjects)[0]
        theme = next((t for t in themes if t.subject_id == subject.id), list(themes)[0])
        
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


# Отменить импорт
@bulk_import.message(F.text == '❌ Отмена', StateFilter('importing_subjects_file', 'importing_themes_file', 'selecting_subject_for_import', 'importing_questions_file'), AdminProtect())
async def cancel_import(message: Message, state: FSMContext):
    """Отмена импорта"""
    await state.clear()
    await message.answer("❌ Импорт отменён.", reply_markup=kb.admin_kb)