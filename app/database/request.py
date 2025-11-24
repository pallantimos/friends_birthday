from datetime import date, datetime
from app.database.models import async_session
from app.database.models import People
from sqlalchemy import extract, select
from app.schemas.people_creation import PeopleCreationSchema


async def add(user_id, data):
    """Добавляет в базу данных человека"""
    async with async_session() as session:
        result = "Данные успешно добавлены"

        try:
            new_people = PeopleCreationSchema.model_validate(data)
            print(new_people.model_dump)
        except ValueError as e:
            e.errors()[0]["msg"]
            return e.errors()[0]["msg"].split(",", 1)[1]

        date_birth = date(
            int(data["date_birth"][-4:]),
            int(data["date_birth"][3:5]),
            int(data["date_birth"][:2]),
        )

        session.add(
            People(
                user_id=user_id,
                name=data["name"],
                date_birth=date_birth,
            )
        )

        await session.commit()
        return result


async def get_birthday(user_id):
    """Получить человека по его telegram id"""
    async with async_session() as session:
        birthdays = await session.execute(
            select(People).where(
                People.user_id == user_id,
            )
        )
        print(user_id)
        birthdays = birthdays.scalars().all()
        return birthdays


async def get_person_by_id(people_id):
    """Получить человека по id"""
    async with async_session() as session:
        results = await session.execute(
            select(People).where(
                People.id == people_id,
            )
        )
        results = results.scalars().all()
        return results


async def get_upcoming_birthdays():
    """ "Проверяет у кого ближайший день рождения"""
    alerts = []
    today_date = date.today()
    today_date = date(2000, today_date.month, today_date.day)

    async with async_session() as session:
        persons = await session.execute(select(People))

    persons = persons.scalars().all()

    for person in persons:
        birth_date = date(2000, person.date_birth.month, person.date_birth.day)
        if 0 < (birth_date - today_date).days <= 3:
            alerts.append(person)

    return alerts


async def delete_person(person_id: int):
    """ "Удалить человека по ID"""
    async with async_session() as session:
        result = await session.execute(
            select(People).where(
                People.id == person_id,
            )
        )
        person = result.scalars().one_or_none()

        if person:
            await session.delete(person)
            await session.commit()
            return True
        return False
