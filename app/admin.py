from django.contrib import admin
from app.models import Profile, Question, Tag, QuestionLike, CommentLike, Comment
# Register your models here.

admin.site.register([Profile, Question, Tag, QuestionLike, CommentLike, Comment])