# -*- coding: utf-8 -*-
import datetime
from flask import Flask, render_template, request, flash, session, redirect, url_for
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

#bootstrap = Bootstrap(app)



#数据模型部分
class User(db.Model):
    __tablename__ = 'User'  #表名字默认是类名字的小写版本(如果没有此语句) 
    
    Id = db.Column(db.Integer(), primary_key=True)
    Username = db.Column(db.String(255))
    Password = db.Column(db.String(255))
    Gender = db.Column(db.Integer())
    Email = db.Column(db.String(255))
    Tel_Number = db.Column(db.String(255))
    Register_Date = db.Column(db.DateTime, default=datetime.datetime.now)
    Orders = db.relationship(
        'Order',
        backref='User',
        lazy='dynamic'
    )

#以下的两个def 可以不用写，系统会自动添加    
    def __init__(self, username, password, gender, email, tel):
        self.Username = username
        self.Password = password
        self.Gender = gender
        self.Email = email
        self.Tel_Number = tel

    # def __repr__(self):
    #     return "<User '{} {} {} {} {} {} '>" .format(self.Username, self.Password, self.Gender, self.Email, self.Tel_Number, self.Register_Date)



class Order(db.Model):
    __tablename__ = 'Order'

    Id = db.Column(db.Integer(), primary_key=True)
    Title = db.Column(db.String(255), nullable=False)
    Details = db.Column(db.String(255), nullable=False)
    # Order_Tel = db.Column(db.String(255))
    Finish = db.Column(db.Integer(), nullable=False)
    Who_Get = db.Column(db.Integer())
    Order_Date = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    User_id = db.Column(db.Integer(), db.ForeignKey('User.Id'))

    def __init__(self, title):
        self.Title = title




class Criticism(db.Model):
    __tablename__ = 'Criticism'

    Id = db.Column(db.Integer(), primary_key=True)
    Nickname = db.Column(db.String(255))
    Criticism = db.Column(db.String(255))
    Cri_Date = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, nickname, criticism,):
        self.Nickname = nickname
        self.Criticism = criticism
    #
    # def __repr__(self):
    #     return "< '{} {}' >" .format(self.Nickname, self.Criticism)



# 路由部分

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index2.html', title='主页', userlogin_name=session['username'])
    return render_template('index2.html', title="主页")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html'), 500

@app.route('/messagewall', methods=['GET', 'POST'])
def messagewall():
    global success
    global lenth
    success = 0             #评论初始值为0即失败
    lenth = 0
    allCri = Criticism.query.order_by(Criticism.Id.desc()).all()
    lenth = len(allCri)

    if request.method == 'POST':
        Criticismfrosql = Criticism(request.form.get("nickname"), request.form.get("criticism"))
        db.session.add(Criticismfrosql)
        db.session.commit()
        success = 1
        allCri = Criticism.query.order_by(Criticism.Id.desc()).all()
        lenth = len(allCri)
        return render_template('messagewall.html', title="留言墙", success=success, allCri=allCri, lenth=lenth)
    return render_template('messagewall.html', title="留言墙", allCri=allCri, lenth=lenth)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global log
    global status
    log = 0
    status = 1
    if request.method == 'POST':
        userlogin_name = request.form.get("name_login")
        userlogin_password = request.form.get("password_login")

        # if User.query.filter(or_(User.Username==userlogin_name, User.Email==userlogin_name)).all() and User.query.filter(User.Password==userlogin_password) :
            # return render_template('index2.html', userlogin_name=userlogin_name)
            # print "Success"
        user = User.query.filter_by(Username=userlogin_name).first()
        if user is not None and user.Password==userlogin_password:
            status = 1
            log = 1
            # flash(u'登陆成功', category="success")
            session['username'] = userlogin_name

            return render_template('index2.html', userlogin_name=session['username'], log=log)

        else:
            # flash(u'用户名或密码错误！', category="danger")
            status = 0
            return  render_template('login2.html', status=status, log=log)
    return render_template('login2.html', title="测试登陆", log=log)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    global exist
    global flag
    exist = 0
    flag = 0
    if request.method == 'POST':
        new_username = request.form.get("Name")
        # Registertime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

        if User.query.filter_by(Username=new_username).all():
            exist = 1
            # flash(u"注册失败！！用户名已存在!   换个更个性的用户名吧 -_-", category="danger")
        else:
            user_forsql = User(new_username, request.form.get("Password"), request.form.get("Gender"), request.form.get("Email"), request.form.get("Tel"))
            db.session.add(user_forsql)
            db.session.commit()
            flag = 1
            # flash("恭喜您！注册成功", category="success")
    return render_template('register.html', exist=exist, flag=flag)

@app.route('/order', methods=['GET', 'POST'])
def order(success=0):
    if 'username' not in session:
        return render_template('order.html')
    elif request.method == 'POST':
        user = User.query.filter_by(Username=session['username']).first()
        new_order = Order(request.form.get("title"))
        new_order.Details = request.form.get("detials")
        new_order.Finish = 0
        new_order.User_id = user.Id
        db.session.add(new_order)
        db.session.commit()
        success = 1
    return render_template('order.html', userlogin_name=session['username'], success=success)

@app.route('/orderwall', methods=['GET', 'POST'])
def orderwall():
    allorderwall = Order.query.order_by(Order.Id.desc()).all()
    user = User.query.all()
    lenth = Order.query.count()

    return render_template('orderwall.html', title="任务广场",allorderwall=allorderwall, lenth=lenth)


@app.route('/orderwall/<int:order_id>', methods=['GET', 'POST'])
def showdetails(order_id):
    AboutOrder = Order.query.filter_by(Id=order_id).first()
    return render_template('OrderDetails.html', title="任务详情", AboutOrder=AboutOrder)


if __name__ == '__main__':
    app.run(host='localhost', port=80)
