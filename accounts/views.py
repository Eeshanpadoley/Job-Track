from collections import Counter
import csv
import re

import pandas as pd
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import JobApplication, Resume


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next") or "dashboard")
        messages.error(request, "We couldn't sign you in. Check your username and password.")
    return render(request, "accounts/login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        if not username or not email or not password:
            messages.error(request, "Please fill in every required field.")
        elif len(password) < 8:
            messages.error(request, "Use a password with at least 8 characters.")
        elif password != confirm_password:
            messages.error(request, "The passwords do not match.")
        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, "That username is already taken. Try another one.")
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email already exists.")
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Your account is ready. Sign in to continue!")
            return redirect("login")
    return render(request, "accounts/register.html")


@login_required(login_url="login")
def dashboard_view(request):
    applications = JobApplication.objects.filter(user=request.user)
    total = applications.count()
    interviews = applications.filter(application_status__iexact="Interview").count()
    offers = applications.filter(application_status__iexact="Offer").count()
    rejections = applications.filter(application_status__iexact="Rejected").count()
    responses = interviews + offers + rejections
    today = timezone.localdate()
    context = {
        "total_applications": total, "interviews": interviews, "offers": offers,
        "rejections": rejections, "responses": responses,
        "response_rate": round(responses / total * 100, 1) if total else 0,
        "recent_applications": applications.select_related("resume").order_by("-application_date", "-id")[:5],
        "resume_count": Resume.objects.filter(user=request.user).count(),
        "upcoming_followups": applications.filter(follow_up_date__gte=today).exclude(application_status__iexact="Rejected").order_by("follow_up_date")[:5],
        "overdue_followups": applications.filter(follow_up_date__lt=today).exclude(application_status__iexact="Rejected").order_by("follow_up_date")[:5],
    }
    return render(request, "accounts/dashboard.html", context)


@login_required(login_url="login")
def analytics_view(request):
    return pandas_analysis_view(request)


@login_required(login_url="login")
def add_application_view(request):
    if request.method == "POST":
        required = [request.POST.get(k, "").strip() for k in ("company_name", "job_title", "required_skills")]
        if not all(required):
            messages.error(request, "Company, job title and required skills are required.")
            return render(request, "accounts/add_application.html", {"form_title": "Add application", "resumes": Resume.objects.filter(user=request.user), "status_options": ["Applied", "Assessment", "Interview", "Offer", "Rejected", "On Hold"], "today": timezone.localdate().isoformat()})
        application_date = request.POST.get("application_date") or timezone.localdate().isoformat()
        try:
            JobApplication.objects.create(
                user=request.user,
                company_name=required[0], job_title=required[1],
                location=request.POST.get("location", "").strip() or "Not specified",
                application_source=request.POST.get("application_source") or request.POST.get("source") or "Other",
                salary=request.POST.get("salary", "").strip(),
                required_skills=required[2],
                application_status=request.POST.get("application_status") or request.POST.get("status") or "Applied",
                application_date=application_date,
                resume=Resume.objects.filter(user=request.user, id=request.POST.get("resume") or None).first(),
                follow_up_date=request.POST.get("follow_up_date") or None,
                interview_notes=request.POST.get("interview_notes", "").strip(),
            )
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid application date.")
            return render(request, "accounts/add_application.html", {"form_title": "Add application", "resumes": Resume.objects.filter(user=request.user), "status_options": ["Applied", "Assessment", "Interview", "Offer", "Rejected", "On Hold"], "today": timezone.localdate().isoformat()})
        messages.success(request, "Job application added successfully.")
        return redirect("my_applications")
    return render(request, "accounts/add_application.html", {"form_title": "Add application", "resumes": Resume.objects.filter(user=request.user), "status_options": ["Applied", "Assessment", "Interview", "Offer", "Rejected", "On Hold"], "today": timezone.localdate().isoformat()})


@login_required(login_url="login")
def my_applications_view(request):
    applications = JobApplication.objects.filter(user=request.user).select_related("resume").order_by("-application_date", "-id")
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    source = request.GET.get("source", "").strip()
    if search:
        from django.db.models import Q
        applications = applications.filter(Q(company_name__icontains=search) | Q(job_title__icontains=search))
    if status:
        applications = applications.filter(application_status__iexact=status)
    if source:
        applications = applications.filter(application_source__icontains=source)
    return render(request, "accounts/my_applications.html", {
        "applications": applications, "search": search, "status": status, "source": source,
        "status_options": ["Applied", "Assessment", "Interview", "Offer", "Rejected", "On Hold"],
    })


@login_required(login_url="login")
def edit_application_view(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, user=request.user)
    if request.method == "POST":
        for field in ("company_name", "job_title", "location", "application_source", "salary", "required_skills", "application_status", "interview_notes"):
            value = request.POST.get(field)
            if value is not None:
                setattr(application, field, value.strip())
        if request.POST.get("application_date"):
            application.application_date = request.POST["application_date"]
        application.follow_up_date = request.POST.get("follow_up_date") or None
        resume_id = request.POST.get("resume") or None
        application.resume = Resume.objects.filter(user=request.user, id=resume_id).first()
        application.save()
        messages.success(request, "Application updated successfully.")
        return redirect("my_applications")
    return render(request, "accounts/edit_application.html", {"form_title": "Edit application", "application": application, "resumes": Resume.objects.filter(user=request.user), "status_options": ["Applied", "Assessment", "Interview", "Offer", "Rejected", "On Hold"], "today": timezone.localdate().isoformat()})


@login_required(login_url="login")
def delete_application_view(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, user=request.user)
    if request.method == "POST":
        application.delete()
        messages.success(request, "Application deleted successfully.")
    else:
        messages.warning(request, "Please use the delete button to confirm deletion.")
    return redirect("my_applications")


@login_required(login_url="login")
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def pandas_analysis_view(request):
    """Build user-scoped summaries for the existing Analytics page."""
    rows = list(JobApplication.objects.filter(user=request.user).values(
        "company_name", "job_title", "application_source", "application_status",
        "required_skills", "application_date"
    ))
    df = pd.DataFrame(rows)
    total = len(df)

    if total:
        df["company_name"] = df["company_name"].fillna("Unknown company").astype(str).str.strip().replace("", "Unknown company")
        df["application_status"] = df["application_status"].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
        df["application_source"] = df["application_source"].fillna("Other").astype(str).str.strip().replace("", "Other")
        df["application_date"] = pd.to_datetime(df["application_date"], errors="coerce")

        company_summary = df.groupby("company_name").size().reset_index(name="count").sort_values(["count", "company_name"], ascending=[False, True]).to_dict("records")
        status_summary = df.groupby("application_status").size().reset_index(name="count").sort_values("count", ascending=False).to_dict("records")
        source_summary = df.groupby("application_source").size().reset_index(name="count").sort_values(["count", "application_source"], ascending=[False, True]).to_dict("records")

        normalized = df["application_status"].str.lower().str.strip()
        interviews = int((normalized == "interview").sum())
        offers = int(normalized.isin(["offer", "selected", "hired"]).sum())
        rejections = int(normalized.isin(["rejected", "reject"]).sum())
        applied = int(normalized.isin(["applied", "application submitted"]).sum())
        assessments = int(normalized.isin(["assessment", "test", "online assessment"]).sum())
        on_hold = int(normalized.isin(["on hold", "pending", "awaiting response"]).sum())

        monthly_df = df.dropna(subset=["application_date"]).copy()
        if not monthly_df.empty:
            monthly_df["month"] = monthly_df["application_date"].dt.to_period("M").astype(str)
            monthly_summary = monthly_df.groupby("month").size().reset_index(name="count").sort_values("month").to_dict("records")
        else:
            monthly_summary = []

        skill_counts = Counter()
        for raw_skills in df["required_skills"].fillna(""):
            for skill in re.split(r"[,;\n|/]", str(raw_skills)):
                skill = re.sub(r"\s+", " ", skill).strip(" .:-")
                if skill:
                    skill_counts[skill] += 1
        # Merge case-only duplicates (e.g. python/Python) while preserving a readable label.
        merged_skills = {}
        for skill, count in skill_counts.items():
            key = skill.casefold()
            if key in merged_skills:
                merged_skills[key]["count"] += count
            else:
                merged_skills[key] = {"skill": skill, "count": count}
        skill_summary = sorted(merged_skills.values(), key=lambda item: (-item["count"], item["skill"].casefold()))[:10]

        source_performance = []
        for source, source_df in df.groupby("application_source"):
            statuses = source_df["application_status"].str.lower().str.strip()
            source_performance.append({
                "application_source": source,
                "interviews": int((statuses == "interview").sum()),
                "offers": int(statuses.isin(["offer", "selected", "hired"]).sum()),
                "rejections": int(statuses.isin(["rejected", "reject"]).sum()),
            })
        source_performance.sort(key=lambda item: item["application_source"].casefold())
    else:
        company_summary, status_summary, source_summary = [], [], []
        monthly_summary, skill_summary, source_performance = [], [], []
        interviews = offers = rejections = applied = assessments = on_hold = 0

    rate = lambda n: round(n / total * 100, 1) if total else 0
    chart_data = {
        "status": {"labels": [item["application_status"] for item in status_summary], "values": [int(item["count"]) for item in status_summary]},
        "company": {"labels": [item["company_name"] for item in company_summary[:10]], "values": [int(item["count"]) for item in company_summary[:10]]},
        "source": {"labels": [item["application_source"] for item in source_summary], "values": [int(item["count"]) for item in source_summary]},
        "monthly": {"labels": [item["month"] for item in monthly_summary], "values": [int(item["count"]) for item in monthly_summary]},
        "skills": {"labels": [item["skill"] for item in skill_summary], "values": [int(item["count"]) for item in skill_summary]},
        "source_performance": {
            "labels": [item["application_source"] for item in source_performance],
            "interviews": [item["interviews"] for item in source_performance],
            "offers": [item["offers"] for item in source_performance],
            "rejections": [item["rejections"] for item in source_performance],
        },
    }
    return render(request, "accounts/analytics.html", {
        "company_summary": company_summary, "status_summary": status_summary,
        "source_summary": source_summary, "monthly_summary": monthly_summary,
        "skill_summary": skill_summary, "source_performance": source_performance,
        "chart_data": chart_data, "total_applications": total,
        "interviews": interviews, "offers": offers, "rejections": rejections,
        "applied": applied, "assessments": assessments, "on_hold": on_hold,
        "interview_rate": rate(interviews), "offer_rate": rate(offers),
        "rejection_rate": rate(rejections), "success_rate": rate(interviews + offers),
    })


@login_required(login_url="login")
def resume_library_view(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        target_role = request.POST.get("target_role", "").strip()
        notes = request.POST.get("notes", "").strip()
        uploaded = request.FILES.get("file")
        if not title or not uploaded:
            messages.error(request, "Please enter a resume name and choose a file.")
        elif uploaded.size > 5 * 1024 * 1024:
            messages.error(request, "Resume file must be 5 MB or smaller.")
        elif uploaded.name.rsplit(".", 1)[-1].lower() not in {"pdf", "doc", "docx"}:
            messages.error(request, "Only PDF, DOC, and DOCX files are allowed.")
        else:
            Resume.objects.create(user=request.user, title=title, target_role=target_role, notes=notes, file=uploaded)
            messages.success(request, "Resume uploaded successfully. You can now attach it to applications.")
            return redirect("resume_library")
    resumes = Resume.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "accounts/resume_library.html", {"resumes": resumes})


@login_required(login_url="login")
def delete_resume_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if request.method == "POST":
        # Existing applications keep their records; their resume reference becomes empty.
        resume.delete()
        messages.success(request, "Resume removed from your library.")
    return redirect("resume_library")


DEFAULT_SKILLS = ["Python", "SQL", "Excel", "Power BI", "Tableau", "Pandas", "NumPy", "Machine Learning", "Statistics", "AWS", "Azure", "Django", "Communication"]


@login_required(login_url="login")
def skill_gap_view(request):
    saved = request.session.get("jobtrack_skills", [])
    if request.method == "POST":
        raw = request.POST.get("skills", "")
        saved = sorted({s.strip() for s in re.split(r"[,\n;]", raw) if s.strip()}, key=str.lower)
        request.session["jobtrack_skills"] = saved
        messages.success(request, "Your skills have been saved for this account on this browser.")
    apps = JobApplication.objects.filter(user=request.user)
    skill_counts = Counter()
    for app in apps:
        for skill in re.split(r"[,;\n|]", app.required_skills or ""):
            skill = skill.strip()
            if skill:
                skill_counts[skill.lower()] += 1
    # Keep a readable version of skill names from stored postings.
    required = sorted(skill_counts.items(), key=lambda item: (-item[1], item[0]))
    user_lower = {s.lower() for s in saved}
    rows = [{"name": name.title() if name.isupper() else name, "count": count,
             "have": any(name.lower() == s or name.lower() in s or s in name.lower() for s in user_lower)}
            for name, count in required]
    gaps = [r for r in rows if not r["have"]]
    return render(request, "accounts/skill_gap.html", {
        "skills_text": ", ".join(saved), "skill_rows": rows, "skill_gaps": gaps,
        "saved_skills": saved, "suggested_skills": DEFAULT_SKILLS,
        "application_count": apps.count(),
    })


@login_required(login_url="login")
def export_applications_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="jobtrack_applications.csv"'
    writer = csv.writer(response)
    writer.writerow(["Company", "Job Title", "Location", "Source", "Salary", "Required Skills", "Status", "Application Date", "Resume Used", "Follow-up Date", "Interview Notes"])
    for app in JobApplication.objects.filter(user=request.user).select_related("resume").order_by("-application_date"):
        writer.writerow([app.company_name, app.job_title, app.location, app.application_source, app.salary, app.required_skills, app.application_status, app.application_date, app.resume.title if app.resume else "", app.follow_up_date or "", app.interview_notes])
    return response
