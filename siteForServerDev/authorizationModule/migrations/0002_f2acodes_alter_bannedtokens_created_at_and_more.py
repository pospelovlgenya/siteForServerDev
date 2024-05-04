# Generated by Django 5.0.1 on 2024-05-04 09:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorizationModule', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='F2ACodes',
            fields=[
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('code', models.PositiveIntegerField(db_index=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='bannedtokens',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='updatedtokens',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.CreateModel(
            name='UserTokens',
            fields=[
                ('token', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('expired_at', models.PositiveIntegerField(db_index=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]