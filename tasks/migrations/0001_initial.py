import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Situation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('swimlane', models.CharField(default='', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='MemberTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('members', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('content', models.TextField(default='')),
                ('urgency', models.CharField(choices=[('高', '高'), ('中', '中'), ('低', '低')], default='', max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('created_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='assigned_tasks', through='tasks.MemberTask', to=settings.AUTH_USER_MODEL)),
                ('situation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.situation')),
            ],
        ),
        migrations.AddField(
            model_name='membertask',
            name='tasks',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tasks.task'),
        ),
    ]
