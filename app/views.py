from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.http import HttpResponse
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)

QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'content': f'This is a wider card {i}...',
    } for i in range(20)
]

TAGS = {"tag1", "tag2", "tag3", "tag4", "tag5", "tag6",
        "Primary", "Secondary", "Success", "Warning", "Danger", "Info", "Light", "Dark"}


def paginate(objects, page, per_page=5):
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
    page = request.GET.get('page', 1)
    items_page = paginate(QUESTIONS, page)
    return render(request, 'index.html', {'questions': items_page, 'pages': items_page})


def question(request, question_id):
    if question_id > 19:
        return HttpResponseBadRequest()
    page = request.GET.get('page', 1)
    comments = [
        {
            'id': i,
            'content': f'Long lorem ipsum {i}...',
        } for i in range(30)
    ]
    items_page = paginate(comments, page)
    item = QUESTIONS[question_id]
    return render(request, 'question.html', {'question': item, 'comments': items_page,
                                             'pages': items_page, 'question_id': question_id})


def ask(request):
    return render(request, 'ask.html')


def signup(request):
    return render(request, 'signup.html')


def login(request):
    return render(request, 'login.html')

def logout(request):
    return render(request, 'logout.html')


def hot(request):
    page = request.GET.get('page', 1)
    items_page = paginate(QUESTIONS, page)
    return render(request, 'hot.html', {'questions': items_page, 'pages': items_page})


def settings(request):
    return render(request, 'settings.html')


def tag(request, tag_name):
    if tag_name not in TAGS:
        return HttpResponseBadRequest()
    page = request.GET.get('page', 1)
    items_page = paginate(QUESTIONS, page)
    return render(request, 'tag.html', {'tag': tag_name, 'questions': items_page, 'pages': items_page})