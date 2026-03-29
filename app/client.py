from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

import app.database.requests as rq
import app.keyboards as kb
import json


client = Router()


class NavigationStates(StatesGroup):
    main_menu = State()
    choosing_subject_for_study = State()
    viewing_theme = State()
    choosing_subject_for_test = State()
    test_in_progress = State()
    weak_test_in_progress = State()


@client.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    is_user = await rq.set_user(message.from_user.id)
    
    if not is_user:
        await message.answer('🎓 Добро пожаловать в систему тестирования!',
                             reply_markup=await kb.clients_name(message.from_user.first_name))
        await message.answer(
            'Эта система поможет вам:\n'
            '✅ Проверить знания по разным предметам\n'
            '✅ Определить слабые места\n'
            '✅ Получить персональные рекомендации\n'
            '✅ Улучшить свой балл\n\n'
            'Введите ваше имя для начала работы:',
            reply_markup=await kb.clients_name(message.from_user.first_name)
            
        )
        await state.set_state('reg_name')
    else:
        await state.set_state(NavigationStates.main_menu)
        await message.answer(
            f'👋 С возвращением!\n\n'
            f'Выберите действие:',
            reply_markup=kb.main_menu_kb
        )
        
    
@client.message(Command('help'))
async def client_help(message: Message):
    now = datetime.now()
    print(f'User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime("%d.%m.%Y")}, Время: {now.strftime("%H:%M:%S")}: {message.text}')
    await message.answer('📋 <b>ДОСТУПНЫЕ КОМАНДЫ:</b>\n\n/start - 🚀 Запуск бота\n/help - ℹ️ Команды бота\n', parse_mode='HTML')
        

@client.message(StateFilter('reg_name'))
async def reg_name(message: Message, state: FSMContext):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    await state.update_data(name=message.text.capitalize())
    data = await state.get_data()
    await rq.update_user(tg_id=message.from_user.id, name=data['name'])
    await message.answer(
        f'✅ Регистрация завершена, {data["name"]}!\n\n'
        f'Теперь вы можете начать обучение. Выберите действие:',
        reply_markup=kb.main_menu_kb
    )
    await state.clear()


@client.message(F.text == 'Химия')
async def chemistry_subject(message: Message):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    await message.answer('Выберите тему по Химии', reply_markup=await kb.get_themes_kb(subject_id=1))


@client.message(F.text == 'Математика')
async def math_subject(message: Message):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    await message.answer('Выберите тему по Математике', reply_markup=await kb.get_themes_kb(subject_id=2))


@client.message(F.text == '📚 Выбрать предмет')
async def choose_subject(message: Message, state: FSMContext):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    await state.set_state(NavigationStates.choosing_subject_for_study)
    await message.answer('Выберите предмет для изучения:', reply_markup=await kb.get_subjects_kb())


@client.message(F.text == '← Назад')
async def go_back(message: Message, state: FSMContext):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    current_state = await state.get_state()
    
    if current_state == NavigationStates.choosing_subject_for_study:
        await state.set_state(NavigationStates.main_menu)
        await message.answer(
            '👈 Вы вернулись в главное меню.\n\nВыберите действие:',
            reply_markup=kb.main_menu_kb
        )


@client.message(F.text == '📖 Изучить темы')
async def study_themes(message: Message, state: FSMContext):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    await state.set_state(NavigationStates.choosing_subject_for_study)
    await message.answer(
        '📖 Выберите предмет для изучения тем:',
        reply_markup=await kb.choose_study_subj()
    )


@client.message(F.text == '✏️ Сдать тест')
async def pass_test(message: Message, state: FSMContext):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    await state.set_state(NavigationStates.choosing_subject_for_test)
    await message.answer('✏️ Выберите предмет для прохождения теста:', reply_markup=await kb.choose_test_subj())


@client.message(F.text == '📊 Моя статистика')
async def my_statistics(message: Message):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    user = await rq.get_user(tg_id=message.from_user.id)
    total_mark = user.total_mark or 0
    
    stats = (
        f'📊 ВАША СТАТИСТИКА\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n\n'
        f'Общий балл: {total_mark} баллов\n\n'
        f'По предметам:\n'
    )
    
    # Получаем все предметы и показываем баллы по каждому
    subjects = await rq.get_subjects()
    marks_by_subject = {}
    if user.marks_by_subject:
        marks_by_subject = json.loads(user.marks_by_subject)
    
    if subjects:
        for subject in subjects:
            subject_mark = int(marks_by_subject.get(str(subject.id), 0))
            subject_tests = subject_mark // 10 if subject_mark > 0 else 0
            stats += f'• {subject.name}: {subject_mark} баллов ({subject_tests} тестов)\n'
    else:
        stats += '📚 Нет предметов в системе\n'
    
    await message.answer(stats)


@client.message(F.text == '🎯 Слабые места')
async def weak_places(message: Message):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    user = await rq.get_user(tg_id=message.from_user.id)
    
    if not user.errors_by_theme:
        await message.answer(
            '✅ Отлично! У вас пока нет слабых мест.\n'
            'Продолжайте решать тесты, чтобы система могла анализировать ваш прогресс.'
        )
        return
    
    errors = json.loads(user.errors_by_theme)
    if not errors:
        await message.answer(
            '✅ Отлично! У вас пока нет слабых мест.\n'
            'Продолжайте решать тесты, чтобы система могла анализировать ваш прогресс.'
        )
        return
    
    weak_text = '🎯 ВАШИ СЛАБЫЕ МЕСТА\n━━━━━━━━━━━━━━━━━━━━━━\n\n'
    sorted_errors = sorted(errors.items(), key=lambda x: int(x[1]), reverse=True)
    
    for theme_id_str, error_count in sorted_errors[:5]:
        try:
            theme = await rq.get_theme(int(theme_id_str))
            weak_text += f'• {theme.name}: {error_count} ошибок\n'
        except:
            pass
    
    weak_text += '\n💡 Рекомендация: Повторите эти темы в разделе "Изучить темы"'
    await message.answer(weak_text)


@client.message(F.text == '⭐ Мой рейтинг')
async def my_rating(message: Message):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    user = await rq.get_user(tg_id=message.from_user.id)
    mark = user.total_mark or 0
    
    # Определяем уровень пользователя
    if mark < 50:
        level = '🔴 Начинающий'
        progress = f'{mark}/100'
    elif mark < 150:
        level = '🟡 Практикант'
        progress = f'{mark}/200'
    elif mark < 300:
        level = '🟢 Учащийся'
        progress = f'{mark}/300'
    elif mark < 500:
        level = '🔵 Отличник'
        progress = f'{mark}/500'
    else:
        level = '⭐ Мастер'
        progress = f'{mark}/500+'
    
    rating_text = (
        f'⭐ ВАШ РЕЙТИНГ\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n\n'
        f'Уровень: {level}\n'
        f'Баллов: {progress}\n\n'
        f'Совет: Решайте больше тестов, чтобы увеличить свой рейтинг!'
    )
    await message.answer(rating_text)


@client.message(F.text == 'Моя успеваемость')
async def study(message: Message):
    now = datetime.now()
    print(f"User {message.from_user.first_name}({message.from_user.id}) send message at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {message.text}")
    user = await rq.get_user(tg_id=message.from_user.id)
    mark = user.total_mark or 0
    chemistry_mark = user.mark_for_chemistry or 0
    math_mark = user.mark_for_math or 0
    
    await message.answer(
        f'📈 ВАША УСПЕВАЕМОСТЬ\n\n'
        f'Общий балл: {mark}\n'
        f'Балл по химии: {chemistry_mark}\n'
        f'Балл по математике: {math_mark}'
    )
    
    if chemistry_mark <= 26 and math_mark <= 26:
        await message.answer("❌ Вам нужно подтянуть химию и математику, побольше читайте темы")
    elif math_mark <= 26:
        await message.answer('❌ Вам нужно подтянуть математику, побольше учите формулы (особенно связанные с тригонометрией)')
    elif chemistry_mark <= 26:
        await message.answer('❌ Вам нужно подтянуть химию, побольше учите про электроны (особенно конфигурацию)')
    else:
        await message.answer('✅ Вау, у вас со всеми предметами всё отлично, вы прям гений!)')


@client.callback_query(F.data.startswith('theme_'))
async def themes(callback: CallbackQuery, state: FSMContext):
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    await callback.answer()
    await state.set_state(NavigationStates.viewing_theme)
    theme_id = callback.data.split('_')[1]
    theme = await rq.get_theme(theme_id=theme_id)
    
    # Форматируем контент темы красиво
    theme_content = (
        f'📚 {theme.name}\n'
        f'{"=" * 50}\n\n'
        f'{theme.description}\n\n'
        f'{"=" * 50}\n'
        f'💡 Совет: Прочитайте материал и попробуйте пройти тест на эту тему!'
    )
    
    await callback.message.answer(theme_content, reply_markup=await kb.get_theme_back_kb())
    

@client.callback_query(F.data.startswith('study_subject_'))
async def study_subject(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    subject_id = int(callback.data.split('_')[2])
    await state.update_data(studying_subject_id=subject_id)
    await callback.message.answer(
        f'📖 Выберите тему для изучения:',
        reply_markup=await kb.get_themes_kb(subject_id=subject_id)
    )


@client.callback_query(F.data.startswith('subject_'))
async def start_test(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    subject_id = int(callback.data.split('_')[1])
    
    # Получаем все тесты по предмету
    tests = await rq.get_tests_by_subject(subject_id)
    tests_list = list(tests)
    
    if not tests_list:
        await callback.message.answer('❌ Тестов для этого предмета не найдено')
        return
    
    # Берём первые 10 вопросов (или все, если меньше)
    test_ids = [test.id for test in tests_list[:10]]
    
    await state.set_state(NavigationStates.test_in_progress)
    await state.update_data(
        test_ids=test_ids,
        current_question=0,
        subject_id=subject_id,
        answers=[],
        test_objects=tests_list[:10]
    )
    
    # Показываем первый вопрос
    await show_question(callback, state)


async def show_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_q = data['current_question']
    test_objects = data['test_objects']
    
    if current_q >= len(test_objects):
        # Тест закончился - показываем результаты
        await show_test_results(callback, state)
        return
    
    test = test_objects[current_q]
    question_num = current_q + 1
    
    question_text = (
        f'❓ Вопрос {question_num}/10\n\n'
        f'{test.name}\n\n'
        f'{test.question}\n\n'
        f'A) {test.answer1}\n'
        f'Б) {test.answer2}\n'
        f'В) {test.answer3}\n'
        f'Г) {test.answer4}'
    )
    
    # Для первого вопроса используем answer, для остальных edit_text
    if current_q == 0:
        await callback.message.answer(question_text, reply_markup=kb.answers)
    else:
        try:
            await callback.message.edit_text(question_text, reply_markup=kb.answers)
        except:
            # Если edit_text не работает, используем answer
            await callback.message.answer(question_text, reply_markup=kb.answers)


async def show_test_results(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await rq.get_user(tg_id=callback.from_user.id)
    test_objects = data['test_objects']
    answers = data['answers']
    subject_id = data['subject_id']
    
    # Подсчитываем правильные ответы и ошибки по темам
    correct_count = 0
    theme_errors = {}  # {theme_id: количество ошибок}
    
    for i, (user_answer, test) in enumerate(zip(answers, test_objects)):
        if user_answer == test.correct_answer:
            correct_count += 1
        else:
            theme_id = test.theme_id
            theme_errors[theme_id] = theme_errors.get(theme_id, 0) + 1
    
    # Сохраняем ошибки в профиль пользователя
    current_errors = {}
    if user.errors_by_theme:
        current_errors = json.loads(user.errors_by_theme)
    
    for theme_id, count in theme_errors.items():
        current_errors[str(theme_id)] = current_errors.get(str(theme_id), 0) + count
    
    await rq.update_user_errors(user.tg_id, json.dumps(current_errors))
    
    # Обновляем баллы для любого предмета
    points_earned = correct_count * 10
    
    # Получаем текущие баллы по предметам из JSON
    marks_by_subject = {}
    if user.marks_by_subject:
        marks_by_subject = json.loads(user.marks_by_subject)
    
    # Увеличиваем балл для текущего предмета
    subject_id_str = str(subject_id)
    marks_by_subject[subject_id_str] = marks_by_subject.get(subject_id_str, 0) + points_earned
    
    # Вычисляем общий балл
    new_total_mark = sum(marks_by_subject.values())
    
    # Сохраняем баллы в БД
    await rq.update_user(
        tg_id=user.tg_id,
        total_mark=new_total_mark,
        marks_by_subject=json.dumps(marks_by_subject)
    )
    
    # Формируем результат
    result_text = (
        f'📊 РЕЗУЛЬТАТЫ ТЕСТА\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n\n'
        f'✅ Правильных ответов: {correct_count}/10\n'
        f'⭐ Баллов за этот тест: {points_earned}\n'
        f'🏆 Общий балл: {new_total_mark}\n'
    )
    
    if theme_errors:
        weak_themes = sorted(theme_errors.items(), key=lambda x: x[1], reverse=True)
        result_text += f'\n❌ ОШИБКИ ПО ТЕМАМ:\n'
        
        for theme_id, error_count in weak_themes:
            theme = await rq.get_theme(theme_id)
            result_text += f'• {theme.name}: {error_count} ошибок\n'
        
        result_text += f'\n💡 РЕКОМЕНДАЦИЯ: Повторите тему "{(await rq.get_theme(weak_themes[0][0])).name}"'
    elif correct_count == 10:
        result_text += '\n✅ Отлично! Все ответы правильные!'
    
    await callback.message.answer(result_text)
    
    # Предлагаем пройти рекомендационный тест по слабым темам
    if theme_errors:
        weak_theme_ids = [theme_id for theme_id, _ in weak_themes[:3]]  # Берём 3 слабейшие темы
        await callback.message.answer(
            '🎯 Хотите пройти тест для повторения слабых тем?',
            reply_markup=await kb.get_weak_themes_kb(weak_theme_ids)
        )
    
    await state.clear()


@client.callback_query(F.data == 'a')
async def check_answer_a(callback: CallbackQuery, state: FSMContext):
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    await process_answer(callback, state, 'А')


@client.callback_query(F.data == 'b')
async def check_answer_b(callback: CallbackQuery, state: FSMContext):
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    await process_answer(callback, state, 'Б')


@client.callback_query(F.data == 'c')
async def check_answer_c(callback: CallbackQuery, state: FSMContext):
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    await process_answer(callback, state, 'В')


@client.callback_query(F.data == 'd')
async def check_answer_d(callback: CallbackQuery, state: FSMContext):
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    await process_answer(callback, state, 'Г')


async def process_answer(callback: CallbackQuery, state: FSMContext, answer: str):
    await callback.answer()
    
    current_state = await state.get_state()
    data = await state.get_data()
    
    # Проверяем, находимся ли мы в обычном тесте или рекомендационном
    if current_state == NavigationStates.test_in_progress:
        is_weak_test = False
    elif current_state == NavigationStates.weak_test_in_progress:
        is_weak_test = True
    else:
        return
    
    test_objects = data['test_objects']
    current_q = data['current_question']
    answers = data['answers']
    
    # Сохраняем ответ
    answers.append(answer)
    current_q += 1
    
    await state.update_data(
        answers=answers,
        current_question=current_q
    )
    
    # Показываем следующий вопрос или результаты
    if current_q < len(test_objects):
        if is_weak_test:
            await show_weak_question(callback, state)
        else:
            await show_question(callback, state)
    else:
        if is_weak_test:
            await show_weak_test_results(callback, state)
        else:
            await show_test_results(callback, state)


@client.callback_query(F.data.startswith('weak_theme_'))
async def start_weak_theme_test(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    theme_id = int(callback.data.split('_')[2])
    
    # Получаем все тесты по этой теме
    tests = await rq.get_tests_by_theme(theme_id)
    tests_list = list(tests)
    
    if not tests_list:
        await callback.message.answer('❌ Тестов для этой темы не найдено')
        return
    
    # Берём первые 10 вопросов
    test_ids = [test.id for test in tests_list[:10]]
    
    await state.set_state(NavigationStates.weak_test_in_progress)
    await state.update_data(
        test_ids=test_ids,
        current_question=0,
        theme_id=theme_id,
        answers=[],
        test_objects=tests_list[:10]
    )
    
    await show_weak_question(callback, state)


@client.callback_query(F.data == 'skip_weak')
async def skip_weak_test(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    await callback.message.answer(
        '✅ Рекомендационный тест пропущен.\n\nВыберите действие:',
        reply_markup=kb.main_menu_kb
    )
    await state.clear()


@client.callback_query(F.data == 'back_to_menu')
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    current_state = await state.get_state()
    
    # Если пользователь в просмотре темы - вернуться в выбор тем
    if current_state == NavigationStates.viewing_theme:
        data = await state.get_data()
        subject_id = data.get('studying_subject_id')
        await state.set_state(NavigationStates.choosing_subject_for_study)
        
        if subject_id:
            await callback.message.answer(
                f'📖 Выберите другую тему для изучения:',
                reply_markup=await kb.get_themes_kb(subject_id=subject_id)
            )
        else:
            await callback.message.answer(
                '📖 Выберите предмет:',
                reply_markup=await kb.choose_study_subj()
            )
    
    # Если пользователь выбирал тему - вернуться в выбор предмета для изучения
    elif current_state == NavigationStates.choosing_subject_for_study:
        await state.set_state(NavigationStates.main_menu)
        await callback.message.answer(
            '👈 Вы вернулись в главное меню.\n\nВыберите действие:',
            reply_markup=kb.main_menu_kb
        )
    
    # Если пользователь выбирал тест - вернуться в выбор предмета для теста
    elif current_state == NavigationStates.choosing_subject_for_test:
        await state.set_state(NavigationStates.main_menu)
        await callback.message.answer(
            '👈 Вы вернулись в главное меню.\n\nВыберите действие:',
            reply_markup=kb.main_menu_kb
        )
    
    # По умолчанию - в главное меню
    else:
        await state.set_state(NavigationStates.main_menu)
        await callback.message.answer(
            '👈 Вы вернулись в главное меню.\n\nВыберите действие:',
            reply_markup=kb.main_menu_kb
        )


@client.callback_query(F.data == 'finish_test')
async def finish_test(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    now = datetime.now()
    print(f"User {callback.from_user.first_name}({callback.from_user.id}) send callback at Дата: {now.strftime('%d.%m.%Y')}, Время: {now.strftime('%H:%M:%S')}: {callback.data}")
    current_state = await state.get_state()
    
    if current_state == NavigationStates.test_in_progress:
        await show_test_results(callback, state)
    elif current_state == NavigationStates.weak_test_in_progress:
        await show_weak_test_results(callback, state)


async def show_weak_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_q = data['current_question']
    test_objects = data['test_objects']
    
    if current_q >= len(test_objects):
        await show_weak_test_results(callback, state)
        return
    
    test = test_objects[current_q]
    question_num = current_q + 1
    
    question_text = (
        f'❓ Рекомендационный тест {question_num}/10\n\n'
        f'{test.name}\n\n'
        f'{test.question}\n\n'
        f'A) {test.answer1}\n'
        f'Б) {test.answer2}\n'
        f'В) {test.answer3}\n'
        f'Г) {test.answer4}'
    )
    
    # Для первого вопроса используем answer, для остальных edit_text
    if current_q == 0:
        await callback.message.answer(question_text, reply_markup=kb.answers)
    else:
        try:
            await callback.message.edit_text(question_text, reply_markup=kb.answers)
        except:
            # Если edit_text не работает, используем answer
            await callback.message.answer(question_text, reply_markup=kb.answers)


async def show_weak_test_results(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await rq.get_user(tg_id=callback.from_user.id)
    test_objects = data['test_objects']
    answers = data['answers']
    theme_id = data['theme_id']
    
    # Подсчитываем правильные ответы
    correct_count = sum(1 for user_answer, test in zip(answers, test_objects)
                       if user_answer == test.correct_answer)
    
    points_earned = correct_count * 10
    theme = await rq.get_theme(theme_id)
    
    result_text = (
        f'📊 РЕЗУЛЬТАТЫ РЕКОМЕНДАЦИОННОГО ТЕСТА\n'
        f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n'
        f'📚 Тема: {theme.name}\n'
        f'✅ Правильных ответов: {correct_count}/10\n'
        f'⭐ Баллов за этот тест: {points_earned}\n'
        f'🏆 Общий балл: {user.total_mark or 0}\n'
    )
    
    await callback.message.answer(result_text)
    await state.clear()