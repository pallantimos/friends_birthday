from pydantic import BaseModel, field_validator, ValidationError
from datetime import date, datetime
import re


class PeopleCreationSchema(BaseModel):
    date_birth: str
    name: str

    @field_validator("date_birth")
    @classmethod
    def date_birth(cls, value):
        try:
            value_year = int(value[-4:])
            value_month = int(value[3:5])
            value_day = int(value[:2])

            value_date = date(value_year, value_month, value_day)
        except Exception as e:
            raise ValueError("Некорректный формат даты рождения")

        if not re.match(r"\d{2}\.\d{2}\.\d{4}$", value):
            raise ValueError("Некорректный формат даты рождения")
        if value_date > date.today():
            raise ValueError("Некорректная дата рождения")
        if value_year < date.today().year - 200:
            raise ValueError("Некорректная дата рождения")

        return value

    @field_validator("name")
    @classmethod
    def name(cls, value: str):
        if bool(re.search(r"[\d\W_]", value)):
            raise ValueError("Некорректное имя")

        return value
