from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_profile"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="timezone",
        ),
    ]
