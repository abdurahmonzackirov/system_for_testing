from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

import app.database.requests as rq


test_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Сдать тест')]
],
                              resize_keyboard=True)


answers = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='А', callback_data='a'),
     InlineKeyboardButton(text='Б', callback_data='b'),
     InlineKeyboardButton(text='В', callback_data='c'),
     InlineKeyboardButton(text='Г', callback_data='d')],
    [InlineKeyboardButton(text='⏹️ Завершить тест', callback_data='finish_test')]
])


# Добавьте эту обновлённую клавиатуру в ваш файл app/keyboards.py

# Добавьте эту обновлённую клавиатуру в ваш файл app/keyboards.py

admin_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📚 Добавить предмет'),
     KeyboardButton(text='🗑️ Удалить предмет')],
    [KeyboardButton(text='📁 Импорт предметов')],  # НОВАЯ КНОПКА
    [KeyboardButton(text='📖 Добавить тему'),
     KeyboardButton(text='🗑️ Удалить тему')],
    [KeyboardButton(text='📁 Импорт тем')],  # НОВАЯ КНОПКА
    [KeyboardButton(text='❓ Добавить вопрос'),
     KeyboardButton(text='🗑️ Удалить вопрос')],
    [KeyboardButton(text='📁 Импорт вопросов')],  # НОВАЯ КНОПКА
    [KeyboardButton(text='👤 Добавить администратора'),
     KeyboardButton(text='❌ Удалить администратора')]
],
                               resize_keyboard=True
                               )      


main_menu_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📚 Выбрать предмет'), KeyboardButton(text='📖 Изучить темы')],
    [KeyboardButton(text='✏️ Сдать тест'), KeyboardButton(text='📊 Моя статистика')],
    [KeyboardButton(text='🎯 Слабые места'), KeyboardButton(text='⭐ Мой рейтинг')],
    [KeyboardButton(text='🌐 Открыть веб-приложение', web_app={'url': 'https://imts.lovable.app'})]
],
                                    resize_keyboard=True
                                    )

async def get_subjects_kb():
    keyboard = ReplyKeyboardBuilder()
    subjects = await rq.get_subjects()
    for subject in subjects:
        keyboard.add(KeyboardButton(text=subject.name))
    keyboard.add(KeyboardButton(text='← Назад'))
    return keyboard.adjust(2).as_markup(resize_keyboard=True)


async def get_themes_kb(subject_id=None):
    keyboard = InlineKeyboardBuilder()
    if subject_id:
        themes = await rq.get_themes_by_subject(subject_id)
    else:
        themes = await rq.get_themes()
    for theme in themes:
        keyboard.add(InlineKeyboardButton(text=theme.name, callback_data=f'theme_{theme.id}'))
    keyboard.add(InlineKeyboardButton(text='← Назад', callback_data='back_to_menu'))
    return keyboard.adjust(1).as_markup()


async def choose_test_subj():
    keyboard = InlineKeyboardBuilder()
    subjects = await rq.get_subjects()
    for subject in subjects:
        keyboard.add(InlineKeyboardButton(text=subject.name, callback_data=f'subject_{subject.id}'))
    keyboard.add(InlineKeyboardButton(text='← Назад', callback_data='back_to_menu'))
    return keyboard.adjust(1).as_markup()


async def choose_study_subj():
    keyboard = InlineKeyboardBuilder()
    subjects = await rq.get_subjects()
    for subject in subjects:
        keyboard.add(InlineKeyboardButton(text=subject.name, callback_data=f'study_subject_{subject.id}'))
    keyboard.add(InlineKeyboardButton(text='← Назад', callback_data='back_to_menu'))
    return keyboard.adjust(1).as_markup()


async def subjects_id():
    keyboard = InlineKeyboardBuilder()
    subject_ids = await rq.get_subjects()
    for subject in subject_ids:
        keyboard.add(InlineKeyboardButton(text=str(subject.id), callback_data=f'subject_{subject.id}'))
    return keyboard.adjust(1).as_markup()


async def get_subjects():
    keyboard = InlineKeyboardBuilder()
    subjects = await rq.get_subjects()
    for subject in subjects:
        keyboard.add(InlineKeyboardButton(text=subject.name, callback_data='empty_data'))
    return keyboard.adjust(1).as_markup()


async def themes_id():
    keyboard = InlineKeyboardBuilder()
    theme_ids = await rq.get_themes()
    for theme in theme_ids:
        keyboard.add(InlineKeyboardButton(text=str(theme.id), callback_data=f'theme_{theme.id}'))
    return keyboard.adjust(1).as_markup()


async def themes_by_subject(subject_id):
    keyboard = InlineKeyboardBuilder()
    themes = await rq.get_themes_by_subject(subject_id)
    for theme in themes:
        keyboard.add(InlineKeyboardButton(text=theme.name, callback_data='empty_data'))
    return keyboard.adjust(1).as_markup()


async def get_themes_by_subject(subject_id):
    keyboard = InlineKeyboardBuilder()
    themes = await rq.get_themes_by_subject(subject_id)
    for theme in themes:
        keyboard.add(InlineKeyboardButton(text=theme.name, callback_data=f'theme_{theme.id}'))
    return keyboard.adjust(1).as_markup()


async def tests_by_theme(theme_id):
    keyboard = InlineKeyboardBuilder()
    tests = await rq.get_tests_by_theme_id(theme_id)
    for test in tests:
        keyboard.add(InlineKeyboardButton(text=test.name, callback_data='empty_data'))
    return keyboard.adjust(1).as_markup()


async def clients_name(name):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=name)]
    ],
                               resize_keyboard=True
                               )


async def get_theme_back_kb():
    """Клавиатура с кнопкой 'Назад' для просмотра темы"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='← Назад к темам', callback_data='back_to_menu'))
    return keyboard.adjust(1).as_markup()


async def get_users_kb():
    """Клавиатура для выбора пользователя (админ-панель)"""
    keyboard = InlineKeyboardBuilder()
    users = await rq.get_users()
    for user in users:
        keyboard.add(InlineKeyboardButton(text=user.name, callback_data=f'user_{user.tg_id}'))
    return keyboard.adjust(1).as_markup()


async def get_weak_themes_kb(theme_ids):
    """Клавиатура для рекомендационных тестов по слабым темам"""
    keyboard = InlineKeyboardBuilder()
    for theme_id in theme_ids:
        theme = await rq.get_theme(theme_id)
        keyboard.add(InlineKeyboardButton(text=theme.name, callback_data=f'weak_theme_{theme_id}'))
    keyboard.add(InlineKeyboardButton(text='← Назад в меню', callback_data='back_to_menu'))
    return keyboard.adjust(1).as_markup()


async def subjects_id():
    """Клавиатура для выбора ID предмета (админ-панель)"""
    keyboard = InlineKeyboardBuilder()
    subjects = await rq.get_subjects()
    for subject in subjects:
        keyboard.add(InlineKeyboardButton(text=subject.name, callback_data=f'subject_{subject.id}'))
    return keyboard.adjust(1).as_markup()


async def themes_id():
    """Клавиатура для выбора ID темы (админ-панель)"""
    keyboard = InlineKeyboardBuilder()
    themes = await rq.get_themes()
    for theme in themes:
        keyboard.add(InlineKeyboardButton(text=theme.name, callback_data=f'theme_{theme.id}'))
    return keyboard.adjust(2).as_markup()


async def get_tests():
    """Клавиатура для выбора теста (админ-панель)"""
    keyboard = InlineKeyboardBuilder()
    tests = await rq.get_tests()
    for test in tests:
        keyboard.add(InlineKeyboardButton(text=test.name, callback_data=f'empty_data'))
    return keyboard.adjust(2).as_markup()


async def get_themes():
    """Клавиатура для выбора темы (админ-панель)"""
    keyboard = InlineKeyboardBuilder()
    themes = await rq.get_themes()
    for theme in themes:
        keyboard.add(InlineKeyboardButton(text=theme.name, callback_data=f'empty_data'))
    return keyboard.adjust(2).as_markup()