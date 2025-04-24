from functools import wraps

from flask import flash, redirect, url_for, request, render_template_string
from flask_login import LoginManager, current_user
from flask_mailman import EmailMessage

from app.models.user import User
from app.static.auth.reset_password_email_html_content import RESET_PASSWORD_EMAIL_HTML_CONTENT

login_manager = LoginManager()


def init_login_manager(app):
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def roles_required(roles):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('You must be logged in to access this page.', 'warning')
                return redirect(url_for('auth.login'))

            if current_user.type == 'admin':
                return func(*args, **kwargs)

            if current_user.type not in roles:
                flash('You do not have permission to access this page.', 'warning')
                return redirect(request.referrer or url_for('home'))

            if current_user.type == 'authorities':
                authority = current_user.authorities
                if authority and not authority.approved:
                    flash('You do not have permission to access this page.', 'warning')
                    return redirect(request.referrer or url_for('home'))

            if current_user.type == 'organization':
                organization = current_user.organization
                if organization and not organization.approved:
                    flash('Your organisation has not yet been approved by the administration.', 'warning')
                    return redirect(request.referrer or url_for('home'))

            return func(*args, **kwargs)

        return decorated_view

    return wrapper


def send_reset_password_email(user):
    reset_password_url = url_for(
        "auth.reset_password",
        token=user.get_reset_password_token(),
        user_id=user.id,
        _external=True
    )

    email_body = render_template_string(
        RESET_PASSWORD_EMAIL_HTML_CONTENT, reset_password_url=reset_password_url
    )

    message = EmailMessage(
        subject="Reset Your Password",
        body=email_body,
        to=[user.email]
    )
    message.content_subtype = "html"

    message.send()
