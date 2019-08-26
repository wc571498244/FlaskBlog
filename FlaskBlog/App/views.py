from flask import Blueprint, render_template
from .models import *

blog = Blueprint('blog', __name__)
admin = Blueprint('admin', __name__)


# 博客首页
@blog.route('/')
def index():
    articles = Article.query.filter().all()
    article_type = ArticleType.query.filter().all()
    data = {
        "articles": articles,
        "title": "首页",
        "article_type": article_type,
    }
    for i in article_type:
        print(len(i.articles))
    return render_template("blog/index.html", **data)


# 文章详情
@blog.route('/detail/<int:id>/')
def detail(id):
    article = Article.query.get(id)
    tags = article.tags
    article_type = ArticleType.query.filter().all()
    data = {
        "title": "文章详情",
        "article": article,
        "tags": tags,
        "article_type": article_type,
    }
    return render_template("blog/detail.html", **data)


# 分类列表
@blog.route("/typelist/<int:id>/")
def typelist(id):
    articles = ArticleType.query.get(id).articles
    article_type = ArticleType.query.filter().all()
    data = {
        "articles": articles,
        "title": "首页",
        "article_type": article_type,
    }
    return render_template("blog/typelist.html", **data)
