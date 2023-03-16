## Activar y desactivar 

source venv/bin/activate

deactivate

pip freeze > requirements.txt

pip freeze | grep -v "^\-e" | cut -d = -f 1 > requirements.txt

pip install -r requirements.txt

pip install --no-deps -r requirements.txt --> solo las que no están preinstaladas

## Para instalar PyQt5

Primero, instalar qt5 con: brew install qt5

pip install PyQt5


