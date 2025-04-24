from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class BaseRegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Register')


class AddressFormMixin:
    street = StringField('Street', validators=[DataRequired()])
    street_number = StringField('Street Number', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    voivodeship = StringField('Voivodeship', validators=[DataRequired()])


class DonorRegisterForm(BaseRegisterForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone = StringField('Phone', validators=[DataRequired(), Length(min=9, max=15)])


class VolunteerRegisterForm(BaseRegisterForm, AddressFormMixin):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=9, max=15)])


class OrganizationRegisterForm(BaseRegisterForm, AddressFormMixin):
    organization_name = StringField('Organization Name', validators=[DataRequired(), Length(min=2)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=9, max=15)])


class AffectedRegisterForm(BaseRegisterForm, AddressFormMixin):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2)])
    needs = TextAreaField('Needs', validators=[DataRequired(), Length(min=10)])


class AuthoritiesRegisterForm(BaseRegisterForm, AddressFormMixin):
    name = StringField('Name', validators=[DataRequired(), Length(min=2)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=9, max=15)])
