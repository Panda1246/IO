from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from .charity_campaign import volunteer_campaign_association


class Volunteer(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str] = mapped_column(unique=True)
    address = relationship('Address')
    address_id = mapped_column(ForeignKey('address.id'))
    user_id = mapped_column(ForeignKey('users.id'))

    tasks = relationship('Task', back_populates='volunteer')
    campaigns = (
        relationship('OrganizationCharityCampaign',
                     secondary=volunteer_campaign_association,
                     back_populates='volunteers')
    )

    def __repr__(self):
        return f'Volunteer:(id={self.id!r}, first_name={self.first_name!r}, last_name={self.last_name!r}\
                 email={self.email!r}, phone={self.phone!r}, address_id={self.address_id!r})'
