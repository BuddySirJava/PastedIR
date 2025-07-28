# urls.py
from django.conf.urls import handler404
from django.urls import path
from .views import home, create_paste, view_encrypted_paste, view_raw_paste, history, err404, about

urlpatterns = [
    path('', home, name='home'),
    path('create/', create_paste, name='create_paste'),
    path('history/', history, name='history'),
    path('about/',about , name='about'),

    path('<str:paste_id>/raw/', view_raw_paste, name='view_raw_paste'),
    path('<str:paste_id>/', view_encrypted_paste, name='view_encrypted_paste'),

]
handler404 = err404

