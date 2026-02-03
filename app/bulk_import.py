from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
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


# Отменить импорт
@bulk_import.message(F.text == '❌ Отмена', StateFilter('importing_subjects_file', 'importing_themes_file', 'selecting_subject_for_import'), AdminProtect())
async def cancel_import(message: Message, state: FSMContext):
    """Отмена импорта"""
    await state.clear()
    await message.answer("❌ Импорт отменён.", reply_markup=kb.admin_kb)