from wtforms import  TextField, TextAreaField, SubmitField, validators, ValidationError, PasswordField
from wtforms.fields.html5 import DateField
from flask_wtf import FlaskForm
from datetime import datetime,date
from dateutil.relativedelta import relativedelta

class ContactForm(FlaskForm):
  name = TextField("Name",[validators.DataRequired("Please enter your name.")])
  email = TextField("Email",[validators.DataRequired("Please enter your Email."),validators.Email("Please enter a valid email.")])
  subject = TextField("Subject",[validators.DataRequired("Please enter a subject line.")])
  message = TextAreaField("Message",[validators.DataRequired("Please enter a message.")])
  submit = SubmitField("Submit")

class RegisterForm(FlaskForm):
  firstName = TextField("First Name",[validators.DataRequired("Please enter your name.")])
  lastName= TextField("Last Name",[validators.DataRequired("Please enter your name.")])
  dob = DateField("Date of Birth", format='%Y-%m-%d')
  email = TextField("Email",[validators.DataRequired("Please enter your Email."),validators.Email("Please enter a valid email.")])
  password = PasswordField("Password",[ validators.Regexp('^\w+$', message="Password must contain only letters, numbers, or underscore"),
        validators.Length(min=8, max=25, message="Password must be betwen 8 & 25 characters"),
        validators.DataRequired("Please enter a password.")] )
  submit = SubmitField("Sign up")
  
  