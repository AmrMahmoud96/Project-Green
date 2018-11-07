from wtforms import  TextField, TextAreaField, SubmitField, validators, ValidationError, PasswordField, IntegerField
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
class PortfolioCalculationForm(FlaskForm):
  equities = IntegerField("Equities" ,[validators.NumberRange(min=0),validators.Optional()],render_kw={"placeholder": "Enter the amount of money you have in equities."})
  bonds = IntegerField("Bonds",[validators.NumberRange(min=0),validators.Optional()],render_kw={"placeholder": "Enter the amount of money you have in bonds."})
  oil = IntegerField("Oil",[validators.NumberRange(min=0),validators.Optional()],render_kw={"placeholder": "Enter the amount of money you have in oil."})
  cash = IntegerField("Cash",[validators.NumberRange(min=0),validators.Optional()],render_kw={"placeholder": "Enter the amount of money you have in cash."})
  submit = SubmitField("Enter")

class RegisterForm(FlaskForm):
  firstName = TextField("First Name",[validators.DataRequired("Please enter your name.")])
  lastName= TextField("Last Name",[validators.DataRequired("Please enter your name.")])
  dob = DateField("Date of Birth", format='%Y-%m-%d')
  email = TextField("Email",[validators.DataRequired("Please enter your Email."),validators.Email("Please enter a valid email.")])
  password = PasswordField("Password",[ validators.Regexp('^\w+$', message="Password must contain only letters, numbers, or underscore"),
        validators.Length(min=8, max=25, message="Password must be betwen 8 & 25 characters"),
        validators.DataRequired("Please enter a password.")] )
  submit = SubmitField("Sign up")
  
  