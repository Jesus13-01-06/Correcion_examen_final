from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import RegistroVeterinarioForm, RegistroDuenoForm, IntervencionForm, BusquedaIntervencionForm
from .models import Usuario, Veterinario, Dueno, Animal, Intervencion
from .utils import crear_grupos_y_permisos


def registro_veterinario(request):
    if request.method == 'POST':
        formulario = RegistroVeterinarioForm(request.POST)

        if formulario.is_valid():
            usuario = formulario.save()
            usuario.rol = Usuario.VETERINARIO
            usuario.save()

            Veterinario.objects.create(
                usuario=usuario,
                numero_colegiado=formulario.cleaned_data['numero_colegiado']
            )

            crear_grupos_y_permisos()
            grupo = Group.objects.get(name='Veterinarios')
            usuario.groups.add(grupo)

            return redirect('login')
    else:
        formulario = RegistroVeterinarioForm()

    return render(request, 'veterinaria/registro.html', {
        'formulario': formulario,
        'titulo': 'Registro de veterinario',
        'tipo_registro': 'veterinario',
    })


def registro_dueno(request):
    if request.method == 'POST':
        formulario = RegistroDuenoForm(request.POST)

        if formulario.is_valid():
            usuario = formulario.save()
            usuario.rol = Usuario.DUENO
            usuario.save()

            Dueno.objects.create(usuario=usuario)

            crear_grupos_y_permisos()
            grupo = Group.objects.get(name='Dueños')
            usuario.groups.add(grupo)

            return redirect('login')
    else:
        formulario = RegistroDuenoForm()

    return render(request, 'veterinaria/registro.html', {
        'formulario': formulario,
        'titulo': 'Registro de dueño',
        'tipo_registro': 'dueno',
    })


@login_required
def lista_intervenciones(request):
    intervenciones = Intervencion.objects.select_related(
        'tratamiento',
        'veterinario_responsable',
        'veterinario_responsable__usuario'
    ).prefetch_related(
        'animales',
        'animales__dueno',
        'animales__dueno__usuario'
    )

    if request.user.rol == Usuario.VETERINARIO:
        veterinario = Veterinario.objects.filter(usuario=request.user).first()
        intervenciones = intervenciones.filter(veterinario_responsable=veterinario)

    elif request.user.rol == Usuario.DUENO:
        dueno = Dueno.objects.filter(usuario=request.user).first()
        intervenciones = intervenciones.filter(animales__dueno=dueno)

    else:
        intervenciones = Intervencion.objects.none()

    return render(request, 'veterinaria/lista_intervenciones.html', {
        'intervenciones': intervenciones.distinct()
    })


@login_required
def mis_animales(request):
    dueno = Dueno.objects.filter(usuario=request.user).first()

    if dueno is None:
        return redirect('lista_intervenciones')

    animales = Animal.objects.filter(dueno=dueno)

    return render(request, 'veterinaria/mis_animales.html', {
        'animales': animales
    })


@login_required
@permission_required('veterinaria.add_intervencion', login_url='login')
def crear_intervencion(request):
    veterinario = Veterinario.objects.filter(usuario=request.user).first()

    if veterinario is None:
        return redirect('lista_intervenciones')

    if request.method == 'POST':
        formulario = IntervencionForm(request.POST)

        if formulario.is_valid():
            intervencion = Intervencion.objects.create(
                nombre=formulario.cleaned_data['nombre'],
                descripcion=formulario.cleaned_data['descripcion'],
                tratamiento=formulario.cleaned_data['tratamiento'],
                nivel_riesgo=formulario.cleaned_data['nivel_riesgo'],
                fecha_programada=formulario.cleaned_data['fecha_programada'],
                fecha_fin_recuperacion=formulario.cleaned_data['fecha_fin_recuperacion'],
                completada=formulario.cleaned_data['completada'],
                veterinario_responsable=veterinario,
            )
            intervencion.animales.set(formulario.cleaned_data['animales'])
            return redirect('lista_intervenciones')
    else:
        formulario = IntervencionForm()

    return render(request, 'veterinaria/intervencion_form.html', {
        'formulario': formulario,
        'titulo': 'Crear intervención',
    })


@login_required
def busqueda_avanzada(request):
    intervenciones = Intervencion.objects.select_related(
        'tratamiento',
        'veterinario_responsable',
        'veterinario_responsable__usuario'
    ).prefetch_related('animales')

    if request.user.rol == Usuario.VETERINARIO:
        veterinario = Veterinario.objects.filter(usuario=request.user).first()
        intervenciones = intervenciones.filter(veterinario_responsable=veterinario)

    elif request.user.rol == Usuario.DUENO:
        dueno = Dueno.objects.filter(usuario=request.user).first()
        intervenciones = intervenciones.filter(animales__dueno=dueno)

    else:
        intervenciones = Intervencion.objects.none()

    formulario = BusquedaIntervencionForm(request.GET or None, usuario=request.user)

    if formulario.is_valid():
        texto = formulario.cleaned_data.get('texto')
        fecha_desde = formulario.cleaned_data.get('fecha_desde')
        fecha_hasta = formulario.cleaned_data.get('fecha_hasta')
        nivel_mayor = formulario.cleaned_data.get('nivel_mayor')
        animales = formulario.cleaned_data.get('animales')
        no_completadas = formulario.cleaned_data.get('no_completadas')

        if texto:
            intervenciones = intervenciones.filter(
                Q(nombre__icontains=texto) | Q(descripcion__icontains=texto)
            )

        if fecha_desde:
            intervenciones = intervenciones.filter(fecha_programada__gte=fecha_desde)

        if fecha_hasta:
            intervenciones = intervenciones.filter(fecha_programada__lte=fecha_hasta)

        if nivel_mayor is not None:
            intervenciones = intervenciones.filter(nivel_riesgo__gt=nivel_mayor)

        if animales:
            animales = animales.all()
            intervenciones = intervenciones.filter(animales__in=animales)

        if no_completadas:
            intervenciones = intervenciones.filter(completada=False)

    return render(request, 'veterinaria/busqueda_avanzada.html', {
        'formulario': formulario,
        'intervenciones': intervenciones.distinct()
    })


@login_required
@permission_required('veterinaria.change_intervencion', login_url='login')
def editar_intervencion(request, intervencion_id):
    intervencion = Intervencion.objects.filter(id=intervencion_id).first()

    if intervencion is None:
        return redirect('lista_intervenciones')

    if intervencion.veterinario_responsable.usuario != request.user:
        return redirect('lista_intervenciones')

    if request.method == 'POST':
        formulario = IntervencionForm(
            request.POST,
            instance=intervencion,
        )

        if formulario.is_valid():
            formulario.save()
            return redirect('lista_intervenciones')
    else:
        formulario = IntervencionForm(
            instance=intervencion,
        )

    return render(request, 'veterinaria/intervencion_form.html', {
        'formulario': formulario,
        'titulo': 'Editar intervención',
        'intervencion': intervencion,
    })


@login_required
@permission_required('veterinaria.delete_intervencion', login_url='login')
def eliminar_intervencion(request, intervencion_id):
    intervencion = Intervencion.objects.filter(id=intervencion_id).first()

    if intervencion is None:
        return redirect('lista_intervenciones')

    if intervencion.veterinario_responsable.usuario != request.user:
        return redirect('lista_intervenciones')

    if request.method == 'POST':
        intervencion.delete()
        return redirect('lista_intervenciones')

    return render(request, 'veterinaria/confirmar_eliminar.html', {
        'intervencion': intervencion,
    })
