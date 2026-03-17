from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import PasswordField, StringField
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class UploadForm(FlaskForm):
    file = FileField(
        "File",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "jpeg", "png"], "Images only!"),
        ],
    )
