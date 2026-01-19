from sqlalchemy import ForeignKey, BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs


engine = create_async_engine(url='sqlite+aiosqlite:///yandex.db')
async_session = async_sessionmaker(engine)


class Base(DeclarativeBase, AsyncAttrs):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(25), nullable=True)
    total_mark: Mapped[int] = mapped_column(nullable=True, default=0)
    mark_for_chemistry: Mapped[int] = mapped_column(nullable=True, default=0)
    mark_for_math: Mapped[int] = mapped_column(nullable=True, default=0)
    marks_by_subject: Mapped[str] = mapped_column(String(10000), nullable=True)  # JSON для баллов по всем предметам {subject_id: score}
    need_practice_subject: Mapped[str] = mapped_column(String(256), nullable=True)
    need_practice_theme: Mapped[str] = mapped_column(String(256), nullable=True)
    errors_by_theme: Mapped[str] = mapped_column(String(10000), nullable=True)  # JSON для отслеживания ошибок
    
    
class Admin(Base):
    __tablename__ = 'admins'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    

class Subject(Base):
    __tablename__ = 'subjects'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    

class Theme(Base):
    __tablename__ = 'themes'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(String(1000000), nullable=True)
    

class Test(Base):
    __tablename__ = 'tests'

    id: Mapped[int] = mapped_column(primary_key=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey('themes.id'))
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    question: Mapped[str] = mapped_column(String(520), nullable=True)
    answer1: Mapped[str] = mapped_column(String(20), nullable=True)
    answer2: Mapped[str] = mapped_column(String(20), nullable=True)
    answer3: Mapped[str] = mapped_column(String(20), nullable=True)
    answer4: Mapped[str] = mapped_column(String(20), nullable=True)
    point: Mapped[int] = mapped_column(nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(20), nullable=True)
    

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)