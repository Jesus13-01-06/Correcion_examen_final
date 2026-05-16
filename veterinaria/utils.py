from django.contrib.auth.models import Group, Permission


def crear_grupos_y_permisos():
    grupo_duenos, creado = Group.objects.get_or_create(name='Dueños')
    grupo_veterinarios, creado = Group.objects.get_or_create(name='Veterinarios')

    permisos_dueno = Permission.objects.filter(
        content_type__app_label='veterinaria',
        codename__in=[
            'view_intervencion',
            'view_animal',
            'view_tratamiento',
        ]
    )

    grupo_duenos.permissions.set(permisos_dueno)

    permisos_veterinario = Permission.objects.filter(
        content_type__app_label='veterinaria',
        codename__in=[
            'add_intervencion',
            'view_intervencion',
            'change_intervencion',
            'delete_intervencion',
            'view_animal',
            'view_tratamiento',
        ]
    )

    grupo_veterinarios.permissions.set(permisos_veterinario)
