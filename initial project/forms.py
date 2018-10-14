from wtforms import  TextField, TextAreaField, SubmitField, validators, ValidationError
from flask_wtf import FlaskForm

class ContactForm(FlaskForm):
  name = TextField("Name",[validators.DataRequired("Please enter A")])
  email = TextField("Email",[validators.DataRequired("Please enter B"),validators.Email("Please enter a valid email.")])
  subject = TextField("Subject",[validators.DataRequired("Please enter C")])
  message = TextAreaField("Message",[validators.DataRequired("Please enter D")])
  submit = SubmitField("Send")