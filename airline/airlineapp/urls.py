from django.urls import path, include
from . import views



app_name = 'airlineapp'
urlpatterns = [
    path('api/findflight/', views.findflight),
    path('api/bookflight/', views.bookflight),

    path('api/payforbooking/', views.payforbooking),

    path('api/confirm/', views.confirm),

    path('api/cancelbooking/', views.cancelbooking),
]
