from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario, Animal, Intervencion


class RegistroVeterinarioForm(UserCreationForm):
    numero_colegiado = forms.CharField(max_length=50)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'numero_colegiado', 'password1', 'password2']


class RegistroDuenoForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']


class IntervencionForm(forms.ModelForm):
    class Meta:
        model = Intervencion
        fields = [
            'nombre',
            'descripcion',
            'tratamiento',
            'animales',
            'nivel_riesgo',
            'fecha_programada',
            'fecha_fin_recuperacion',
            'completada',
        ]

        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 5}),
            'fecha_programada': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_recuperacion': forms.DateInput(attrs={'type': 'date'}),
            'animales': forms.SelectMultiple(),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if nombre:
            repetidas = Intervencion.objects.filter(nombre__iexact=nombre)

            if self.instance.pk:
                repetidas = repetidas.exclude(pk=self.instance.pk)

            if repetidas.exists():
                raise forms.ValidationError('Ya existe una intervención con ese nombre.')

        return nombre

    def clean_nivel_riesgo(self):
        nivel_riesgo = self.cleaned_data.get('nivel_riesgo')

        if nivel_riesgo is not None and (nivel_riesgo < 0 or nivel_riesgo > 10):
            raise forms.ValidationError('El nivel de riesgo debe estar entre 0 y 10.')

        return nivel_riesgo

    def clean(self):
        cleaned_data = super().clean()

        descripcion = cleaned_data.get('descripcion')
        tratamiento = cleaned_data.get('tratamiento')
        animales = cleaned_data.get('animales')
        fecha_programada = cleaned_data.get('fecha_programada')
        fecha_fin_recuperacion = cleaned_data.get('fecha_fin_recuperacion')

        if descripcion and len(descripcion) < 100:
            self.add_error('descripcion', 'La descripción debe tener al menos 100 caracteres.')

        if tratamiento and not tratamiento.apto_para_intervenciones:
            self.add_error('tratamiento', 'El tratamiento seleccionado no es apto para intervenciones.')

        if animales:
            for animal in animales:
                edad_en_dias = (date.today() - animal.fecha_nacimiento).days
                if edad_en_dias < 180:
                    self.add_error('animales', f'El animal {animal} tiene menos de 6 meses.')

        if fecha_programada and fecha_fin_recuperacion:
            if fecha_programada >= fecha_fin_recuperacion:
                self.add_error(
                    'fecha_programada',
                    'La fecha programada debe ser anterior a la fecha fin de recuperación.'
                )

        if not self.instance.pk:
            if fecha_fin_recuperacion and fecha_fin_recuperacion < date.today():
                self.add_error(
                    'fecha_fin_recuperacion',
                    'La fecha fin de recuperación debe ser igual o posterior a hoy.'
                )

        return cleaned_data


class BusquedaIntervencionForm(forms.Form):
    texto = forms.CharField(required=False)

    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    nivel_mayor = forms.IntegerField(required=False)

    animales = forms.ModelMultipleChoiceField(
        queryset=Animal.objects.none(),
        required=False,
        widget=forms.SelectMultiple()
    )

    no_completadas = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        if usuario and usuario.is_authenticated:
            if usuario.rol == Usuario.DUENO:
                self.fields['animales'].queryset = Animal.objects.filter(
                    dueno__usuario=usuario
                )
            elif usuario.rol == Usuario.VETERINARIO:
                self.fields['animales'].queryset = Animal.objects.filter(
                    intervenciones__veterinario_responsable__usuario=usuario
                ).distinct()
            else:
                self.fields['animales'].queryset = Animal.objects.none()

    def clean_texto(self):
        texto = self.cleaned_data.get('texto')

        if texto and len(texto) < 3:
            raise forms.ValidationError('El texto de búsqueda debe tener al menos 3 caracteres.')

        return texto

    def clean_nivel_mayor(self):
        nivel_mayor = self.cleaned_data.get('nivel_mayor')

        if nivel_mayor is not None and (nivel_mayor < 0 or nivel_mayor > 10):
            raise forms.ValidationError('El nivel debe estar entre 0 y 10.')

        return nivel_mayor

    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')

        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            self.add_error('fecha_hasta', 'La fecha hasta debe ser posterior a la fecha desde.')

        return cleaned_data
