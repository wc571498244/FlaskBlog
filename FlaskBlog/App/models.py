from .exts import db


# 文章分类表
class ArticleType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
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


# 标签表
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    ab = db.Column(db.String(50))
    articles = db.relationship('Article', backref='tags', secondary=article_tags, lazy='dynamic')