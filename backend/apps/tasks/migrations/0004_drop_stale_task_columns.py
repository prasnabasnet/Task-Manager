from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0003_remove_task_assignee_task_assignees"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE tasks_task "
                "DROP COLUMN IF EXISTS department_id, "
                "DROP COLUMN IF EXISTS organization_id;"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
