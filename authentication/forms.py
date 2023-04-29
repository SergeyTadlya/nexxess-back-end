from django.forms import ModelForm, TextInput, PasswordInput, NumberInput, FileInput
from allauth.account.forms import (SignupForm, LoginForm, ChangePasswordForm, ResetPasswordForm)
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django import forms


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


class CustomSignupForm(SignupForm):
    name = forms.CharField(
        label='Your name',
        max_length=45,
        widget=forms.TextInput(
            attrs={'placeholder': '', 'class': 'authentication__box-input', 'id': 'authentication-input__username'})
    )
    email = forms.EmailField(
        label='E-mail',
        max_length=35,
        widget=forms.TextInput(
            attrs={'placeholder': '', 'class': 'authentication__box-input', 'id': 'authentication-input__password'})
    )

    password1 = forms.CharField(
        label='Create password',
        max_length=35,
        widget=forms.PasswordInput(
            attrs={'placeholder': '', 'class': 'authentication__box-input', 'id': 'authentication-input__password'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # remove fields username and password2
        self.fields.pop('username', None)
        self.fields.pop('first_name', None)
        self.fields.pop('last_name', None)
        self.fields.pop('password2', None)

        self.fields['name'].label = 'Your name'
        self.fields['email'].label = 'E-mail'
        self.fields['password1'].widget.attrs.update({'class': 'authentication__box-input',
                                                      'id': 'authentication-input__password',
                                                      'placeholder': '',
                                                      })

    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data.get('name')
        user.save()
        return user


class CustomResetPasswordForm(ResetPasswordForm):
    email = forms.EmailField(
        label='E-mail',
        max_length=35,
        widget=forms.TextInput(
            attrs={'placeholder': '', 'class': 'authentication__box-input', 'id': 'authentication-input__password'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)


class EditProfileForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
