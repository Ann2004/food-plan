from datetime import timedelta

from django.db import migrations, models
from django.utils import timezone


def populate_created_at(apps, schema_editor):
    Subscription = apps.get_model("core", "Subscription")
    for sub in Subscription.objects.filter(created_at__isnull=True):
        sub.created_at = timezone.now() - timedelta(days=30)
        sub.save(update_fields=["created_at"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0019_0021_add_subscription_user_number_squashed"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                null=True,
                verbose_name="Дата создания",
            ),
        ),
        migrations.RunPython(
            code=populate_created_at,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
