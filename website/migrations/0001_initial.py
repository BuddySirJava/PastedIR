# Generated manually based on website/models.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('displayname', models.CharField(max_length=255)),
                ('alias', models.CharField(db_index=True, max_length=255, unique=True)),
            ],
            options={
                'ordering': ['displayname'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['username'],
            },
        ),
        migrations.CreateModel(
            name='Paste',
            fields=[
                ('id', models.CharField(db_index=True, editable=False, max_length=6, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('one_time', models.BooleanField(db_index=True, default=False)),
                ('view_count', models.IntegerField(default=0)),
                ('expires', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('salt', models.CharField(blank=True, default=None, max_length=24, null=True)),
                ('iv', models.CharField(blank=True, default=None, max_length=24, null=True)),
                ('ciphertext', models.TextField()),
                ('lang', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.language')),
                ('owner', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.user')),
            ],
            options={
                'ordering': ['-created'],
                'indexes': [
                    models.Index(fields=['created', 'expires'], name='website_paste_created_expires_idx'),
                    models.Index(fields=['one_time', 'view_count'], name='website_paste_one_time_view_count_idx'),
                ],
            },
        ),
    ] 