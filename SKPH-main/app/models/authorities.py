from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column

from app.extensions import db


class Authorities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    address = relationship('Address')
    address_id = mapped_column(ForeignKey('address.id'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'Authorities(id={self.id} name={self.name})'

    def get_approve_status(self):
        return self.approved

    def approve(self):
        self.approved = True
        db.session.commit()

    def disapprove(self):
        self.approved = False
        db.session.commit()
