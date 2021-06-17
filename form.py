from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    publication = TextAreaField('Publications')
    grants = TextAreaField('Grants')
    awards = TextAreaField('Awards')
    teaching = TextAreaField('Teaching')
    submit = SubmitField('Post')
