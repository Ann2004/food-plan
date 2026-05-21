from difflib import SequenceMatcher

from django.contrib.auth.password_validation import CommonPasswordValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext


class CustomUserAttributeSimilarityValidator:
    def validate(self, password, user=None):

        if not user:
            return

        user_attributes = [
            user.username,
            user.email,
            user.first_name,
        ]

        for attribute in user_attributes:
            if not attribute:
                continue

            similarity = SequenceMatcher(
                a=password.lower(),
                b=attribute.lower(),
            ).ratio()

            if similarity > 0.7:
                raise ValidationError(
                    gettext("Пароль слишком похож на ваш email или имя."),
                    code="password_too_similar",
                )

    def get_help_text(self):
        return gettext("Пароль не должен быть похож на email или имя.")


class CustomMinimumLengthValidator:
    def validate(self, password, user=None):

        if len(password) < 8:
            raise ValidationError(
                gettext("Пароль должен содержать минимум 8 символов."),
                code="password_too_short",
            )

    def get_help_text(self):
        return gettext("Ваш пароль должен содержать минимум 8 символов.")


class CustomCommonPasswordValidator(CommonPasswordValidator):
    def validate(self, password, user=None):

        try:
            super().validate(password, user)

        except ValidationError:
            raise ValidationError(
                gettext("Пароль слишком простой."),
                code="password_too_common",
            )

    def get_help_text(self):
        return gettext("Пароль не должен быть слишком простым.")


class CustomNumericPasswordValidator:
    def validate(self, password, user=None):

        if password.isdigit():
            raise ValidationError(
                gettext("Пароль не должен состоять только из цифр."),
                code="password_entirely_numeric",
            )

    def get_help_text(self):
        return gettext("Пароль не должен состоять только из цифр.")
