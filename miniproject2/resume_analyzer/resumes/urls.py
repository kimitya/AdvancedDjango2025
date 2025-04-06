
from django.urls import path
from .views import (ResumeUploadView, ResumeDetailView, JobDescriptionCreateView,
                   JobDescriptionMatchView, JobDescriptionListView, JobDescriptionDetailView)

urlpatterns = [
    path('upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('<int:pk>/', ResumeDetailView.as_view(), name='resume-detail'),
    path('jobs/create/', JobDescriptionCreateView.as_view(), name='job-create'),
    path('jobs/<int:job_id>/matches/', JobDescriptionMatchView.as_view(), name='job-matches'),
    path('jobs/', JobDescriptionListView.as_view(), name='job-list'),  # Все вакансии
    path('jobs/<int:pk>/', JobDescriptionDetailView.as_view(), name='job-detail'),  # Вакансия по ID
]