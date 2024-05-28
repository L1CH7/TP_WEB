from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
# from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from django.urls import reverse

from app.forms import LoginForm, RegisterForm, SettingsForm, AskForm, CommentForm
from app.models import Question, Tag, Comment, Profile


TOP_TAGS = Tag.manager.top_of_tags(10)
TOP_USERS = Profile.manager.get_top_users(10)


def paginate(objects,request, per_page=20):
    page = request.GET.get('page', 1)
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
    items_page = paginate(questions, request, 20)
    return render(request, 'index.html', {'questions': items_page, 'pages': items_page, 'tags': TOP_TAGS, 'users': TOP_USERS})


def question(request, question_id):
    try:
        item = Question.manager.get_question_by_id(question_id)
    except:
        return HttpResponseBadRequest()
    comments = Comment.manager.get_comments_ordered_by_likes(question_id)
    items_page = paginate(comments, request, 30)
    if request.method == 'GET':
        comment_form = CommentForm()
    if request.method == 'POST':
        content = request.POST.get('content')
        profile = Profile.manager.get_profile_by_id(request.user.id)
        question = Question.manager.get_question_by_id(question_id)
        comment_form = CommentForm(request.POST, question=question, author=profile, initial={'content':content})
        if comment_form.is_valid():
            new_comment = comment_form.save()
            if new_comment:
                return redirect('question', question_id=question_id)
    return render(request, 'question.html', {'question': item, 'comments': items_page,
                                             'pages': items_page, 'question_id': question_id, 'tags': TOP_TAGS,'users': TOP_USERS, 'comment_form': comment_form})


@login_required(login_url='/login/', redirect_field_name='continue')
def ask(request):
    if request.method == "GET":
        ask_form = AskForm()
    if request.method == "POST":
        title, content, tags = request.POST['title'], request.POST['content'], request.POST['tags']
        profile = Profile.manager.get_profile_by_id(request.user.id)
        ask_form = AskForm(request.POST, author=profile, initial={"title": title, "content":content, "tags":tags})
        if ask_form.is_valid():
            new_question = ask_form.save()
            if new_question:
                return redirect('question', question_id=new_question.id)
    return render(request, 'ask.html', {'tags': TOP_TAGS,'users': TOP_USERS, 'ask_form':ask_form})


def signup(request):

    if request.method == "GET":
        user_form = RegisterForm()
    if request.method == "POST":
        user_form = RegisterForm(request.POST, request.FILES)
        if user_form.is_valid():
            user = user_form.save()
            new_user = authenticate(request, username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password'])
            if user:
                login(request, new_user)
                return redirect(reverse('index'))
            else:
                user_form.add_error(None, "User saving error!")
    return render(request, 'signup.html', {'tags': TOP_TAGS,'users': TOP_USERS, 'user_form': user_form})


def log_in(request):
    if request.method == 'GET':
        login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user is not None:
                login(request, user)
                return redirect(request.GET.get('continue', 'index'))
    return render(request, 'login.html', {'tags': TOP_TAGS, 'users': TOP_USERS, 'login_form': login_form})


def log_out(request):
    auth.logout(request)
    return redirect(reverse('login'))


def hot(request):
    items_page = paginate(Question.manager.get_top_questions(), request)
    return render(request, 'hot.html', {'questions': items_page, 'pages': items_page, 'tags': TOP_TAGS,'users': TOP_USERS})


@login_required(login_url='/login/', redirect_field_name='continue')
def settings(request):
    if request.method == 'GET':
        user_id = request.user.id
        user, profile = Profile.manager.get_user_by_id(user_id), Profile.manager.get_profile_by_id(user_id)
        settings_form = SettingsForm(initial={'username': user.username, 'email': user.email, 'avatar': profile.avatar})
    if request.method == 'POST':
        curr_username, email, avatar = request.user.username, request.POST['email'], request.POST['avatar']
        settings_form = SettingsForm(request.POST, request=request, initial={'username': curr_username, 'email': email, 'avatar': avatar})
        if settings_form.is_valid():
            settings_form.update()
    return render(request, 'settings.html', {'tags': TOP_TAGS,'users': TOP_USERS, 'settings_form': settings_form})


def tag(request, tag_name):
    tag_item = Tag.manager.get_questions_by_tag(tag_name)
    items_page = paginate(tag_item.order_by('-create_date'), request)
    return render(request, 'tag.html', {'tag': tag_name, 'questions': items_page, 'pages': items_page, 'tags': TOP_TAGS,'users': TOP_USERS})