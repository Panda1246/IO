from enum import Enum

from flask_babel import lazy_gettext as _
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLEnum

from app.extensions import db


class RequestStatus(Enum):
    PENDING = _("Pending")
    APPROVED = _("Approved")
    REJECTED = _("Not approved")
    COMPLETED = _("Completed")


class Request(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    amount: Mapped[int]
    status: Mapped[RequestStatus] = mapped_column(SQLEnum(RequestStatus), nullable=False)
    req_address = relationship('Address')
    req_address_id = mapped_column(ForeignKey('address.id'))
    affected_id = mapped_column(ForeignKey('affected.id'))
    donation_type_id = mapped_column(ForeignKey('donation_type.id'))
    amount: Mapped[int]

    affected = relationship('Affected', back_populates='requests')
    donation_type = relationship('DonationType')

    def __repr__(self):
        return (
            f'Request:(id={self.id!r}, name={self.name!r}, '
            f'status={self.status.value!r}, needs={self.needs.value!r}, '
            f'quantity={self.quantity!r}, affected_id={self.affected_id!r})'
        )
