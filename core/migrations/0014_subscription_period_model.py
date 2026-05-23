import django.db.models.deletion
from django.db import migrations, models


def create_periods_and_migrate_subscriptions(apps, schema_editor):
    SubscriptionPeriod = apps.get_model("core", "SubscriptionPeriod")
    Subscription = apps.get_model("core", "Subscription")

    periods_data = [
        (1, "1 месяц", 1.0),
        (3, "3 месяца", 1.6),
        (6, "6 месяцев", 1.8),
        (12, "12 месяцев", 2.0),
    ]

    period_map = {}
    for months, name, multiplier in periods_data:
        obj = SubscriptionPeriod.objects.create(
            months=months, name=name, price_multiplier=multiplier
        )
        period_map[months] = obj

    for subscription in Subscription.objects.all():
        subscription.period_new = period_map[subscription.period]
        subscription.save(update_fields=["period_new"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_move_allergies_to_ingredient"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubscriptionPeriod",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "months",
                    models.PositiveSmallIntegerField(
                        unique=True, verbose_name="Месяцев"
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=50, verbose_name="Название"),
                ),
                (
                    "price_multiplier",
                    models.DecimalField(
                        decimal_places=2,
                        default=1.0,
                        max_digits=5,
                        verbose_name="Множитель цены",
                    ),
                ),
            ],
            options={
                "verbose_name": "Период подписки",
                "verbose_name_plural": "Периоды подписки",
            },
        ),
        migrations.AddField(
            model_name="subscription",
            name="period_new",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.subscriptionperiod",
                verbose_name="Период подписки",
            ),
        ),
        migrations.RunPython(
            create_periods_and_migrate_subscriptions,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="subscription",
            name="period",
        ),
        migrations.RenameField(
            model_name="subscription",
            old_name="period_new",
            new_name="period",
        ),
        migrations.AlterField(
            model_name="subscription",
            name="period",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core.subscriptionperiod",
                verbose_name="Период подписки",
            ),
        ),
    ]
