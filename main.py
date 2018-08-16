# -*- coding: utf-8 -*-
import datetime, os, time
from flask import Flask, render_template, request, flash, session, redirect, url_for
from config import DevConfig
from werkzeug import secure_filename

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import not_, or_

from flask_wtf import Form
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_bootstrap import Bootstrap
app = Flask(__name__)
app.config.from_object(DevConfig)

db = SQLAlchemy(app)


# 自定义jinja过滤器
def time_format(l):
    return str(l)[:-7]
app.add_template_filter(time_format, 'format_time')


#bootstrap = Bootstrap(app)

UPLOAD_FOLDER = "./static/Upload_File/"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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

    # Orders = db.relationship(
    #     'Order',
    #     backref='User',
    #     lazy='dynamic'
    # )

    # Get_Orders = db.relationship(
    #     'Got_Order',
    #     backref='User',
    #     lazy='dynamic'
    # )

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

    Order_Date = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    Dead_Date = db.Column(db.DateTime, nullable=False)
    Picture_Name = db.Column(db.String(255))
    User_id = db.Column(db.Integer(), db.ForeignKey('User.Id'), nullable=False)         # 发单用户的Id
    Got_id = db.Column(db.Integer(), db.ForeignKey('User.Id'))                          # 接单用户的Id

    User = db.relationship('User', foreign_keys='Order.User_id')
    Got_User = db.relationship('User', foreign_keys='Order.Got_id')

    Got_Date = db.Column(db.DateTime)                                                     # 接单的时间

    # Get_Orders = db.relationship(
    #     'Got_Order',
    #     backref='Order',
    #     lazy='dynamic'
    # )

    def __init__(self, title):
        self.Title = title

# class Got_Order(db.Model):
#
#     __tablename__ = 'Got_Order'
#
#     Id = db.Column(db.Integer(), primary_key=True)
#     Got_Date = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
#     User_id = db.Column(db.Integer(), db.ForeignKey('User.Id'))
#     Order_id = db.Column(db.Integer(), db.ForeignKey('Order.Id'))
#
#     def __int__(self, order_id):
#         self.Order_id = order_id




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
def checkuser():
    if 'username' in session:
        global user
        user = User.query.filter_by(Username=session['username']).first()

@app.route('/')
def index():
    if 'username' in session:
        global user
        user = User.query.filter_by(Username=session['username']).first()
        return render_template('index2.html', title=u'袋鼠邻居主页', userlogin_name=session['username'], user=user)
    return render_template('index2.html', title=u"袋鼠邻居主页")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', title=u"错误"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html', title=u"错误"), 500

@app.route('/messagewall', methods=['GET', 'POST'])
def messagewall():
    global success
    global lenth
    global userlogin_name
    success = 0             #评论初始值为0即失败
    lenth = 0
    allCri = Criticism.query.order_by(Criticism.Id.desc()).all()
    lenth = len(allCri)

    if 'username' in session:
        user = User.query.filter_by(Username=session['username']).first()
        userlogin_name = session['username']
        if request.method == 'POST':
            Criticismfrosql = Criticism(request.form.get("nickname"), request.form.get("criticism"))
            db.session.add(Criticismfrosql)
            db.session.commit()
            success = 1
            allCri = Criticism.query.order_by(Criticism.Id.desc()).all()
            lenth = len(allCri)

        return render_template('messagewall.html', title=u"留言墙", success=success, allCri=allCri, lenth=lenth, userlogin_name=session['username'], user=user)
    else:
        if request.method == 'POST':
            Criticismfrosql = Criticism(request.form.get("nickname"), request.form.get("criticism"))
            db.session.add(Criticismfrosql)
            db.session.commit()
            success = 1
            allCri = Criticism.query.order_by(Criticism.Id.desc()).all()
            lenth = len(allCri)

        return render_template('messagewall.html', title=u"留言墙", success=success, allCri=allCri, lenth=lenth)


@app.route('/login', methods=['GET', 'POST'])
def login():
    checkuser()
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

            return render_template('index2.html', userlogin_name=session['username'], log=log, title=u"登陆", user=user)

        else:
            # flash(u'用户名或密码错误！', category="danger")
            status = 0
            return  render_template('login2.html', status=status, log=log, title=u"登陆", user=user)
    return render_template('login2.html', title=u"登陆", log=log)


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
    return render_template('register.html', exist=exist, flag=flag, title=u"注册")

# 发订单
@app.route('/order', methods=['GET', 'POST'])
def order(success=0):
    checkuser()
    now_time = datetime.datetime.now()

    global now_time
    if 'username' not in session:
        return render_template('notlogin.html', title=u"创建订单")
    elif request.method == 'POST':

        user_now = User.query.filter_by(Username=session['username']).first()
        new_order = Order(request.form.get("title"))
        new_order.Details = request.form.get("detials")
        new_order.Dead_Date = request.form.get("diedate")
        new_order.Finish = 0
        new_order.User_id = user_now.Id

        db.session.add(new_order)
        db.session.commit()

        if request.files.has_key("inputFile"):
            file = request.files['inputFile']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                index_point = filename.index(".")
                filename = str(new_order.Id)+filename[index_point:]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_order.Picture_Name = filename

                db.session.add(new_order)
                db.session.commit()
        success = 1
    return render_template('order.html', title=u"创建订单", userlogin_name=session['username'], user=user, success=success, now_time=now_time)

# 任务大厅展示
@app.route('/orderwall', methods=['GET', 'POST'])
def orderwall():
    # now_time = float(time.mktime(datetime.datetime.now().timetuple()))
    datetime = datetime
    global datetime
    checkuser()
    allorderwall = Order.query.order_by(Order.Id.desc()).all()
    # user = User.query.all()
    lenth = Order.query.count()

    if 'username' in session:
        return render_template('orderwall.html', title=u"任务广场",allorderwall=allorderwall, lenth=lenth, userlogin_name=session['username'], user=user, datetime=datetime)
    return render_template('orderwall.html', title=u"任务广场",allorderwall=allorderwall, lenth=lenth, datetime=datetime)

# 订单详情
@app.route('/orderwall/<int:order_id>', methods=['GET', 'POST'])
def showdetails(order_id):
    checkuser()
    AboutOrder = Order.query.filter_by(Id=order_id).first()
    if 'username' in session:
        return render_template('OrderDetails.html', title=u"任务详情", AboutOrder=AboutOrder, userlogin_name=session['username'], user=user)
    return render_template('OrderDetails.html', title=u"任务详情", AboutOrder=AboutOrder)

# 确认接单
@app.route('/orderwall/<int:order_id>/confirm', methods=['GET', 'POST'])
def getorder(order_id):
    checkuser()
    got_success = 0
    AboutOrder = Order.query.filter_by(Id=order_id).first()
    if 'username' not in session:
        return render_template('notlogin.html', title=u"请先登陆")
    elif request.method == 'POST':
        if request.form.get("confirm") == "1":
            get_user = User.query.filter_by(Username=session['username']).first()
            AboutOrder.Got_id = get_user.Id
            AboutOrder.Got_Date = datetime.datetime.now()
            db.session.add(AboutOrder)
            db.session.commit()
            got_success = 1
            return redirect(url_for('takein', user_id=get_user.Id))
        else:
            return redirect(url_for('orderwall'))

    return render_template('confirmorder.html', title=u"确认接单", AboutOrder=AboutOrder, userlogin_name=session['username'], got_success=got_success, user=user)

@app.route('/user/<int:user_id>/sendout', methods=['POST', 'GET'])
def sendout(user_id):
    checkuser()

    AboutOrder = Order.query.filter_by(User_id=user_id).order_by(Order.Id.desc()).all()
    lenth = len(AboutOrder)
    if request.method == "POST":
        user_order = Order.query.filter_by(Id=request.form.get("order_id")).first()
        if request.form.get("cancel") == "1":                                                       #取消订单
            user_order.Finish = request.form.get("cancel")
            db.session.add(user_order)
            db.session.commit()
        else:
            user_order.Finish = request.form.get("finish")                                          #确认收货
            db.session.add(user_order)
            db.session.commit()
    return render_template('sendout.html', title=u"发出订单", AboutOrder=AboutOrder, lenth=lenth, userlogin_name=session['username'], user=user)

@app.route('/user/<int:user_id>/takein')
def takein(user_id):
    checkuser()

    AboutOrder = Order.query.filter_by(Got_id=user_id).order_by(Order.Id.desc()).all()
    lenth = len(AboutOrder)
    return render_template('takein.html', title=u"接受订单", AboutOrder=AboutOrder, lenth=lenth, userlogin_name=session['username'], user=user)


if __name__ == '__main__':
    app.run(host='localhost', port=80)