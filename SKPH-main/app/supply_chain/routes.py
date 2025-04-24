from datetime import datetime

from flask import Blueprint, redirect, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import cast, VARCHAR

from app.auth.user_service import roles_required
from app.extensions import db
from app.models.address import Address
from app.models.affected import Affected
from app.models.authorities import Authorities
from app.models.charity_campaign import CharityCampaign
from app.models.charity_campaign import OrganizationCharityCampaign
from app.models.donation import DonationItem, DonationMoney, DonationType
from app.models.donor import Donor
from app.models.item_stock import ItemStock
from app.models.organization import Organization
from app.models.request import Request, RequestStatus
from app.models.user import User

bp = Blueprint('supply_chain', __name__,
               template_folder='../templates/supply_chain',
               static_folder='static',
               static_url_path='supply-chain')


def get_request_data(req_id=None):
    if req_id is None:
        current_requests = Request.query \
            .join(DonationType, Request.donation_type_id == DonationType.id) \
            .join(Affected, Request.affected_id == Affected.id) \
            .join(Address, Request.req_address_id == Address.id) \
            .add_columns(Request.id, Request.name, Request.status, Affected.first_name, Affected.last_name,
                         Affected.campaign_id,
                         Address.city, Address.street, Address.voivodeship, DonationType.type, Request.amount) \
            .all()
    else:
        current_requests = Request.query \
            .join(DonationType, Request.donation_type_id == DonationType.id) \
            .join(Affected, Request.affected_id == Affected.id) \
            .join(Address, Request.req_address_id == Address.id) \
            .filter(Request.id == req_id) \
            .add_columns(Request.id, Request.name, Request.status, Affected.first_name, Affected.last_name,
                         Affected.campaign_id,
                         Address.city, Address.street, Address.voivodeship, DonationType.type, Request.amount) \
            .first()
    return current_requests


@bp.route('/demo', methods=['GET'])
def demo():
    return render_template('module_demo.jinja')


@bp.route('/', methods=['GET', 'POST'])
@roles_required('organization')
def index(error_message=None):
    curr_user_id = current_user.id
    curr_organization = Organization.query \
        .filter(Organization.user_id == curr_user_id).first()

    if request.method == 'GET':
        all_charity_campaigns = db.session.query(CharityCampaign). \
            join(OrganizationCharityCampaign, CharityCampaign.id == OrganizationCharityCampaign.charity_campaign_id). \
            join(Organization, Organization.id == OrganizationCharityCampaign.organization_id). \
            filter(Organization.organization_name == curr_organization.organization_name).all()

        # curr_organization_name = 'FUNDACJA OJCA RYDZYKA'
        curr_charity_campaign = all_charity_campaigns[0]

        # requests for current charity campaign
        current_requests = Request.query \
            .join(DonationType, Request.donation_type_id == DonationType.id) \
            .join(Affected, Request.affected_id == Affected.id) \
            .join(Address, Request.req_address_id == Address.id) \
            .add_columns(Request.id, Request.name, Request.status, Affected.first_name, Affected.last_name,
                         Affected.campaign_id,
                         Address.city, Address.street, Address.voivodeship, DonationType.type, Request.amount) \
            .filter(Affected.campaign_id == curr_charity_campaign.id) \
            .all()

        # current OrganizationCharityCampaign
        curr_organization_charity_campaign = OrganizationCharityCampaign \
            .query.filter(OrganizationCharityCampaign.organization == curr_organization) \
            .filter(OrganizationCharityCampaign.charity_campaign == curr_charity_campaign).first()

        # current item donations
        item_donations = ItemStock.query \
            .join(DonationType, ItemStock.item_type_id == DonationType.id) \
            .add_columns(ItemStock.amount, DonationType.type) \
            .filter(ItemStock.organization_charity_campaign == curr_organization_charity_campaign).all()

        # donation item history for current OrganizationCharityCampaign
        donation_item_history = DonationItem.query \
            .join(Donor, DonationItem.donor_id == Donor.donor_id) \
            .join(DonationType, DonationItem.donation_type_id == DonationType.id) \
            .add_columns(DonationItem.donationItem_id, DonationItem.description, DonationItem.amount,
                         cast(DonationItem.donation_date, VARCHAR), DonationType.type, Donor.name, Donor.surname) \
            .filter(DonationItem.charity_campaign == curr_organization_charity_campaign).all()

        # donation money history for current OrganizationCharityCampaign
        donation_money_history = DonationMoney.query \
            .join(Donor, DonationMoney.donor_id == Donor.donor_id) \
            .filter(DonationMoney.charity_campaign == curr_organization_charity_campaign).all()

        # Current money amount - account balance for current OrganizationCharityCampaign
        curr_account_balance = ItemStock.query \
            .join(DonationType, ItemStock.item_type_id == DonationType.id) \
            .filter(DonationType.type == 'Money',
                    ItemStock.organization_charity_campaign == curr_organization_charity_campaign).first()

        return render_template('supply_chain.jinja',
                               item_donations=item_donations,
                               charity_campaign=curr_charity_campaign,
                               current_requests=current_requests,
                               request_status=RequestStatus,
                               curr_organization=curr_organization,
                               donation_item_history=donation_item_history,
                               donation_money_history=donation_money_history,
                               curr_account_balance=curr_account_balance,
                               all_charity_campaigns=all_charity_campaigns)

    elif request.method == 'POST':
        # charity campaign selection
        selected_charity_campaign_id = request.form['curr_charity_campaign']
        curr_charity_campaign = CharityCampaign.query.filter(CharityCampaign.id == selected_charity_campaign_id).first()
        if curr_charity_campaign is None or curr_organization is None:
            return render_template('supply_chain.jinja')
        # get all avaliable charity campaigns
        all_charity_campaigns = db.session.query(CharityCampaign). \
            join(OrganizationCharityCampaign, CharityCampaign.id == OrganizationCharityCampaign.charity_campaign_id). \
            join(Organization, Organization.id == OrganizationCharityCampaign.organization_id). \
            filter(Organization.organization_name == curr_organization.organization_name).all()

        # get requests for current organization
        current_requests = Request.query \
            .join(DonationType, Request.donation_type_id == DonationType.id) \
            .join(Affected, Request.affected_id == Affected.id) \
            .join(Address, Request.req_address_id == Address.id) \
            .add_columns(Request.id, Request.name, Request.status, Affected.first_name,
                         Affected.last_name, Affected.campaign_id, Address.city, Address.street,
                         Address.voivodeship, DonationType.type, Request.amount) \
            .filter(Affected.campaign_id == curr_charity_campaign.id) \
            .all()

        # get current OrganizationCharityCampaign
        curr_organization_charity_campaign = OrganizationCharityCampaign \
            .query.filter(OrganizationCharityCampaign.organization == curr_organization) \
            .filter(OrganizationCharityCampaign.charity_campaign == curr_charity_campaign).first()

        # get item donations
        item_donations = ItemStock.query \
            .join(DonationType, ItemStock.item_type_id == DonationType.id) \
            .add_columns(ItemStock.amount, DonationType.type) \
            .filter(ItemStock.organization_charity_campaign == curr_organization_charity_campaign).all()

        # get item donation history
        donation_item_history = DonationItem.query \
            .join(Donor, DonationItem.donor_id == Donor.donor_id) \
            .join(DonationType, DonationItem.donation_type_id == DonationType.id) \
            .add_columns(DonationItem.donationItem_id, DonationItem.description, DonationItem.amount,
                         cast(DonationItem.donation_date, VARCHAR), DonationType.type, Donor.name, Donor.surname) \
            .filter(DonationItem.charity_campaign == curr_organization_charity_campaign).all()

        # get money donation history
        donation_money_history = DonationMoney.query \
            .join(Donor, DonationMoney.donor_id == Donor.donor_id) \
            .filter(DonationMoney.charity_campaign == curr_organization_charity_campaign).all()

        # get current money amount(account balance)
        curr_account_balance = ItemStock.query \
            .join(DonationType, ItemStock.item_type_id == DonationType.id) \
            .filter(DonationType.type == 'Money',
                    ItemStock.organization_charity_campaign == curr_organization_charity_campaign).first()

        # rendrer template
        return render_template('supply_chain.jinja',
                               item_donations=item_donations,
                               charity_campaign=curr_charity_campaign,
                               current_requests=current_requests,
                               request_status=RequestStatus,
                               curr_organization=curr_organization,
                               donation_item_history=donation_item_history,
                               donation_money_history=donation_money_history,
                               curr_account_balance=curr_account_balance,
                               all_charity_campaigns=all_charity_campaigns,
                               error_message=error_message)

    return redirect('/supply-chain')


@bp.route('/truncate')
@login_required
def truncate():
    db.drop_all()
    db.create_all()
    db.session.commit()
    print('what: ')
    return render_template('module_demo.jinja', data_present=False)


@bp.route('/request/<int:req_id>', methods=['GET', 'POST'])
@roles_required('organization')
def manage_request(req_id):
    curr_organization = Organization.query.filter(Organization.user_id == current_user.id).first()
    curr_request_data = get_request_data(req_id=req_id)
    curr_affected = Affected.query.join(Request, Request.affected_id == Affected.id).filter(
        Request.id == req_id).first()
    curr_charity_campaign = CharityCampaign.query.filter(CharityCampaign.id == curr_affected.campaign_id).first()
    curr_organization_charity_campaign = OrganizationCharityCampaign.query \
        .filter(OrganizationCharityCampaign.charity_campaign == curr_charity_campaign,
                OrganizationCharityCampaign.organization == curr_organization).first()

    stock_item = ItemStock.query \
        .join(DonationType, ItemStock.item_type_id == DonationType.id) \
        .add_columns() \
        .filter(DonationType.type == curr_request_data.type) \
        .filter(ItemStock.organization_charity_campaign_id == curr_organization_charity_campaign.id) \
        .first()

    if curr_request_data.status == RequestStatus.COMPLETED:
        return render_template('manage_request.jinja',
                               curr_request=curr_request_data,
                               error_message='Request already completed',
                               stock_item=stock_item)
    if request.method == 'GET':
        return render_template('manage_request.jinja', curr_request=curr_request_data,
                               stock_item=stock_item)

    elif request.method == 'POST':
        if stock_item is None:
            return render_template('manage_request.jinja',
                                   curr_request=curr_request_data,
                                   error_message='Could not send items to affected - no items in stock',
                                   stock_item=stock_item)

        current_request = Request.query.filter(Request.id == req_id).first()
        current_stock = ItemStock.query.filter(ItemStock.id == stock_item.id).first()
        donation_amount = int(request.form['donation_amount'])
        if donation_amount <= current_stock.amount:
            current_request.status = RequestStatus.COMPLETED
            current_stock.amount -= donation_amount
            current_request.amount = donation_amount
            db.session.commit()
            return render_template('manage_request.jinja',
                                   curr_request=curr_request_data,
                                   success_message='Items sent successfully',
                                   stock_item=stock_item)
        else:
            print('error')
            return render_template('manage_request.jinja',
                                   curr_request=curr_request_data,
                                   error_message='Could not send items to affected - an error occured',
                                   stock_item=stock_item)

    return render_template('supply_chain.jinja',
                           error_message='Something went wrong. please refresh the page')


@bp.route('/view-all', methods=['GET', 'POST'])
@roles_required('authorities')
def view_all():
    curr_authority = Authorities.query.filter(Authorities.user_id == current_user.id).first()
    all_charity_campaigns = CharityCampaign.query \
        .filter(CharityCampaign.authorities_id == curr_authority.id) \
        .all()
    if request.method == 'GET':
        return render_template('all_resources.jinja',
                               charity_campaigns=all_charity_campaigns)

    elif request.method == 'POST':
        if request.form['curr_charity_campaign_id'] == 'none':
            print('not good')
            return render_template('supply_chain.jinja',
                                   charity_campaign=None,
                                   item_donations=None)
        curr_charity_campaign = CharityCampaign.query.filter(
            CharityCampaign.id == request.form['curr_charity_campaign_id']).first()
        organizations_with_resources = []
        curr_organizations = Organization.query \
            .join(OrganizationCharityCampaign,
                  OrganizationCharityCampaign.charity_campaign_id == curr_charity_campaign.id) \
            .join(CharityCampaign, OrganizationCharityCampaign.charity_campaign_id == CharityCampaign.id) \
            .all()
        for organization in curr_organizations:
            curr_resources = {}
            curr_organization_charity_campaign = OrganizationCharityCampaign.query \
                .filter(OrganizationCharityCampaign.charity_campaign_id == curr_charity_campaign.id,
                        OrganizationCharityCampaign.organization_id == organization.id).first()
            if curr_organization_charity_campaign is not None:
                stock_for_organization = ItemStock.query \
                    .join(DonationType, ItemStock.item_type_id == DonationType.id) \
                    .add_columns(DonationType.type, ItemStock.amount) \
                    .filter(ItemStock.organization_charity_campaign_id == curr_organization_charity_campaign.id) \
                    .all()

                item_donations_for_organization = DonationItem.query \
                    .join(DonationType, DonationItem.donation_type_id == DonationType.id) \
                    .add_columns(DonationType.type, DonationItem.amount) \
                    .filter(DonationItem.charity_campaign == curr_organization_charity_campaign) \
                    .all()

                money_donations_for_organization = DonationMoney.query \
                    .filter(DonationMoney.charity_campaign_id == curr_organization_charity_campaign.id) \
                    .all()

                curr_resources["organization"] = organization
                curr_resources["item_stock"] = stock_for_organization
                curr_resources["item_donations"] = item_donations_for_organization
                curr_resources["money_donations"] = money_donations_for_organization

                organizations_with_resources.append(curr_resources)

        requests_for_charity_campaign = Request.query \
            .join(Affected, Request.affected_id == Affected.id) \
            .join(DonationType, Request.donation_type_id == DonationType.id) \
            .join(Address, Affected.address_id == Address.id) \
            .add_columns(Request.amount, Request.name, DonationType.type, Affected.first_name,
                         Affected.last_name, Address.street, Address.street_number, Address.city, Request.status) \
            .filter(Affected.campaign_id == curr_charity_campaign.id) \
            .all()

        print(organizations_with_resources)
        return render_template('all_resources.jinja',
                               charity_campaigns=all_charity_campaigns,
                               curr_charity_campaign=curr_charity_campaign,
                               curr_organizations=curr_organizations,
                               organizations_with_resources=organizations_with_resources,
                               requests_for_charity_campaign=requests_for_charity_campaign,
                               request_status=RequestStatus)
    return redirect('/supply-chain')


def create_address():
    lista = []
    address1 = Address(
        street="123 Main St",
        street_number="Apt 101",
        city="New York",
        voivodeship="NY"
    )

    address2 = Address(
        street="456 Elm St",
        street_number="Apt 202",
        city="Los Angeles",
        voivodeship="CA"
    )

    address3 = Address(
        street="456 Elm St",
        street_number="Apt 202",
        city="lodz",
        voivodeship="lodzkie"
    )
    lista.append(address1)
    lista.append(address2)
    lista.append(address3)
    db.session.add(address1)
    db.session.add(address2)
    db.session.add(address3)
    db.session.commit()
    return lista


def create_user():
    lista = []
    user1 = User(
        email="john.doe@example.com",
        password_hash="password123",
        active=True,
        type="donor"
    )

    user2 = User(
        email="jane.smith@example.com",
        password_hash="password456",
        active=True,
        type="donor"
    )

    user3 = User(
        email="jane.smith234@example.com",
        password_hash="password456",
        active=True,
        type="authorities"
    )

    user4 = User(
        email="affected@email.com",
        password_hash='pass222',
        active=True,
        type="affected"
    )

    user7 = User(
        email="black@email.com",
        password_hash='3232pass22',
        active=True,
        type="affected"
    )

    user5 = User(
        email="org@email.com",
        password_hash='pass222',
        active=True,
        type="organization"
    )

    user6 = User(
        email="wosp@email.com",
        password_hash='wosppass',
        active=True,
        type="organization"
    )

    user8 = User(
        email="thirdauthoritye3@email.com",
        password_hash='ebe222322e3',
        active=True,
        type="authorities"
    )
    lista.append(user1)
    lista.append(user2)
    lista.append(user3)
    lista.append(user4)
    lista.append(user5)
    lista.append(user6)
    lista.append(user7)
    lista.append(user8)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)
    db.session.add(user5)
    db.session.add(user6)
    db.session.add(user7)
    db.session.add(user8)
    db.session.commit()
    return lista


def create_authority(user):
    lista = []
    authority = Authorities(
        name="New York City Authority",
        phone="123-456-7890",
        address_id=Address.query.filter(Address.street == "123 Main St" and Address.city == 'New York').first().id,
        user_id=User.query.filter(User.email == "jane.smith234@example.com").first().id
    )
    authority2 = Authorities(
        name="Lodz City Authority",
        phone="123-45226-333",
        address_id=Address.query.filter(Address.street == "123 Main St" and Address.city == 'New York').first().id,
        user=user
    )
    lista.append(authority)
    lista.append(authority2)
    db.session.add(authority)
    db.session.add(authority2)
    db.session.commit()
    return lista


def create_donation_type():
    donation_type_2 = DonationType(type='Food')
    donation_type_3 = DonationType(type='Clothes')
    donation_type_4 = DonationType(type='Other')
    donation_type_money = DonationType(type='Money')

    db.session.add(donation_type_2)
    db.session.add(donation_type_3)
    db.session.add(donation_type_4)
    db.session.add(donation_type_money)
    db.session.commit()
    return donation_type_2, donation_type_3, donation_type_4, donation_type_money


@bp.route('/add-data')
@login_required
def add_data():
    address = create_address()
    users = create_user()

    # print(User.query.filter(User.email == "org@email.com").first().email)

    donor1 = Donor(
        name="John",
        surname="Doe",
        phone_number="123-456-7890",
        email="john.doe2@example.com",
        user=users[0]
    )

    donor2 = Donor(
        name="Jane",
        surname="Smith",
        phone_number="987-654-3210",
        email="jane.smith@example.com",
        user_id=User.query.filter(User.email == "jane.smith@example.com").first().id
    )
    donations_types = create_donation_type()
    authorities = create_authority(users[7])

    db.session.add(donor1)
    db.session.add(donor2)
    charity_campaign_1 = CharityCampaign(
        name="Charity campaign 1",
        description="Sample campaign",
        authorities_id=Authorities.query.filter(Authorities.name == "New York City Authority").first().id
    )

    charity_campaign_2 = CharityCampaign(
        name='Charity campaign 2',
        description="Second sample campaign",
        authority=authorities[0]
    )

    charity_campaign_3 = CharityCampaign(
        name='Charity campaign 3',
        description="third",
        authority=authorities[1]
    )

    db.session.add(charity_campaign_1)
    db.session.add(charity_campaign_2)
    db.session.add(charity_campaign_3)

    organization1 = Organization(
        organization_name="FUNDACJA OJCA RYDZYKA",
        description="bardzo dobra organizacja",
        approved=True,
        address_id=Address.query.filter(Address.street == "456 Elm St",
                                        Address.street_number == 'Apt 202',
                                        Address.city == 'Los Angeles').first().id,
        user_id=User.query.filter(User.email == "org@email.com").first().id,
    )

    organization2 = Organization(
        organization_name="WOŚP",
        description="okradli rydzyka nie polecam",
        approved=True,
        address=address[2],
        user=users[5]
    )

    db.session.add(organization1)
    db.session.add(organization2)
    organization_charity_campaign_1 = OrganizationCharityCampaign(
        charity_campaign=charity_campaign_1,
        organization=organization1
    )

    organization_charity_campaign_2 = OrganizationCharityCampaign(
        charity_campaign=charity_campaign_1,
        organization=organization2
    )

    organization_charity_campaign_3 = OrganizationCharityCampaign(
        charity_campaign=charity_campaign_2,
        organization=organization2
    )

    db.session.add(organization_charity_campaign_1)
    db.session.add(organization_charity_campaign_2)
    db.session.add(organization_charity_campaign_3)

    # donation items
    donation_item1 = DonationItem(
        description="Test Donation 1",
        donation_date=datetime.today(),
        amount=100.0,
        donor_id=Donor.query.filter(Donor.email == 'john.doe2@example.com').first().donor_id,
        charity_campaign=organization_charity_campaign_1,
        donation_type=donations_types[0]
    )

    donation_item2 = DonationItem(
        description="Test Donation 2",
        donation_date=datetime.today(),
        amount=50.0,
        donor_id=Donor.query.filter(Donor.email == 'jane.smith@example.com').first().donor_id,
        charity_campaign=organization_charity_campaign_2,
        donation_type=donations_types[1]
    )

    donation_item3 = DonationItem(
        description="dla potrzebujących",
        donation_date=datetime.today(),
        amount=65,
        donor=donor2,
        charity_campaign=organization_charity_campaign_1,
        donation_type=donations_types[3]
    )

    donation_item4 = DonationItem(
        description="ubranie mega donacja",
        donation_date=datetime.today(),
        amount=650,
        donor=donor2,
        charity_campaign=organization_charity_campaign_2,
        donation_type=donations_types[2]
    )

    affected1 = Affected(
        first_name="John",
        last_name="Affected",
        needs="food",
        address_id=Address.query.filter(
            Address.street == "456 Elm St",
            Address.street_number == 'Apt 202',
            Address.city == 'Los Angeles')
        .first().id,
        user_id=User.query.filter(User.email == "affected@email.com").first().id,
        campaign_id=CharityCampaign.query.filter(CharityCampaign.name == 'Charity campaign 1').first().id,
    )

    affected2 = Affected(
        first_name="Jane",
        last_name="Black",
        needs="everything",
        address=address[2],
        user=users[6],
        campaign_id=CharityCampaign.query.filter(CharityCampaign.name == 'Charity campaign 1').first().id,
    )

    # create charity campaign
    stock_1 = ItemStock(item_type=donations_types[1],
                        organization_charity_campaign=organization_charity_campaign_1,
                        amount=donation_item1.amount)

    stock_2 = ItemStock(item_type=donations_types[2],
                        organization_charity_campaign=organization_charity_campaign_2,
                        amount=donation_item2.amount)

    stock_3 = ItemStock(item_type=donations_types[3],
                        organization_charity_campaign=organization_charity_campaign_1,
                        amount=donation_item3.amount)

    stock_2.amount += donation_item4.amount

    db.session.add(donation_item1)
    db.session.add(donation_item2)
    db.session.add(donation_item3)
    db.session.add(donation_item4)
    db.session.add(stock_1)
    db.session.add(stock_2)
    db.session.add(stock_3)
    db.session.add(affected1)
    db.session.add(affected2)

    request_1 = Request(
        name='first reqest',
        status='PENDING',
        amount=10,
        req_address_id=Address.query.filter(
            Address.street == "456 Elm St" and Address.street_number == 'Apt 202' and Address.city == 'Los Angeles')
        .first().id,
        affected_id=Affected.query.filter(
            Affected.first_name == 'John' and Affected.last_name == 'Affected').first().id,
        donation_type_id=DonationType.query.filter(DonationType.type == 'Food').first().id

    )

    request_2 = Request(
        name='second reqest - i need money',
        status='PENDING',
        amount=150,
        req_address=address[1],
        affected=affected1,
        donation_type=donations_types[3]

    )

    request_3 = Request(
        name='give me something',
        status='PENDING',
        amount=35,
        req_address=address[2],
        affected=affected2,
        donation_type=donations_types[3]

    )

    db.session.add(request_1)
    db.session.add(request_2)
    db.session.add(request_3)

    donation_money_1 = DonationMoney(
        description='First money donation',
        donation_type='Money',
        cashAmount=200,
        donor=donor1,
        charity_campaign=organization_charity_campaign_1
    )

    donation_money_2 = DonationMoney(
        description='Second money donation',
        donation_type='Money',
        cashAmount=4000,
        donor=donor1,
        charity_campaign=organization_charity_campaign_2
    )
    stock_money = ItemStock(item_type=donations_types[3],
                            organization_charity_campaign=organization_charity_campaign_1,
                            amount=donation_money_1.cashAmount)

    stock_money2 = ItemStock(item_type=donations_types[3],
                             organization_charity_campaign=organization_charity_campaign_2,
                             amount=4000)

    db.session.add(donation_money_1)
    db.session.add(donation_money_2)
    db.session.add(stock_money)
    db.session.add(stock_money2)

    db.session.commit()

    return render_template('module_demo.jinja', data_present=True)
