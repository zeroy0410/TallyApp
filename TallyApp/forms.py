from datetime import datetime
# from msilib.schema import File
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,IntegerField,SelectField,DateField,FloatField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flask_wtf.file import FileField,FileAllowed
from TallyApp.models import User

class RegistrationForm(FlaskForm):
    username=StringField('用户名',validators=[DataRequired(),Length(min=5,max=20)])
    email=StringField('邮箱',validators=[DataRequired(),Email()])
    password=PasswordField('密码',validators=[DataRequired()])
    confirm_password=PasswordField('确认密码',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('注册')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('用户名已存在')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        print(user)
        if user:
            raise ValidationError('邮箱已被注册')

class LoginForm(FlaskForm):
    username=StringField('用户名',validators=[DataRequired()])
    password=PasswordField('密码',validators=[DataRequired()])
    remember=BooleanField('记住我')
    submit=SubmitField("登录")

class DataForm(FlaskForm):
    notes=StringField('备注',validators=[])
    cost=FloatField('金额',validators=[DataRequired()])
    category=SelectField('分类',validators=[],default=1,coerce=int)
    date_added=DateField('日期',default=datetime.utcnow)
    submit=SubmitField('提交')

class UploadForm(FlaskForm):
    file_=FileField('上传文件',validators=[FileAllowed(['xlsx'])])
    submit=SubmitField('提交')