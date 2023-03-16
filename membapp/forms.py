from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired


class ContactForm(FlaskForm):
    screenshot = FileField("upload screenshot:",validators=[FileRequired(),FileAllowed(['png','jpg',"Ensure you upload the right extension"])])
    #fullname = StringField("Your Name:",validators=[DataRequired()]) #generate input of type text
    email = StringField("Your Email: ", validators=[Email(message='hello, ypur email should be valid')])
    message = TextAreaField("Your Message:",validators=[DataRequired(),Length(min=10,message='your message is too short')])
    submit = SubmitField("Send message")
    confirm_email= StringField("Confirm Email",validators=[EqualTo('email')])