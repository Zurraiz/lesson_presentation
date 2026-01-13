from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.list_templates, name='list_templates'),
    path('generate/outline/', views.generate_outline, name='generate_outline'),
    path('generate/slide/', views.generate_slide_content, name='generate_slide'),
    path('search/images/', views.search_images, name='search_images'),
    path('build/', views.build_presentation, name='build_presentation'),
]
