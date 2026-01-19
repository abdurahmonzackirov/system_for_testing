from app.database.models import async_session
from app.database.models import User, Subject, Test, Theme, Admin
from sqlalchemy import select, update, insert, delete


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


@connection
async def set_user(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    
    if not user:
        session.add(User(tg_id=tg_id))
        await session.commit()
        return False
    return True if user.name else False


@connection
async def get_user(session, tg_id):
    return await session.scalar(select(User).where(User.tg_id == tg_id))


@connection
async def get_admins(session):
    return await session.scalars(select(Admin))


@connection
async def get_admin(session, tg_id):
    return await session.scalar(select(Admin).where(Admin.tg_id == tg_id))


@connection
async def add_admin(session, tg_id):
    await session.execute(insert(Admin).values(tg_id=tg_id))
    await session.commit()
    
    
@connection
async def delete_admin(session, tg_id):
    await session.execute(delete(Admin).where(Admin.tg_id == tg_id))
    await session.commit()


@connection
async def get_users(session):
    return await session.scalars(select(User))


@connection
async def update_user(session, tg_id, name=None, total_mark=None, mark_for_chemistry=None, mark_for_math=None, marks_by_subject=None):
    """Обновить информацию пользователя"""
    update_data = {}
    if name is not None:
        update_data['name'] = name
    if total_mark is not None:
        update_data['total_mark'] = total_mark
    if mark_for_chemistry is not None:
        update_data['mark_for_chemistry'] = mark_for_chemistry
    if mark_for_math is not None:
        update_data['mark_for_math'] = mark_for_math
    if marks_by_subject is not None:
        update_data['marks_by_subject'] = marks_by_subject
    
    if update_data:
        await session.execute(update(User).where(User.tg_id == tg_id).values(**update_data))
        await session.commit()


@connection
async def update_user_errors(session, tg_id, errors_json):
    """Обновить информацию об ошибках пользователя"""
    await session.execute(update(User).where(User.tg_id == tg_id).values(errors_by_theme=errors_json))
    await session.commit()
    
    
@connection
async def get_subjects(session):
    return await session.scalars(select(Subject))
    

@connection
async def get_themes(session):
    return await session.scalars(select(Theme))


@connection
async def get_themes_by_subject(session, subject_id):
    return await session.scalars(select(Theme).where(Theme.subject_id == subject_id))
    

@connection
async def get_theme(session, theme_id):
    return await session.scalar(select(Theme).where(Theme.id == theme_id))
    

@connection
async def get_test(session, test_id):
    return await session.scalar(select(Test).where(Test.id == test_id))


@connection
async def get_tests(session):
    return await session.scalars(select(Test))


@connection
async def get_tests(session, theme_id):
    return await session.scalars(select(Test).where(Test.theme_id == theme_id))


@connection
async def add_subject(session, name):
    session.add(Subject(name=name))
    await session.commit()
    

@connection
async def add_theme(session, subject_id, name, description):
    session.add(Theme(
        subject_id=subject_id,
        name=name,
        description=description
    ))
    await session.commit()
    
    
@connection
async def add_test(session, theme_id, subject_id, name, question, answer1, answer2, answer3, answer4, point, correct_answer):
    session.add(Test(
        theme_id=theme_id,
        subject_id=subject_id,
        name=name,
        question=question,
        answer1=answer1,
        answer2=answer2,
        answer3=answer3,
        answer4=answer4,
        point=point,
        correct_answer=correct_answer
    ))
    await session.commit()
    

@connection
async def delete_subject(session, subject_id):
    await session.execute(delete(Subject).where(Subject.id == subject_id))
    await session.commit()


@connection
async def delete_theme(session, theme_id):
    await session.execute(delete(Theme).where(Theme.id == theme_id))
    await session.commit()
    

@connection
async def delete_test(session, test_id):
    await session.execute(delete(Test).where(Test.id == test_id))
    await session.commit()
    

@connection
async def get_subject(session, subject_id):
    return await session.scalar(select(Subject).where(Subject.id == subject_id))


@connection
async def get_tests_by_subject(session, subject_id):
    return await session.scalars(select(Test).where(Test.subject_id == subject_id))


@connection
async def get_tests_by_theme(session, theme_id):
    return await session.scalars(select(Test).where(Test.theme_id == theme_id))


@connection
async def get_tests_by_themes(session, theme_ids):
    """Получить тесты по списку тем"""
    return await session.scalars(select(Test).where(Test.theme_id.in_(theme_ids)))


@connection
async def get_all_tests(session):
    return await session.scalars(select(Test))