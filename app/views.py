from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from app.models import Question, Tag, Comment, Profile


TOP_TAGS = Tag.manager.top_of_tags(10)
TOP_USERS = Profile.manager.get_top_users(10)

def paginate(objects, page, per_page=10):
    paginator = Paginator(objects, per_page)
    default_page = 1
    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(default_page)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)
    return items_page


def index(request):
    questions = Question.manager.get_new_questions()
    page = request.GET.get('page', 1)
    items_page = paginate(questions, page, 20)
    return render(request, 'index.html', {'questions': items_page, 'pages': items_page, 'tags': TOP_TAGS, 'users': TOP_USERS})


def question(request, question_id):
    try:
        item = Question.manager.get_question_by_id(question_id)
    except:
        return HttpResponseBadRequest()
    page = request.GET.get('page', 1)
    comments = Comment.manager.get_comments_ordered_by_likes(question_id)
    items_page = paginate(comments, page, 30)
    return render(request, 'question.html', {'question': item, 'comments': items_page,
                                             'pages': items_page, 'question_id': question_id, 'tags': TOP_TAGS,'users': TOP_USERS})


def ask(request):
    return render(request, 'ask.html', {'tags': TOP_TAGS,'users': TOP_USERS})


def signup(request):
    return render(request, 'signup.html', {'tags': TOP_TAGS,'users': TOP_USERS})


def log_in(request):
    return render(request, 'login.html', {'tags': TOP_TAGS,'users': TOP_USERS})


def hot(request):
    page = request.GET.get('page', 1)
    items_page = paginate(Question.manager.get_top_questions(), page)
    return render(request, 'hot.html', {'questions': items_page, 'pages': items_page, 'tags': TOP_TAGS,'users': TOP_USERS})


def settings(request):
    return render(request, 'settings.html', {'tags': TOP_TAGS,'users': TOP_USERS})


def tag(request, tag_name):
    page = request.GET.get('page', 1)
    tag_item = Tag.manager.get_questions_by_tag(tag_name)
    items_page = paginate(tag_item.order_by('-create_date'), page)
    return render(request, 'tag.html', {'tag': tag_name, 'questions': items_page, 'pages': items_page, 'tags': TOP_TAGS,'users': TOP_USERS})