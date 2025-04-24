from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash

from app.auth.register_forms import VolunteerRegisterForm, OrganizationRegisterForm, DonorRegisterForm, \
    AffectedRegisterForm, AuthoritiesRegisterForm
from app.auth.reset_password_forms import ResetPasswordRequestForm, ResetPasswordForm
from app.auth.user_service import roles_required, send_reset_password_email
from app.extensions import db
from app.models.address import Address
from app.models.affected import Affected
from app.models.authorities import Authorities
from app.models.donor import Donor
from app.models.organization import Organization
from app.models.user import User
from app.models.volunteer import Volunteer

bp = Blueprint('auth', __name__,
               template_folder='../templates/auth',
               static_folder='static',
               static_url_path='auth')


@bp.route('/')
def index():
    admin_user = User.query.filter_by(email="admin@skph.com").first()

    if not admin_user:
        new_admin = User(
            email="admin@skph.com",
            password_hash=generate_password_hash("haslo123"),
            type="admin"
        )
        db.session.add(new_admin)
        db.session.commit()

    if current_user.is_authenticated:
        logout_user()

    return "Admin user created if it did not exist already."


def get_registration_form(user_type):
    form_classes = {
        'volunteer': VolunteerRegisterForm,
        'organization': OrganizationRegisterForm,
        'donor': DonorRegisterForm,
        'affected': AffectedRegisterForm,
        'authorities': AuthoritiesRegisterForm
    }
    return form_classes.get(user_type)()


def create_user_and_related_data(form, user_type):
    user = User(email=form.email.data, type=user_type)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()

    if user_type == 'donor':
        donor = Donor(
            name=form.first_name.data,
            surname=form.last_name.data,
            phone_number=form.phone.data,
            email=form.email.data,
            user_id=user.id
        )
        db.session.add(donor)

    if user_type in ['volunteer', 'organization', 'affected', 'authorities']:
        address = Address(
            street=form.street.data,
            street_number=form.street_number.data,
            city=form.city.data,
            voivodeship=form.voivodeship.data
        )
        db.session.add(address)
        db.session.commit()

        if user_type == 'volunteer':
            volunteer = Volunteer(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                address=address,
                address_id=address.id,
                user_id=user.id
            )
            db.session.add(volunteer)

        elif user_type == 'organization':
            organization = Organization(
                organization_name=form.organization_name.data,
                description=form.description.data,
                address=address,
                address_id=address.id,
                user_id=user.id
            )
            db.session.add(organization)

        elif user_type == 'affected':
            affected = Affected(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                needs=form.needs.data,
                address=address,
                address_id=address.id,
                user_id=user.id
            )
            db.session.add(affected)

        elif user_type == 'authorities':
            authorities = Authorities(
                name=form.name.data,
                phone=form.phone.data,
                address=address,
                address_id=address.id,
                user_id=user.id
            )
            db.session.add(authorities)

    db.session.commit()


@bp.route('/register/<user_type>', methods=['GET', 'POST'])
def register(user_type):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = get_registration_form(user_type)
    if not form:
        abort(404)

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('register.jinja', form=form, user_type=user_type)

        create_user_and_related_data(form, user_type)
        return redirect(url_for('auth.login'))

    return render_template('register.jinja', form=form, user_type=user_type)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.jinja')


@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_password_email(user)
            flash('Check your email for the instructions to reset your password.', 'info')
            return redirect(url_for('auth.login'))
        flash('Invalid email address.', 'danger')

    return render_template('reset_password_request.jinja', form=form)


@bp.route('/reset_password/<token>/<user_id>', methods=['GET', 'POST'])
def reset_password(token, user_id):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.validate_reset_password_token(token, user_id)
    if not user:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.jinja', form=form)


@bp.route('/register', methods=['GET'])
def register_choice():
    return render_template('register_choice.jinja')


@bp.route('/manage_users', methods=['GET', 'POST'])
@roles_required('admin')
def manage_users():
    authorities = Authorities.query.all()
    organizations = Organization.query.all()

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')
        user_type = request.form.get('user_type')

        if user_type == 'authorities':
            user = User.query.get(user_id)
            if user and user.authorities:
                authority = user.authorities
                if action == 'approve':
                    authority.approve()
                    flash(f'Authority {authority.name} approved.', 'success')
                elif action == 'disapprove':
                    authority.disapprove()
                    flash(f'Authority {authority.name} disapproved.', 'warning')
        elif user_type == 'organization':
            user = User.query.get(user_id)
            if user and user.organization:
                organization = user.organization
                if action == 'approve':
                    organization.approve()
                    flash(f'Organization {organization.organization_name} approved.', 'success')
                elif action == 'disapprove':
                    organization.disapprove()
                    flash(f'Organization {organization.organization_name} disapproved.', 'warning')
            else:
                flash("Organization not found.", "danger")

        return redirect(url_for('auth.manage_users'))

    return render_template('manage_users.jinja', authorities=authorities, organizations=organizations)


@bp.route('/profile')
@login_required
def profile():
    role_urls = {
        # 'admin': url_for('admin.dashboard'),
        'affected': url_for('affected.my_details'),
        'donor': url_for('donors.donor_profile'),
        'organization': url_for('organization.organization_profile'),
        'volunteer': url_for('volunteers.volunteer_profile'),
        'authorities': url_for('organization.authorities_profile')
    }
    return redirect(role_urls[current_user.type])
