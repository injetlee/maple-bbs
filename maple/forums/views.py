#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# *************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   File Name: view.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2015-11-25 02:21:04
# *************************************************************************
from flask import (render_template, Blueprint)
from maple.question.models import Tags, Questions
from maple import app, login_serializer, login_manager, db,cache
from maple.user.models import User
from maple.board.models import Board_F
from maple.group.models import Group

site = Blueprint('forums', __name__)


@login_manager.token_loader
def load_token(token):
    max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()
    data = login_serializer.loads(token, max_age=max_age)
    user = User.load_by_name(data[0])
    if user and data[1] == user.password:
        return user
    return None


@login_manager.user_loader
def user_loader(id):
    user = User.query.get(int(id))
    return user


@site.route('/', methods=['GET'])
@cache.cached(timeout=180)
def index():
    from sqlalchemy import or_
    clubs = Group.query.limit(15)
    schools = Questions.query.join(Questions.tags).filter(
        Tags.name == '新闻').offset(0).limit(5)
    wulwxys = Questions.query.join(Questions.tags).filter(
        Tags.name == '新闻').offset(5).limit(5)
    jidians = Questions.query.join(Questions.tags).filter(
        Tags.name == '新闻').offset(10).limit(5)
    bss = Questions.query.join(Questions.tags).filter(Tags.name ==
                                                      '新闻').offset(15).limit(5)
    masters = Questions.query.join(Questions.tags).filter(or_(
        Tags.name == '考研', Tags.name == '研究生新闻')).limit(5)
    questions = Questions.query.limit(16)
    return render_template('index/index.html',
                           questions=questions,
                           schools=schools,
                           wulwxys=wulwxys,
                           bss=bss,
                           jidians=jidians,
                           masters=masters,
                           clubs=clubs)


@site.route('/index', methods=['GET'])
@cache.cached(timeout=180)
def forums():
    boards = Board_F.query.all()
    return render_template('index/forums.html', boards=boards)


@site.route('/t', methods=['GET'], defaults={'tag': None, 'number': None})
@site.route('/t/<tag>', methods=['GET'], defaults={'number': 1})
@site.route('/t/<tag>?page=<int:number>', methods=['GET'])
@cache.cached(timeout=180)
def tag(tag, number):
    if tag is not None:
        pages = Questions.query.join(Questions.tags).\
            filter(Tags.name == tag).count()
        pages = pages // 20 + 1
        questions = Questions.query.join(Questions.tags).\
            filter(Tags.name == tag).offset((number - 1)*20).limit(20)
        return render_template('index/tags.html',
                               questions=questions,
                               tag=tag,
                               pages=pages,
                               number=number)
    else:
        tags = db.session.query(Tags.name).group_by(Tags.name).all()
        return render_template('index/all_tags.html', tags=tags)


# @site.route('/about', methods=['GET'])
# @cache.cached(timeout=180)
# def about():
#     return render_template('index/about.html')
