from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField
from wtforms.validators import InputRequired, Email, EqualTo
from flask_wtf.file import FileRequired, FileField, FileAllowed

ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'png', 'jpg', 'jpeg'}

# Create an event Database:
class EventManagementForm(FlaskForm):
    event_name = StringField('Event', validators=[InputRequired()])
    event_categorty = StringField('Category', validators=[InputRequired()])
    event_description = TextAreaField('Description', validators=[InputRequired()])
    start_date = StringField('Start Date', validators=[InputRequired()])
    start_time = StringField('Start Time', validators=[InputRequired()])
    end_date = StringField('End Date', validators=[InputRequired()])
    end_time = StringField('End Time', validators=[InputRequired()])
    event_location = StringField('Location', validators=[InputRequired()])
    event_image = FileField('Event Image', validators=[FileRequired(message='Image cannot be empty'),FileAllowed(ALLOWED_FILE, message='Only supports PNG, JPG, png, jpg')])
    ticket_price = StringField('Ticket Price', validators=[InputRequired()])
    capacity = StringField('Capacity', validators=[InputRequired()])
    submit = SubmitField("Create")

# creates the login information
class LoginForm(FlaskForm):
    username = StringField("User Name", validators=[InputRequired('Enter user name')])
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

# this is the registration form
class RegisterForm(FlaskForm):
    username = StringField("User Name", validators=[InputRequired()])
    first_name=StringField("First Name", validators=[InputRequired()])
    last_name=StringField("Last Name", validators=[InputRequired()])
    mobile_number=StringField("Mobile Number", validators=[InputRequired()])
    street_address=StringField("Street Address", validators=[InputRequired()])
    # email address should be unique
    email = StringField("Email Address", validators=[Email("Please enter a valid email")])
    # linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired(), EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password")

    # submit button
    submit = SubmitField("Register")

# User comment
class CommentForm(FlaskForm):
    text = TextAreaField('Comment', [InputRequired()])
    submit = SubmitField('Create')

