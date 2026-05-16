# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    VETERINARIO = 1
    DUENO = 2

    ROLES = (
        (VETERINARIO, 'Veterinario'),
        (DUENO, 'Dueño'),
    )

    rol = models.PositiveSmallIntegerField(choices=ROLES, null=True, blank=True)


class Veterinario(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='veterinario'
    )
    numero_colegiado = models.CharField(max_length=50)

    def __str__(self):
        return self.usuario.username


class Dueno(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='dueno'
    )

    def __str__(self):
        return self.usuario.username


class Animal(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    dueno = models.ForeignKey(Dueno, on_delete=models.CASCADE, related_name='animales')

    def __str__(self):
        return self.nombre


class Tratamiento(models.Model):
    nombre = models.CharField(max_length=100)
    apto_para_intervenciones = models.BooleanField()

    def __str__(self):
        return self.nombre


class Intervencion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    animales = models.ManyToManyField(Animal, related_name='intervenciones')
    nivel_riesgo = models.IntegerField()
    fecha_programada = models.DateField()
    fecha_fin_recuperacion = models.DateField()
    completada = models.BooleanField(default=False)
    veterinario_responsable = models.ForeignKey(Veterinario, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
