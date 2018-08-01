# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from config import DevConfig

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(DevConfig)

db = SQLAlchemy(app)



#数据模型部分
class User(db.Model):
    __tablename__ = 'User'  #表名字默认是类名字的小写版本(如果没有此语句) 
    
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    posts = db.relationship(    
        'Post',
        backref = 'user',
        lazy = 'dynamic'
    )
#以下的两个def 可以不用写，系统会自动添加    
    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return "<User '{}'>" .format(self.username)


tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)



class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    publish_date = db.Column(db.DateTime())
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )
    user_id = db.Column(db.Integer(), db.ForeignKey('User.id'))   #关联形数据模型，post表关联到User表

    tags = db.relationship(
        'Tag',
        secondary=tags,
        backref=db.backref('posts', lazy='dynamic')
    )
    
    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>" .format(self.title)

class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    
    def __init__(self, title):
        self.title = title
    def __repr__(self):
        return "<Tag '{}'>" .format(self.title)


class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))
    
    def __repr__(self):
        return "<Comment '{}'>" .format(self.text[:15])


# 路由部分

@app.route('/')
def index():
    return render_template('index.html', title="测试主页")
@app.route('/login')
def login():
    return render_template('login.html', title="测试登陆")


if __name__ == '__main__':
    app.run(host='172.16.252.178', port=9999)
