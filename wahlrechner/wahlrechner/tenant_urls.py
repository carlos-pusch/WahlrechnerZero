from django.urls import path

from . import views

# lz_b_1: Diese URLs werden alle unter <slug:wahl_slug>/ eingebunden,
# daher haben sie den wahl_slug nicht mehr in der eigenen Definition.
# Die Views erhalten den wahl_slug automatisch als ersten Parameter.

urlpatterns = [
    path('', views.start, name='start'),
    path('these/<int:these_pk>/<str:zustand>/', views.these, name='these'),
    path('confirm/<str:zustand>/', views.confirm, name='confirm'),
    path('confirm/<str:zustand>/submit/', views.confirm_submit, name='confirm_submit'),
    path('result/<str:zustand>/', views.result, name='result'),
    path('reason/<int:these_pk>/<str:zustand>/', views.reason, name='reason'),
]
