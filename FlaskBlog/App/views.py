from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from sqlalchemy import desc

from .models import *
from .exts import cache

blog = Blueprint('blog', __name__)
admin = Blueprint('admin', __name__)


def get_same_info(page=1, articles=""):
    # 文章分类
    article_type = ArticleType.query.filter().all()
    # 站长推荐
    main_articles = Article.query.order_by(desc("click_num")).all()[:6]
    pagination = ""
    try:
        # 分页
        pagination = articles.paginate(page, per_page=5, error_out=False)
    except:
        pass
    data = {
        "article_type": article_type,
        "main_articles": main_articles,
        'pagination': pagination,
    }
    return data


# 博客首页
@blog.route('/index/<int:page>/')
# @cache.cached(timeout=60 * 3)
def index(page=1):
    articles = Article.query.order_by(desc("create_time"))
    data = {
        "title": "首页",
    }

    data.update(get_same_info(page, articles))
    articles = data['pagination'].items
    data['articles'] = articles
    return render_template("blog/index.html", **data)


@blog.route('/')
def home():
    return redirect(url_for("blog.index", page=1))


# 文章详情
@blog.route('/detail/<int:id>/')
def detail(id):
    article = Article.query.get(id)
    tags = article.tag1
    # 评论列表
    comments = Comment.query.filter_by(article_id=id).all()

    # 点击量统计(一个ip15分钟内只能算一个点击)
    # ip个文章id都要算进来
    ip = request.remote_addr
    cache_id = cache.get(id)
    cache_ip = cache.get(ip)
    if not cache_ip or not cache_id:
        cache.set(ip, ip, timeout=60 * 15)
        cache.set(id, id, timeout=60 * 15)
        article.click_num += 1
        db.session.commit()

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
# @cache.cached(timeout=60 * 3)
def typelist(id):
    page = request.args.get('page', 1, type=int)
    type = ArticleType.query.get(id)
    articles = Article.query.filter_by(article_type=type.id).order_by(desc("create_time"))
    data = {
        "articles": articles,
        "title": "首页",
        "typeid": id,
    }
    data.update(get_same_info(page, articles))
    articles = data['pagination'].items
    data['articles'] = articles
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
    data = {
        "active1": "active",
    }
    return render_template("admin/index.html", **data)


# 后台文章管理
@admin.route("/admin/article/")
def admin_article():
    articles = Article.query.order_by(desc("create_time")).all()
    data = {
        "articles": articles,
        "active2": "active",
    }
    return render_template("admin/article.html", **data)


# 文章修改
@admin.route("/admin/updatearticle/<int:id>/", methods=["GET", "POST"])
def update_article(id):
    if request.method == "GET":
        article = Article.query.get(id)
        tags = Tag.query.all()
        types = ArticleType.query.all()
        data = {
            "article": article,
            'tags': tags,
            "types": types,
            "active2": "active",
        }
        return render_template("admin/update-article.html", **data)
    elif request.method == "POST":
        # 获取表单提交上来的数据
        title = request.form.get("title")
        content = request.form.get("content")
        tags = request.form.getlist("tags")
        type = request.form.get("category")
        description = request.form.get("describe")
        img = request.form.get("titlepic")
        print(img)
        # 查找对应的文章
        article = Article.query.get(id)
        # 修改数据
        article.title = title
        article.content = content
        article.description = description
        article.img = img
        article.articletype = ArticleType.query.get(type)
        tag_list = []
        for i in tags:
            tag = Tag.query.get(i)
            tag_list.append(tag)
        article.tag1 = tag_list
        # 提交
        db.session.commit()
        return redirect(url_for("admin.update_article", id=id))


# 文章删除
@admin.route('/admin/delarticle/')
def del_article():
    article_id = request.args.get("article_id")
    article = Article.query.get(article_id)
    data = {
        "code": 1000,
        "msg": ""
    }
    if not article:
        data['code'] = 1002
        data['msg'] = "文章不存在！"
        return jsonify(data)
    try:
        db.session.delete(article)
        db.session.commit()
    except:
        data['code'] = 1001
        data['msg'] = "删除失败请重试！"
        return jsonify(data)
    data['msg'] = "文章删除成功！"
    return jsonify(data)


# 文章增加
@admin.route('/admin/addarticle/', methods=["GET", "POST"])
def add_article():
    if request.method == "GET":
        tags = Tag.query.all()
        types = ArticleType.query.all()
        data = {
            'tags': tags,
            "active2": "active",
            "types": types,
        }
        return render_template("admin/add-article.html", **data)
    elif request.method == "POST":
        # 获取表单提交上来的数据
        title = request.form.get("title")
        content = request.form.get("content")
        tags = request.form.getlist("tags")
        type = request.form.get("category")
        description = request.form.get("describe")
        img = request.form.get("titlepic")
        article = Article()
        # 新增数据
        article.title = title
        article.content = content
        article.description = description
        article.img = img
        article.create_time = datetime.datetime.now()
        article.articletype = ArticleType.query.get(type)
        tag_list = []
        for i in tags:
            tag = Tag.query.get(i)
            tag_list.append(tag)
        article.tag1 = tag_list
        # 提交
        db.session.commit()
        return redirect(url_for("admin.admin_article"))
