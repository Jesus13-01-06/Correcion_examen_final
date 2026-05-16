# Correcion_examen_final

# Examen Django - CRUD y sesiones

## Instalación

python3 -m venv myvenv
source myvenv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python -X utf8 manage.py loaddata veterinaria/fixtures/datos.json
python manage.py runserver


## Usuarios de prueba
Investigador
Usuario: veterinario1
Contraseña: 1234
Pacientes
Usuario: dueno1
Contraseña: 1234

## URLs principales
/login/
/logout/
/registro/veterinario/
/registro/dueno/
/intervenciones/crear/
/intervenciones/busqueda/
/
## Funcionalidades
Registro de veterinario
Registro de dueños
Login y logout
CRUD de ensayos clínicos
Validaciones en servidor
Búsqueda avanzada
Restricción por usuario logueado
Fixtures con grupos, permisos y datos de prueba
Debugger configurado con .vscode/launch.json 
