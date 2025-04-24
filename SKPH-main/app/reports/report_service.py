from collections import Counter
from datetime import datetime

from app.extensions import db
from app.models.affected import Affected
from app.models.charity_campaign import OrganizationCharityCampaign, CharityCampaign
from app.models.donation import DonationItem, DonationMoney, DonationType
from app.models.donor import Donor
from app.models.organization import Organization
from app.models.request import Request
from app.models.resource_report import ResourceReport
from app.models.volunteer import Volunteer


class ReportService:
    def __init__(self):
        self._reports = []
        self._next_id = 1

    def generate_report(self):
        affected_list = db.session.query(Affected).all()

        needs_counter = Counter()
        for aff in affected_list:
            if aff.needs:
                needs_counter[aff.needs] += 1
            else:
                needs_counter["(no needs)"] += 1

        entries = []
        for need_value, count in needs_counter.items():
            entries.append({
                "resource_name": need_value,
                "quantity": count,
                "location": "N/A"
            })

        new_report = ResourceReport(
            report_id=self._next_id,
            created_at=datetime.now(),
            entries=entries
        )

        self._reports.append(new_report)
        self._next_id += 1

        return new_report

    def get_all_reports(self):
        return self._reports

    def get_report_by_id(self, report_id):
        for rep in self._reports:
            if rep.report_id == report_id:
                return rep
        return None

    # ====== Affected statystyki =======
    def stats_by_city(self):
        data = {}
        affected_list = db.session.query(Affected).all()
        for aff in affected_list:
            city = aff.address.city if aff.address else "Brak"
            data[city] = data.get(city, 0) + 1
        return data

    def stats_by_voivodeship(self):
        data = {}
        affected_list = db.session.query(Affected).all()
        for aff in affected_list:
            voiv = aff.address.voivodeship if aff.address else "Brak"
            data[voiv] = data.get(voiv, 0) + 1
        return data

    def stats_by_needs(self):
        data = {}
        affected_list = db.session.query(Affected).all()
        for aff in affected_list:
            n = aff.needs if aff.needs else "Brak"
            data[n] = data.get(n, 0) + 1
        return data

    # ====== Request statystyki =======
    def stats_request_by_status(self):
        data = {}
        requests_list = db.session.query(Request).all()
        for req in requests_list:
            status_str = req.status.value  # np. 'Pending', 'Approved'
            data[status_str] = data.get(status_str, 0) + 1
        return data

    # ====== Volunteer statystyki =======
    def stats_by_city_volunteer(self):
        data = {}
        volunteers = db.session.query(Volunteer).all()
        for vol in volunteers:
            city = vol.address.city if vol.address else "Brak"
            data[city] = data.get(city, 0) + 1
        return data

    def stats_volunteer_task_count(self):
        data = {}
        volunteers = db.session.query(Volunteer).all()
        for vol in volunteers:
            count_tasks = len(vol.tasks)
            label = f"{count_tasks} zadań"
            data[label] = data.get(label, 0) + 1
        return data

    def get_all_volunteers(self):
        return db.session.query(Volunteer).all()

    # ====== Donor statystyki =======
    def get_all_donors(self):
        return db.session.query(Donor).all()

    def stats_donation_type_count(self):
        money_count = db.session.query(DonationMoney).count()
        item_count = db.session.query(DonationItem).count()
        return {
            "Money donations": money_count,
            "Item donations": item_count
        }

    def stats_donation_sums(self):
        total_money = db.session.query(db.func.sum(DonationMoney.cashAmount)).scalar() or 0
        total_items = db.session.query(db.func.sum(DonationItem.amount)).scalar() or 0
        return {
            "Total money sum": float(total_money),
            "Total item sum": float(total_items)
        }

    def stats_donation_items_by_type(self):
        data = {}
        rows = (
            db.session.query(
                DonationItem.amount,
                DonationType.type
            )
            .join(DonationType, DonationItem.donation_type_id == DonationType.id)
            .all()
        )
        for (amt, dt_type) in rows:
            data[dt_type] = data.get(dt_type, 0) + amt
        return data

    def stats_donation_money_by_campaign(self):
        data = {}
        money_rows = (
            db.session.query(DonationMoney)
            .join(OrganizationCharityCampaign, DonationMoney.charity_campaign_id == OrganizationCharityCampaign.id)
            .join(CharityCampaign, OrganizationCharityCampaign.charity_campaign_id == CharityCampaign.id)
            .all()
        )
        for dm in money_rows:
            # dm.charity_campaign to OrganizationCharityCampaign
            # dm.charity_campaign.charity_campaign to CharityCampaign
            camp = dm.charity_campaign.charity_campaign
            camp_name = camp.name if camp else "Brak kampanii"
            data[camp_name] = data.get(camp_name, 0) + dm.cashAmount
        return data

    # ====== Organization statystyki =======
    def stats_organization_approval(self):
        approved_count = db.session.query(Organization).filter_by(approved=True).count()
        not_approved_count = db.session.query(Organization).filter_by(approved=False).count()
        return {
            "Approved": approved_count,
            "Not approved": not_approved_count
        }

    def get_all_organizations(self):
        return db.session.query(Organization).all()

    def count_campaigns_per_organization(self, org: Organization) -> int:
        return db.session.query(OrganizationCharityCampaign).filter_by(organization_id=org.id).count()

    def count_volunteers_per_organization(self, org: Organization) -> int:
        org_campaigns = db.session.query(OrganizationCharityCampaign).filter_by(organization_id=org.id).all()
        volunteers_set = set()
        for oc in org_campaigns:
            for vol in oc.volunteers:
                volunteers_set.add(vol.id)
        return len(volunteers_set)

    def get_campaigns_for_organization(self, org: Organization):
        return (
            db.session.query(OrganizationCharityCampaign)
            .filter_by(organization_id=org.id)
            .all()
        )
