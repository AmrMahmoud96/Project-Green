from wtforms import  TextField, TextAreaField, SubmitField, validators, ValidationError
from flask_wtf import FlaskForm

class ContactForm(FlaskForm):
  name = TextField("Name",[validators.DataRequired("Please enter your name.")])
  email = TextField("Email",[validators.DataRequired("Please enter your Email."),validators.Email("Please enter a valid email.")])
  subject = TextField("Subject",[validators.DataRequired("Please enter a subject line.")])
  message = TextAreaField("Message",[validators.DataRequired("Please enter a message.")])
  submit = SubmitField("Submit")