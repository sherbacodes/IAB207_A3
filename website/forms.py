from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, IntegerField, DateField, TimeField, FloatField
from wtforms.validators import InputRequired, Email, EqualTo, Regexp, ValidationError, NumberRange
from flask_wtf.file import FileRequired, FileField, FileAllowed
from wtforms import SelectField
from datetime import date

ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'png', 'jpg', 'jpeg'}

# Create an event form
class EventManagementForm(FlaskForm):
    event_name = StringField('Event name', validators=[InputRequired()])
    category_id = SelectField(
        'Category',
        coerce=int,
        validators=[NumberRange(min=1, message="Please select a category.")]
    )
    event_description = TextAreaField('Description', validators=[InputRequired()])
    start_date = DateField('Start Date', validators=[InputRequired()])
    end_date = DateField('End Date', validators=[InputRequired()])
    start_time = TimeField('Start Time', validators=[InputRequired()])
    end_time = TimeField('End Time', validators=[InputRequired()])
    event_location = StringField('Location', validators=[InputRequired()])
    event_image = FileField('Event Image', validators=[
        FileRequired(message='Image cannot be empty'),
        FileAllowed(ALLOWED_FILE, message='Only supports PNG, JPG, png, jpg')
    ])
    ticket_price = IntegerField('Ticket Price ($)', validators=[InputRequired(), NumberRange(min=0, message='Ticket price cannot be negative')])
    capacity = IntegerField('Capacity', validators=[InputRequired(), NumberRange(min=1, message='Capacity must be at least 1')])
    submit = SubmitField("Create")

    def validate_start_date(self, field):
        if field.data < date.today():
            raise ValidationError("Start date cannot be in the past.")

    def validate_end_date(self, field):
        if self.start_date.data and field.data < self.start_date.data:
            raise ValidationError("End date cannot be before the start date.")

# Login form
class LoginForm(FlaskForm):
    username = StringField("User Name", validators=[InputRequired('Enter user name')])
    password = PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

# Custom validator to check for spaces in the field
def no_spaces(form, field):
    if ' ' in field.data:
        raise ValidationError("Spaces are not allowed in this field.")

# Registration form
class RegisterForm(FlaskForm):
    username = StringField("User Name", validators=[InputRequired(), no_spaces])
    first_name = StringField("First Name", validators=[InputRequired(), no_spaces])
    last_name = StringField("Last Name", validators=[InputRequired(), no_spaces])

    phone_number = StringField("Mobile Number", validators=[
        InputRequired(),
        Regexp(r'^04\d{8}$', message="Enter a valid 10-digit mobile number starting with 04 (no spaces).")
    ])

    street_address = StringField("Street Address", validators=[InputRequired()])
    email = StringField("Email Address", validators=[Email("Please enter a valid email."), no_spaces])

    gender = SelectField("Gender", choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[InputRequired()])

    profile_image = FileField("Profile Image (optional)", validators=[
        FileAllowed(ALLOWED_FILE, message='Only PNG, JPG, JPEG files are allowed.')
    ])

    password = PasswordField("Password", validators=[
        InputRequired(),
        EqualTo('confirm', message="Passwords should match"),
        no_spaces
    ])
    confirm = PasswordField("Confirm Password", validators=[InputRequired(), no_spaces])

    submit = SubmitField("Register")

# Comment form
class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[InputRequired()])
    submit = SubmitField('Post Comment')

# Profile editing form
class ProfileEditForm(FlaskForm):
    username = StringField("User Name", validators=[InputRequired(), no_spaces])
    first_name = StringField("First Name", validators=[InputRequired(), no_spaces])
    last_name = StringField("Last Name", validators=[InputRequired(), no_spaces])

    phone_number = StringField("Mobile Number", validators=[
        InputRequired(),
        Regexp(r'^04\d{8}$', message="Enter a valid 10-digit mobile number starting with 04 (no spaces).")
    ])

    street_address = StringField("Street Address", validators=[InputRequired()])
    email = StringField("Email Address", validators=[Email("Please enter a valid email."), no_spaces])

    gender = SelectField("Gender", choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[InputRequired()])

    profile_image = FileField("Profile Image (optional)", validators=[
        FileAllowed(ALLOWED_FILE, message='Only PNG, JPG, JPEG files are allowed.')
    ])

    password = PasswordField("New Password", validators=[
        EqualTo('confirm', message="Passwords should match"),
        no_spaces
    ])
    confirm = PasswordField("Confirm New Password", validators=[no_spaces])

    submit = SubmitField("Update Profile")