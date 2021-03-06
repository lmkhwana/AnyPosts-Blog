from flask_wtf import FlaskForm
from flask_wtf .file import FileField, FileAllowed
from anyposts.models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max = 20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()]) 
    password = PasswordField('Password', validators=[Length(min=6, max=12), DataRequired()]) 
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=6, max=12), DataRequired(), EqualTo('password')]) 
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()]) 
    password = PasswordField('Password', validators=[Length(min=6, max=12), DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max = 20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])]) 
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Comment')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account for that email, please register')



class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[Length(min=6, max=12), DataRequired()]) 
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=6, max=12), DataRequired(), EqualTo('password')]) 
    submit = SubmitField('Reset Password')





    