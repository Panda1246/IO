from flask import request
from flask_babel import Babel
from flask_mailman import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def get_locale():
    return request.cookies.get('lang', 'pl')


db = SQLAlchemy(model_class=Base)
babel = Babel()
mail = Mail()
