from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


def resume_upload_path(instance, filename):
    return f"resumes/user_{instance.user_id}/{filename}"


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField(max_length=120, help_text="Example: Data Analyst Resume")
    target_role = models.CharField(max_length=120, blank=True)
    file = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],
    )
    notes = models.CharField(max_length=250, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    application_source = models.CharField(max_length=100)
    salary = models.CharField(max_length=100, blank=True)
    required_skills = models.TextField()
    application_status = models.CharField(max_length=50, default="Applied")
    application_date = models.DateField()
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications")
    follow_up_date = models.DateField(null=True, blank=True)
    interview_notes = models.TextField(blank=True, help_text="Interview date, recruiter contact, preparation notes, questions, etc.")

    def __str__(self):
        return f"{self.company_name} - {self.job_title}"
