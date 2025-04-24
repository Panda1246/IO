from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from app.extensions import db

from .charity_campaign import organization_campaign_association


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    approved = db.Column(db.Boolean, default=False)
    address = relationship('Address')
    address_id = mapped_column(ForeignKey('address.id'))
    charity_campaigns = relationship('CharityCampaign',
                                     secondary=organization_campaign_association,
                                     back_populates='organizations')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def get_approve_status(self):
        return self.approved

    def approve(self):
        self.approved = True
        db.session.commit()

    def disapprove(self):
        self.approved = False
        db.session.commit()

    def __repr__(self):
        return f'Organization(id={self.id}, organization_name={self.organization_name}, description={self.description})'
