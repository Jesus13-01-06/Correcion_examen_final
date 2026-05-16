from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_intervenciones, name='lista_intervenciones'),

    path('registro/veterinario/', views.registro_veterinario, name='registro_veterinario'),
    path('registro/dueno/', views.registro_dueno, name='registro_dueno'),

    path('mis-animales/', views.mis_animales, name='mis_animales'),

    path('intervenciones/crear/', views.crear_intervencion, name='crear_intervencion'),
    path('intervenciones/busqueda/', views.busqueda_avanzada, name='busqueda_avanzada'),
    path('intervenciones/<int:intervencion_id>/editar/', views.editar_intervencion, name='editar_intervencion'),
    path('intervenciones/<int:intervencion_id>/eliminar/', views.eliminar_intervencion, name='eliminar_intervencion'),
]
