# Generated by Django 5.0.6 on 2024-05-20 14:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('members', '0001_initial'),
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='tasks',
            field=models.ManyToManyField(through='tasks.MemberTask', to='tasks.task'),
        ),
        migrations.AddField(
            model_name='member',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='friend',
            name='from_member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_requests_sent', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friend',
            name='to_member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_requests_received', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='member',
            name='friends',
            field=models.ManyToManyField(related_name='related_to', through='members.Friend', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='status',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to=settings.AUTH_USER_MODEL),
        ),
    ]
