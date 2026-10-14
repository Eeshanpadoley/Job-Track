from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("add-application/", views.add_application_view, name="add_application"),
    path("analytics/", views.pandas_analysis_view, name="analytics"),
    path("skill-gap/", views.skill_gap_view, name="skill_gap"),
    path("resumes/", views.resume_library_view, name="resume_library"),
    path("resumes/<int:resume_id>/delete/", views.delete_resume_view, name="delete_resume"),
    path("export/csv/", views.export_applications_csv, name="export_csv"),
    path("my-applications/", views.my_applications_view, name="my_applications"),
    path("edit-application/<int:application_id>/", views.edit_application_view, name="edit_application"),
    path("delete-application/<int:application_id>/", views.delete_application_view, name="delete_application"),
]
