from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 
from .models import Profile
class UserRegisterForm(UserCreationForm):
    email= forms.EmailField()

    class Meta:
        model=User
        fields = ['username','email','password1','password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

   

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name',
            'phone',
            'image',
            'address',
            'city',
            'state',
            'country',
            'postal_code',
        ]

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()


# users/forms.py
from django import forms
from django.contrib.auth.password_validation import validate_password

class SetNewPasswordForm(forms.Form):
    password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        validators=[validate_password],
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data