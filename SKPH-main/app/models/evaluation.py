from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Evaluation(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[int]
    description: Mapped[str]

    def __repr__(self):
        return f'Evaluation(id={self.id!r}, score={self.score!r}, description={self.description!r})'
