from django.urls import path
from .views import *

urlpatterns = [
    path('', admin_login, name='admin_login'),
    path('add-criminal/', add_criminal, name='add_criminal'),
    path('search_criminal/', search_criminal, name='search_criminal'),
    path('criminal/<int:criminal_id>/', criminal_detail, name='criminal_detail'),
    path('dashboard/', criminal_image_search, name='dashboard'),
    path('add-image/', add_image_to_criminal, name='add_image_to_criminal'),
    path('get-searched-image/', get_searched_image, name='get_searched_image')

    ]