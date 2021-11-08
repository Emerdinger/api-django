from django.urls import path
from . import views

urlpatterns=[
    path('recomendar/', views.recomendarApi),
    path('recomendar/<str:title>', views.recomendarApi),
    path('recohistorial/<str:historial>', views.recomendarHistorialApi)
]