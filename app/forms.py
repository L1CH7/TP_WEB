from django import forms
from django.contrib import auth
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from app.models import Profile, Question, Tag, Comment


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(min_length=4, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        user = auth.authenticate(request=self.request, **self.cleaned_data)
        if user is None:
            raise ValidationError({'password': 'Wrong password or username'})


class RegisterForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(min_length=4, widget=forms.PasswordInput)
    password_check = forms.CharField(label="Repeat password", widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        password = self.cleaned_data['password']
        password_check = self.cleaned_data['password_check']

        if password != password_check:
            raise ValidationError({'password': 'Passwords do not match', 'password_check': ''})

    def save(self, **kwargs):
        data = self.cleaned_data

        avatar = data['avatar']
        data.pop('avatar')
        data.pop('password_check')

        user = User.objects.create_user(**data)
        if not user:
            self.add_error(None, "User saving error!")
            return None
        profile = Profile.manager.create(user=user, avatar=avatar)
        if not profile:
            self.add_error(None,"Profile saving error!")
            return None

        return user

class SettingsForm(forms.Form):
    username = forms.CharField(disabled=True)
    email = forms.EmailField(required=False)
    password = forms.CharField(min_length=4, widget=forms.PasswordInput, label="Old password")
    new_password = forms.CharField(min_length=4, widget=forms.PasswordInput, label="New password", required=False)
    password_check = forms.CharField(widget=forms.PasswordInput, label="Repeat password", required=False)
    avatar = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SettingsForm, self).__init__(*args, **kwargs)

    def clean_password_check(self):
        new_password = self.cleaned_data['new_password']
        password_for_checking = self.cleaned_data['password_check']
        if password_for_checking != new_password:
            raise ValidationError("Passwords don't match!")
        return password_for_checking

    def clean_password(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = auth.authenticate(request=self.request, username=username, password=password)
        if user is None:
            raise ValidationError("The old password is incorrect!")
        return password

    def update(self):
        data = self.cleaned_data

        username = data['username']
        new_password = data['new_password']
        avatar = data['avatar']

        data.pop('username')
        data.pop('password')
        data.pop('new_password')
        data.pop('password_check')
        data.pop('avatar')

        User.objects.filter(username=username).update(**data)

        user_tmp = User.objects.get(username=username)
        if not user_tmp:
            self.add_error(field=None, error="User updating error!")
            return None

        profile = Profile.manager.filter(user_id=user_tmp.id).update(avatar=avatar)
        if not profile:
            self.add_error(field=None, error="Profile updating error!")
            return None

        if new_password != '':
            user_tmp.set_password(new_password)
            user_tmp.save()

            test_auth_user = auth.authenticate(request=self.request, username=username, password=new_password)
            if test_auth_user is not None:
                login(self.request, test_auth_user)
            else:
                self.add_error(field=None, error="User authenticating error!")

        return user_tmp

class AskForm(forms.ModelForm):
    title = forms.CharField(max_length=64)
    content = forms.CharField(widget=forms.Textarea, max_length=255)
    tags = forms.CharField(help_text="Enter up to three tags separated by a comma")

    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']

    def __init__(self, *args, **kwargs):
        self.profile_id = kwargs.pop('author', None)
        super(AskForm, self).__init__(*args, **kwargs)

    def clean_tags(self):
        input_tags = self.cleaned_data['tags']
        tags = input_tags.split(',')
        if len(tags) > 3:
            raise ValidationError("More than three tags have been entered!")
        if len(tags) != len(set(tags)):
            raise ValidationError("Tags must be unique!")
        return input_tags

    def save(self):
        title, content, tags = self.cleaned_data['title'], self.cleaned_data['content'], self.cleaned_data['tags']
        new_question = Question(title=title, content=content, author=self.profile_id)
        new_question.save()

        if not new_question:
            self.add_error(field=None, error="Question saving error!")
            return None
        splitted_tags = [x.strip() for x in tags.split(',')]
        for tag in splitted_tags:
            some_tag = Tag.manager.update_or_create(name=tag)[0]
            if not some_tag:
                self.add_error(field=None, error="Tag saving error!")
                return None
            new_question.tags.add(some_tag)

        return new_question

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, max_length=255, label="")
    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question', None)
        self.profile = kwargs.pop('author', None)
        super(CommentForm, self).__init__(*args, **kwargs)

    def save(self):
        content = self.cleaned_data['content']
        comment = Comment.manager.create(content=content, author=self.profile, question=self.question)
        if not comment:
            self.add_error(field=None, error="Comment saving error!")
            return None
        return comment
