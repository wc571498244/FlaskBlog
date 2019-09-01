import datetime

from .exts import db


# 文章分类表
class ArticleType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    cname = db.Column(db.String(50))
    articles = db.relationship("Article", backref="articletype", lazy=True)


# 中间表(文章标签)
article_tags = db.Table('article_tags',
                        db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
                        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                        )


#  文章表
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime)
    click_num = db.Column(db.Integer, default=0)
    description = db.Column(db.String(200))
    img = db.Column(db.String(255), default="")
    article_type = db.Column(db.Integer, db.ForeignKey(ArticleType.id))
    comments = db.relationship("Comment", backref="article1", lazy=True)
    like = db.relationship("LikeArticle", backref="articles", lazy=True)

# 标签表
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    articles = db.relationship('Article', backref='tag1', secondary=article_tags, lazy=True)


# 评论表
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(300))
    time = db.Column(db.DateTime, default=datetime.datetime.now())
    username = db.Column(db.String(30))
    article_id = db.Column(db.Integer, db.ForeignKey(Article.id))


# 管理员用户
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(255))
    phone = db.Column(db.String(11))
    name = db.Column(db.String(20))
    logs = db.relationship('LoginLog', backref='loginlogs', lazy=True)


# 登录记录表
class LoginLog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip = db.Column(db.String(100))
    login_time = db.Column(db.DATETIME, default=datetime.datetime.now())
    users = db.Column(db.Integer, db.ForeignKey(AdminUser.id))


# 点赞表
class LikeArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip = db.Column(db.String(100))
    article = db.Column(db.Integer, db.ForeignKey(Article.id))