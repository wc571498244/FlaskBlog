import re

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g
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

    # 下一篇文章
    next_article = Article.query.filter(Article.create_time.__lt__(article.create_time)).all()[-1]

    # 上一篇文章
    prev_article = Article.query.filter(Article.create_time.__gt__(article.create_time)).first()

    # 是否点赞
    likes = article.like
    like = None
    for i in likes:
        if request.remote_addr == i.ip:
            like = i
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
        "comments": comments,
        "prev_article": prev_article,
        "next_article": next_article,
        'likes': likes
    }
    if like:
        data["like_ip"] = like.ip

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
    articles = Article.query.filter().all()
    comments = Comment.query.filter().all()
    types = ArticleType.query.filter().all()
    tags = Tag.query.filter().all()
    data = {
        "active1": "active",
        "request": request,
        "articles": articles,
        "comments": comments,
        "tags": tags,
        "types": types,
        "user": g.user,
    }
    return render_template("admin/index.html", **data)


# 后台文章管理
@admin.route("/admin/article/<int:page>/")
def admin_article(page):
    pagination = Article.query.order_by(desc("create_time")).paginate(page, per_page=10, error_out=False)
    data = {
        "articles": pagination.items,
        "active2": "active",
        "pagination": pagination,
    }
    return render_template("admin/article.html", **data)


# 后台文章修改
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


# 后台文章删除
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


# 后台文章增加
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
        return redirect(url_for("admin.admin_article", page=1))


# 后台文章删除全部
@admin.route("/admin/delallarticle/", methods=["POST"])
def del_all_article():
    article_ids = request.form.getlist("checkbox[]")

    for i in article_ids:
        article = Article.query.get(i)
        db.session.delete(article)
        db.session.commit()
    return redirect(url_for("admin.admin_article", page=1))


# 后台分类管理
@admin.route('/admin/type/')
def admin_type():
    types = ArticleType.query.filter().all()
    data = {
        "types": types,
        "active3": "active",
    }
    return render_template("admin/category.html", **data)


# 后台分类增加
@admin.route('/admin/addtype/', methods=['POST'])
def type_add():
    name = request.form.get("name")
    cname = request.form.get("cname")
    data = {
        "code": 1000,
        "msg": "NO",
    }
    type = ArticleType.query.filter_by(name=name).first()
    if not type:
        type = ArticleType()
        type.name = name
        type.cname = cname
        try:
            db.session.add(type)
            db.session.commit()
            data['msg'] = "添加成功！"
            data['id'] = type.id
        except:
            data['code'] = 1001
            data['msg'] = "添加失败请重试！"

            return jsonify(data)
        return jsonify(data)
    data['msg'] = "分类已存在！"
    return jsonify(data)


# 后台分类删除
@admin.route('/admin/deltype/', methods=['POST'])
def dle_type():
    type_id = request.form.get("type_id")
    data = {
        "code": 1000,
        "msg": "nice",
    }
    type = ArticleType.query.filter_by(id=type_id).first()
    if type:
        db.session.delete(type)
        db.session.commit()
        data['msg'] = "删除成功"
        return jsonify(data)
    data['code'] = 1001
    data['msg'] = "此分类不存在"
    return jsonify(data)


# 后台分类修改
@admin.route('/admin/updatetype/<int:id>/', methods=["POST", "GET"])
def update_type(id):
    if request.method == "GET":
        type = ArticleType.query.get(id)
        data = {
            "active3": "active",
            "type": type,
        }
        return render_template("admin/update-category.html", **data)
    elif request.method == "POST":
        name = request.form.get('name')
        cname = request.form.get('cname')
        type = ArticleType.query.get(id)
        type.name = name
        type.cname = cname
        db.session.commit()
        data = {
            "active3": "active",
            "msg": "修改成功",
            "type": type
        }
        return render_template("admin/update-category.html", **data)


# 后台标签管理
@admin.route('/admin/tags/', methods=["POST", "GET", "PUT"])
def admin_tags():
    if request.method == "GET":
        tags = Tag.query.filter().all()
        data = {
            "tags": tags,
            "active4": "active",
        }
        return render_template("admin/tags.html", **data)
    elif request.method == "POST":
        name = request.form.get("name")
        data = {
            "code": 1000,
            "msg": "NO",
        }
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag()
            tag.name = name
            try:
                db.session.add(tag)
                db.session.commit()
                data['msg'] = "添加成功！"
                data['id'] = tag.id
            except:
                data['code'] = 1001
                data['msg'] = "添加失败请重试！"
                return jsonify(data)
            return jsonify(data)
        data['msg'] = "分类已存在！"
        return jsonify(data)
    elif request.method == "PUT":
        tagid = request.form.get("tagid")
        data = {
            "code": 1000,
            "msg": "nice",
        }
        tag = Tag.query.filter_by(id=tagid).first()
        if type:
            db.session.delete(tag)
            db.session.commit()
            data['msg'] = "删除成功"
            return jsonify(data)
        data['code'] = 1001
        data['msg'] = "此分类不存在"
        return jsonify(data)


# 后台修改标签
@admin.route("/admin/updatetag/<int:id>/", methods=['POST', "GET"])
def update_tag(id):
    if request.method == "GET":
        tag = Tag.query.get(id)
        data = {
            "active4": "active",
            "tag": tag,
        }
        return render_template("admin/update-tag.html", **data)
    elif request.method == "POST":
        name = request.form.get('name')
        tag = Tag.query.get(id)
        tag.name = name
        db.session.commit()
        data = {
            "active4": "active",
            "msg": "修改成功",
            "tag": tag,
        }
        return render_template("admin/update-tag.html", **data)


# 后台评论管理
@admin.route('/admin/comments/', methods=['POST', "GET", "DELETE"])
def admin_comments():
    if request.method == "GET":
        page = int(request.args.get("page", 1))
        pagination = Comment.query.filter(Comment.article_id != None).paginate(page, per_page=10, error_out=False)
        comments = pagination.items
        data = {
            "active5": "active",
            "comments": comments,
            "pagination": pagination,
        }
        return render_template("admin/comment.html", **data)
    elif request.method == 'POST':
        c_id = request.form.get("c_id")
        comment = Comment.query.get(c_id)
        data = {
            "code": 1000,
            "id": comment.id,
            "article": comment.article1.title,
            "content": comment.content,
            "username": comment.username,
        }
        return jsonify(data)
    elif request.method == "DELETE":
        c_id = request.form.get("c_id")
        comment = Comment.query.filter_by(id=c_id).first()
        data = {
            "code": 1000,
            "msg": "",
        }
        if comment:
            db.session.delete(comment)
            db.session.commit()
            data['msg'] = "删除成功！"
            return jsonify(data)
        data['code'] = 1001
        data['msg'] = "没有此评论"
        return jsonify(data)


# 删除多条评论
@admin.route('/admin/delcomments/', methods=['POST'])
def del_comments():
    comments_id = request.form.getlist("checkbox[]")
    for i in comments_id:
        comment = Comment.query.get(i)
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for("admin.admin_comments"))


# 登录验证中间件
@admin.before_request
def login_check():
    path = request.path
    if path == "/admin/login/":
        return render_template("admin/login.html")
    if re.match(r"^/admin/(\w+/)+$", path):
        user_id = session.get("user_id")
        user = AdminUser.query.filter_by(id=user_id).first()
        if user:
            g.user = user
            g.logs = user.logs[-5:]
        else:
            g.user = None
            return redirect(url_for("admin.admin_login"))


# 后台登录页面
@admin.route("/admin/login/", methods=["GET"])
def admin_login():
    return render_template("admin/login.html")


# 后台登录验证
@admin.route("/logincheck/", methods=["POST"])
def login_check():
    username = request.form.get("username")
    password = request.form.get("password")
    user = AdminUser.query.filter_by(username=username).first()
    data = {
        "code": 1001,
        "msg": "",
    }
    if user:
        if password == user.password:
            session['user_id'] = user.id
            data['code'] = 1000
            data['msg'] = "登录成功"
            log = LoginLog()
            log.ip = str(request.remote_addr) + ":" + str(request.environ["REMOTE_PORT"])
            log.loginlogs = user
            db.session.add(log)
            db.session.commit()
            return jsonify(data)
        data['code'] = 1002
        data['msg'] = "密码错误请重试"
        return jsonify(data)
    data['msg'] = "用户名不存在"
    return jsonify(data)


# 后台注销
@admin.route("/admin/logout/")
def admin_logout():
    session.pop("user_id")
    return redirect(url_for("admin.admin_login"))


# 管理员个人信息显示
@admin.route('/admin/perinfo/')
def per_info():
    try:
        user = g.user
    except:
        user = None
    print()
    if user:
        data = {
            "code": 1000,
            "username": user.username,
            "name": user.name,
            "phone": user.phone,
        }
        return jsonify(data)
    return jsonify({"code": 1001, "msg": "请先登录！"})


# 修改个人信息
@admin.route('/admin/change_info/', methods=["POST"])
def change_info():
    old_pwd = request.form.get("old_pwd")
    new_pwd = request.form.get("new_pwd")
    pwd = request.form.get("pwd")
    print(pwd, type(pwd))

    user = g.user
    print(user.password, type(user.password))
    data = {
        "code": 1000,
        "msg": "",
    }
    if user.password != old_pwd:
        data['code'] = 1001
        data['msg'] = "密码错误！"

        return jsonify(data)
    if pwd != new_pwd:
        data['code'] = 1002
        data['msg'] = "两次密码不一致！"
        return jsonify(data)

    user.password = new_pwd
    db.session.commit()
    data['msg'] = "修改成功"
    return jsonify(data)


# 取消或点赞
@blog.route('/articlelike/', methods=["POST"])
def article_like():
    a_id = request.form.get("a_id")
    article = Article.query.get(a_id)
    likes = LikeArticle.query.all()
    like = None
    for i in likes:
        if request.remote_addr == i.ip:
            like = i
    if like:
        db.session.delete(like)
        db.session.commit()
        print(-1)
        return jsonify({"code": -1})
    else:
        like = LikeArticle()
        like.ip = request.remote_addr
        like.articles = article
        db.session.add(like)
        db.session.commit()
        print(1)
        return jsonify({"code": 1})
