from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_World_view, name='home'),
    path('submit/', views.htmlView, name='submit'),
    path('post_example/', views.postExample, name='post_example'),
    path('submit_django_form/', views.submit_django_form, name='submit_django_form'),
    path("templating/", views.template_view, name="template"),
]