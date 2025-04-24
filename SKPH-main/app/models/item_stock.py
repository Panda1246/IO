from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class ItemStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_type_id = db.Column(db.Integer, ForeignKey('donation_type.id'), nullable=False)
    organization_charity_campaign_id: Mapped[int] = mapped_column(ForeignKey('organization_charity_campaign.id'))
    organization_charity_campaign = relationship('OrganizationCharityCampaign')
    item_type = relationship('DonationType')
    amount = db.Column(db.Integer)
