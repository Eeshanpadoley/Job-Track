import django.core.validators
import accounts.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def preserve_existing_rows(apps, schema_editor):
    # New nullable fields leave existing application records intact.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_jobapplication_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Example: Data Analyst Resume', max_length=120)),
                ('target_role', models.CharField(blank=True, max_length=120)),
                ('file', models.FileField(upload_to=accounts.models.resume_upload_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])])),
                ('notes', models.CharField(blank=True, max_length=250)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resumes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='jobapplication', name='resume',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applications', to='accounts.resume'),
        ),
        migrations.AddField(
            model_name='jobapplication', name='follow_up_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='jobapplication', name='interview_notes',
            field=models.TextField(blank=True, help_text='Interview date, recruiter contact, preparation notes, questions, etc.'),
        ),
    ]
