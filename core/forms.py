from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Profile, Review


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "id": "email"}),
    )

    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "id": "password"}),
    )

    error_messages = {
        "invalid_login": "Неправильный email или пароль.",
        "inactive": "Этот аккаунт отключен.",
    }

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        login_email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if login_email and password:
            user = authenticate(
                username=login_email,
                password=password,
            )

            if user is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )

            if not user.is_active:
                raise forms.ValidationError(
                    self.error_messages["inactive"],
                    code="inactive",
                )

            self.user_cache = user

        return cleaned_data

    def get_user(self):
        return self.user_cache


class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "first_name",
            }
        ),
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "id": "email",
            }
        ),
    )

    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "password",
            }
        ),
    )

    confirm_password = forms.CharField(
        label="Подтверждение пароля",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "password-confirm",
            }
        ),
    )

    error_messages = {
        "password_mismatch": "Пароли не совпадают.",
        "email_exists": "Пользователь с таким email уже существует.",
    }

    def clean_email(self):

        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                self.error_messages["email_exists"],
                code="email_exists",
            )

        return email

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        email = cleaned_data.get("email")
        first_name = cleaned_data.get("first_name")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )

        if password:
            temp_user = User(
                username=email,
                email=email,
                first_name=first_name,
            )

            try:
                validate_password(password, user=temp_user)

            except forms.ValidationError as error:
                self.add_error("password", error)

        return cleaned_data

    def save(self):

        return User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
        )


class ProfileForm(forms.Form):
    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "first_name",
            }
        ),
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "id": "email",
            }
        ),
    )

    new_password = forms.CharField(
        label="Новый пароль",
        required=False,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "password",
            }
        ),
    )

    confirm_password = forms.CharField(
        label="Подтверждение пароля",
        required=False,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "password-confirm",
            }
        ),
    )

    avatar = forms.ImageField(
        label="Аватар",
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "d-none",
                "id": "avatar-input",
                "accept": "image/*",
            }
        ),
    )

    error_messages = {
        "password_mismatch": "Пароли не совпадают.",
        "email_exists": "Пользователь с таким email уже существует.",
    }

    def __init__(self, *args, user=None, **kwargs):

        self.current_user = user

        super().__init__(*args, **kwargs)

    def clean_email(self):

        email = self.cleaned_data.get("email")

        if (
            email
            and User.objects.exclude(pk=self.current_user.pk)
            .filter(email=email)
            .exists()
        ):
            raise forms.ValidationError(
                self.error_messages["email_exists"],
                code="email_exists",
            )

        return email

    def clean(self):

        cleaned_data = super().clean()

        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        email = cleaned_data.get("email")
        first_name = cleaned_data.get("first_name")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )

        if new_password:
            temp_user = User(
                username=email,
                email=email,
                first_name=first_name,
            )

            try:
                validate_password(new_password, user=temp_user)

            except forms.ValidationError as error:
                self.add_error("new_password", error)

        return cleaned_data

    def save(self):

        user = self.current_user

        user.first_name = self.cleaned_data["first_name"]
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]

        new_password = self.cleaned_data.get("new_password")

        if new_password:
            user.set_password(new_password)

        user.save()

        avatar = self.cleaned_data.get("avatar")

        if avatar:
            profile, _ = Profile.objects.get_or_create(user=user)

            profile.avatar = avatar
            profile.save()

        return user


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'rating-input'}),
        label="Ваша оценка"
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'text', 'image']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Поделитесь вашим впечатлением о сервисе FoodPlan...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'text': 'Текст отзыва',
            'image': 'Фото'
        }