from django.forms import ModelForm, TextInput, PasswordInput, NumberInput, FileInput
from django import forms
from allauth.account.forms import (SignupForm, LoginForm, ChangePasswordForm, ResetPasswordForm)
from django import forms
from allauth.account.forms import LoginForm
from django import forms
from allauth.account.forms import SignupForm

class CustomLoginForm(LoginForm):
    login = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'authentication__box-input',
            'id': 'authentication-input__username',
            'placeholder': 'Username',

        })
    )
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={
            'class': 'authentication__box-input',
            'id': 'authentication-input__password',

        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['login'].widget.attrs.update({'class': 'authentication__box-input',
                                                   'id': 'authentication-input__username',
                                                  'placeholder': '',
                                                   })
        self.fields['password'].widget.attrs.update({'class': 'authentication__box-input',
                                                      'id': 'authentication-input__password',
                                                      })


# class CustomSignupForm(SignupForm):
#     name = forms.CharField(
#                 label='Your name',
#                 max_length=255,
#                 widget=forms.TextInput(attrs={'placeholder': 'Your name'})
#             )
#
#     email = forms.EmailField(
#         label='E-mail',
#         max_length=255,
#         widget=forms.EmailInput(attrs={'placeholder': 'E-mail', 'class': 'authentication__box-input', 'id': 'authentication-input__password'})
#     )
#
#     password1 = forms.CharField(
#         label='Create password',
#         widget=forms.PasswordInput(attrs={'placeholder': 'Create password', 'class': 'authentication__box-input', 'id': 'authentication-input__password'})
#     )
#
#     agree_terms = forms.BooleanField(
#         label='I agree to terms & conditions',
#         widget=forms.CheckboxInput(attrs={'class': 'authentication__registration-check', 'id': 'authentication__registration-check'}),
#         required=True
#     )
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         # удаляем поля, кроме full_name, email и password1
#         self.fields.pop('username', None)
#         self.fields.pop('first_name', None)
#         self.fields.pop('last_name', None)
#         self.fields.pop('password2', None)
#
#         # меняем лейблы полей
#         self.fields['name'].label = 'Full Name'
#         self.fields['email'].label = 'E-mail'
#         self.fields['password1'].label = 'Create password'
#         self.fields['agree_terms'].label = 'I agree to terms & conditions'
#
#     def save(self, request):
#         # вызываем родительский метод save и возвращаем результат
#         user = super().save(request)
#         user.full_name = self.cleaned_data.get('full_name')
#         user.save()
#         return user
class CustomSignupForm(SignupForm):
    name = forms.CharField(
        label='Your name',
        max_length=45,
        widget=forms.TextInput(attrs={'placeholder': '', 'class': 'authentication__box-input', 'id': 'authentication-input__username'})
    )
    email = forms.EmailField(
            label='E-mail',
            max_length=35,
            widget=forms.EmailInput(attrs={'placeholder': '', 'class': 'authentication__box-input', 'id': 'authentication-input__password'})
        )
    password = forms.CharField(
            label='Create password',
            max_length=35,
            widget=forms.PasswordInput(attrs={'placeholder': '', 'class': 'authentication__box-input', 'id': 'authentication-input__password'})
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # удаляем поля, кроме name, email и password
        self.fields.pop('username', None)
        self.fields.pop('first_name', None)
        self.fields.pop('last_name', None)
        self.fields.pop('password2', None)

        # меняем лейблы полей
        self.fields['name'].label = 'Your name'
        self.fields['email'].label = 'Email'
        self.fields['password1'].label = 'Create password'


    def save(self, request):
        # вызываем родительский метод save и возвращаем результат
        user = super().save(request)
        user.name = self.cleaned_data.get('name')
        user.save()
        return user

class CustomResetPasswordForm(ResetPasswordForm):
    email = forms.EmailField(
        label='E-mail',
        max_length=35,
        widget=forms.EmailInput(
            attrs={'placeholder': '', 'class': 'authentication__box-input', 'id': 'authentication-input__password'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Удаление поля "username" из формы
        self.fields.pop('username', None)
        # # Изменение лейбла для поля "email"
        # self.fields['email'].label = _('Email')
