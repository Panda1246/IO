from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Task(db.Model):

    AVAILABLE_STATUS = ('completed', 'ongoing', 'rejected')

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    status = mapped_column(Enum(*AVAILABLE_STATUS, name='task_status'), default='ongoing', nullable=False)
    charity_campaign_id = mapped_column(ForeignKey('organization_charity_campaign.id'))
    volunteer_id = mapped_column(ForeignKey('volunteer.id'))
    evaluation_id = mapped_column(ForeignKey('evaluation.id'))

    evaluation_ = relationship('Evaluation')
    volunteer = relationship('Volunteer', back_populates='tasks')

    def __repr__(self):
        return (
            f'Task:(id={self.id!r}, name={self.name!r}, '
            f'description={self.description!r}, volunteer_id={self.volunteer_id!r})'
        )
