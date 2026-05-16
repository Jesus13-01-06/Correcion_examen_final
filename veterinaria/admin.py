# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Veterinario, Animal, Tratamiento, Intervencion


class UsuarioAdmin(UserAdmin):
  fieldsets = UserAdmin.fieldsets + (
      ('Rol de la aplicación', {'fields': ('rol',)}),
  )

  add_fieldsets = UserAdmin.add_fieldsets + (
      ('Rol de la aplicación', {'fields': ('rol',)}),
  )


@admin.register(Intervencion)
class Intervencion(admin.ModelAdmin):
  list_display = (
      'nombre',
      'tratamiento',
      'nivel_riesgo',
      'fecha_programada',
      'fecha_fin_recuperacion',
      'completada',
      'veterinario_responsable',
  )
  filter_horizontal = ('animales',)


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Veterinario)
admin.site.register(Animal)
admin.site.register(Tratamiento)
