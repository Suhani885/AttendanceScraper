from django.urls import path
from . import views

urlpatterns = [
    path('scrapeAttendance/', views.scrape_attendance),
    path('getAttendance/', views.get_attendance),
]