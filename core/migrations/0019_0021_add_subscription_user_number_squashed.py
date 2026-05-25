from django.conf import settings
from django.db import migrations, models


def populate_user_numbers(apps, schema_editor):
    Subscription = apps.get_model("core", "Subscription")
    seen_users = set()
    for sub in Subscription.objects.order_by("id"):
        if sub.user_id not in seen_users:
            seen_users.add(sub.user_id)
            number = 0
        number += 1
        sub.user_number = number
        sub.save(update_fields=["user_number"])


class Migration(migrations.Migration):

    replaces = [
        ("core", "0019_add_subscription_user_number"),
        ("core", "0020_populate_subscription_user_number"),
        ("core", "0021_make_user_number_not_null"),
    ]

    dependencies = [
        ("core", "0018_add_promocode_fk_to_subscription"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="profile",
            options={"verbose_name": "Профиль", "verbose_name_plural": "Профили"},
        ),
        migrations.AddField(
            model_name="subscription",
            name="user_number",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="Номер подписки"
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(
                blank=True, null=True, upload_to="avatars/", verbose_name="Аватар"
            ),
        ),
        migrations.AddConstraint(
            model_name="subscription",
            constraint=models.UniqueConstraint(
                fields=("user", "user_number"), name="unique_user_sub_number"
            ),
        ),
        migrations.RunPython(
            code=populate_user_numbers,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="subscription",
            name="user_number",
            field=models.PositiveSmallIntegerField(
                verbose_name="Номер подписки",
            ),
        ),
    ]
