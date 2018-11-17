from wtforms import  TextField, TextAreaField, SubmitField, validators, ValidationError, PasswordField, DecimalField
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
class DetailedPortfolioCalculationForm(FlaskForm):
  SPY = DecimalField("SPY" ,[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in developed equity markets."})
  EFA = DecimalField("EFA",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in developed equity markets."})
  EEM = DecimalField("EEM",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in emerging market equities."})
  VNQ = DecimalField("VNQ",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in developed real estate."})
  TLT = DecimalField("TLT",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in long duration US bonds."})
  AGG = DecimalField("AGG",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in US intermediate bonds."})
  BWX = DecimalField("BWX",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in international developed market bonds."})
  EMB = DecimalField("EMB",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in emerging market bonds."})
  TIP = DecimalField("TIP",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in inflation-protected bonds."})
  MUB = DecimalField("MUB",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in municipal bonds."})
  SHV = DecimalField("SHV",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in money market/short term bonds."})
  DBC = DecimalField("DBC",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in commodities."})
  GLD = DecimalField("GLD",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in gold."})
  submit = SubmitField("Enter")
class PortfolioCalculationForm(FlaskForm):
  SPY = DecimalField("Equities" ,[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in equities."})
  TLT = DecimalField("Bonds",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in bonds."})
  DBC = DecimalField("Commodities",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in commoditites."})
  VNQ = DecimalField("Real Estate",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in real estate."})
  MUB = DecimalField("Cash",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in cash."})
  GLD = DecimalField("Gold",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in gold."})
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
  
  