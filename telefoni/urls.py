from django.urls import path
from . import views

urlpatterns = [
    path('cerca/', views.cerca_telefonate, name='cerca_telefonate'),
    path('modifica/<int:id>/', views.modifica_telefonata, name='modifica_telefonata'),
    path('elimina/<int:id>/', views.elimina_telefonata, name='elimina_telefonata'),
    path('inserisci/', views.inserisci_telefonata, name='inserisci_telefonata'),
    path('contratti/', views.cerca_contratti, name='cerca_contratti'),
    path('sim/', views.cerca_sim, name='cerca_sim'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]