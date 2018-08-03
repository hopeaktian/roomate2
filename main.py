# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, flash
from config import DevConfig

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import not_, or_

from flask_wtf import Form
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_bootstrap import Bootstrap
app = Flask(__name__)
app.config.from_object(DevConfig)

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)
# 表单对象
# class RegisterForm(Form):
#     Name = StringField(
#         u'名字',
#         validators=[DataRequired(), Length(max=255)]
#     )
#
#     Password = StringField(
#         u'密码',
#         validators=[DataRequired(), Length(max=255)]
#     )
#
#     Email = StringField(
#         u'邮件',
#         validators=[DataRequired, Email()]
#     )
#     Tel = IntegerField(
#         u'电话',
#         validators=[DataRequired, Length(max=11)]
#     )
#     Gender = SelectField(
#         u'性别',
#         validators=[DataRequired()]
#     )



#数据模型部分
class User(db.Model):
    __tablename__ = 'User'  #表名字默认是类名字的小写版本(如果没有此语句) 
    
    Id = db.Column(db.Integer(), primary_key=True)
    Username = db.Column(db.String(255))
    Password = db.Column(db.String(255))
    Gender = db.Column(db.Integer())
    Email = db.Column(db.String(255))
    Tel_Number = db.Column(db.String(255))

#以下的两个def 可以不用写，系统会自动添加    
    def __init__(self, username, password, gender, email, tel):
        self.Username = username
        self.Password = password
        self.Gender = gender
        self.Email = email
        self.Tel_Number = tel

    def __repr__(self):
        return "<User '{} {} {} {} {} '>" .format(self.Username, self.Password, self.Gender, self.Email, self.Tel_Number)





# 路由部分

@app.route('/')
def index():
    return render_template('index2.html', title="测试主页")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userlogin_name = request.form.get("name_login")
        userlogin_password = request.form.get("password_login")

        # if User.query.filter(or_(User.Username==userlogin_name, User.Email==userlogin_name)).all() and User.query.filter(User.Password==userlogin_password) :
            # return render_template('index2.html', userlogin_name=userlogin_name)
            # print "Success"
        user = User.query.filter_by(Username=userlogin_name).first()
        if user is not None and user.Password==userlogin_password:
            log = 1
            return render_template('index2.html', userlogin_name=userlogin_name, log=log)
            flash("登陆成功")
        else:
            flash("用户名或密码错误！")
            log =0
            return  render_template('login2.html')
    return render_template('login2.html', title="测试登陆")



exist = 0
flag = 0
@app.route('/register', methods=['GET', 'POST'])
def register():
    global exist
    global flag
    exist = 0
    flag = 0
    if request.method == 'POST':
        new_username = request.form.get("Name")

        if User.query.filter_by(Username=new_username).all():
            exist = 1
        else:
            user_forsql = User(new_username, request.form.get("Password"), request.form.get("Gender"), request.form.get("Email"), request.form.get("Tel"))
            db.session.add(user_forsql)
            db.session.commit()
            flag = 1
    return render_template('register.html', exist=exist, flag=flag)



if __name__ == '__main__':
    app.run(host='localhost', port=80)
