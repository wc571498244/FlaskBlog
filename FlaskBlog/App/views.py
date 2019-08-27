from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from sqlalchemy import desc

from .models import *

blog = Blueprint('blog', __name__)
admin = Blueprint('admin', __name__)


def get_same_info():
    # 文章分类
    article_type = ArticleType.query.filter().all()
    # 站长推荐
    main_articles = Article.query.order_by(desc("click_num")).all()
    data = {
        "article_type": article_type,
        "main_articles": main_articles,
    }
    return data


# 博客首页
@blog.route('/')
def index():
    articles = Article.query.order_by(desc("create_time")).all()
    data = {
        "articles": articles,
        "title": "首页",
    }
    data.update(get_same_info())
    return render_template("blog/index.html", **data)


# 文章详情
@blog.route('/detail/<int:id>/')
def detail(id):
    article = Article.query.get(id)
    tags = article.tag1
    # 评论列表
    comments = Comment.query.filter_by(article_id=id).all()
    data = {
        "title": "文章详情",
        "article": article,
        "tags": tags,
        "comments": comments
    }
    data.update(get_same_info())
    return render_template("blog/detail.html", **data)


# 分类列表
@blog.route("/typelist/<int:id>/")
def typelist(id):
    articles = ArticleType.query.get(id).articles
    data = {
        "articles": articles,
        "title": "首页",
    }
    data.update(get_same_info())
    return render_template("blog/typelist.html", **data)


# 文章评论
@blog.route('/article/comment/', methods=['POST'])
def article_comment():
    username = request.form.get("username")
    saytext = request.form.get("saytext")
    article_id = request.form.get("article_id")
    if username == "" or saytext == "":
        data = {
            "code": 1001,
            "msg": "用户名和内容不能为空"
        }
        return jsonify(data)
    comment = Comment.query.filter_by(username=username).first()
    if not comment:
        comment = Comment()
        comment.username = username
        comment.content = saytext
        comment.article_id = article_id
        db.session.add(comment)
        db.session.commit()
        data = {
            "code": 1000,
            "msg": "评论成功",
            "data": {
                "username": comment.username,
                "content": comment.content,
                "time": comment.time,
            }
        }
        return jsonify(data)
    data = {
        "code": 1002,
        "msg": "用户名已存在"
    }
    return jsonify(data)


# 后台管理首页
@admin.route("/admin/index/")
def admin_index():
    return render_template("admin/index.html")


# 后台文章管理
@admin.route("/admin/article/")
def admin_article():
    return render_template("admin/article.html")
