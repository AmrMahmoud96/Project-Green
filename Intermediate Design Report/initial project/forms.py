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
  #['ACWV','AGG','DBC','EMB','EMGF','GLD','HYG','IMTM','IQLT','IVLU','MTUM','QUAL','SCHH','SIZE','SPTL','TIP','USMV','VLUE','SHV','SPY]
  ACWV = DecimalField("ACVW",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in global equities."})
  AGG = DecimalField("AGG",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in US intermediate bonds."})
  DBC = DecimalField("DBC",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in commodities."})
  EMB = DecimalField("EMB",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in emerging market bonds."})
  EMGF = DecimalField("EMGF",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in emerging markets."})
  GLD = DecimalField("GLD",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in gold."})
  HYG = DecimalField("HYG",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in high yield bonds."})
  IMTM = DecimalField("IMTM",[validators.NumberRange(min=0),validators.Optional()],places=2)
  IQLT = DecimalField("IQLT",[validators.NumberRange(min=0),validators.Optional()],places=2)
  IVLU = DecimalField("IVLU",[validators.NumberRange(min=0),validators.Optional()],places=2)
  MTUM = DecimalField("MTUM",[validators.NumberRange(min=0),validators.Optional()],places=2)
  QUAL = DecimalField("QUAL",[validators.NumberRange(min=0),validators.Optional()],places=2)
  SCHH = DecimalField("SCHH",[validators.NumberRange(min=0),validators.Optional()],places=2)
  SIZE = DecimalField("SIZE",[validators.NumberRange(min=0),validators.Optional()],places=2)
  SPTL = DecimalField("SPTL",[validators.NumberRange(min=0),validators.Optional()],places=2)
  TIP = DecimalField("TIP",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in inflation-protected bonds."})
  USMV = DecimalField("USMV",[validators.NumberRange(min=0),validators.Optional()],places=2)
  VLUE = DecimalField("VLUE",[validators.NumberRange(min=0),validators.Optional()],places=2)
  SHV = DecimalField("SHV",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in money market/short term bonds."})
  SPY = DecimalField("SPY" ,[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in developed equity markets."})
  submit = SubmitField("Enter")
class PortfolioCalculationForm(FlaskForm):
  SPY = DecimalField("Equities" ,[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in equities."})
  AGG = DecimalField("Bonds",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in bonds."})
  DBC = DecimalField("Commodities",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in commoditites."})
  SCHH = DecimalField("Real Estate",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in real estate."})
  SHV = DecimalField("Cash",[validators.NumberRange(min=0),validators.Optional()],places=2,render_kw={"placeholder": "Enter the amount of money you have in cash."})
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
  
  