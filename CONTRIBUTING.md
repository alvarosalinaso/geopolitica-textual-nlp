# Contribuir

## Configuracion del entorno

`ash
pip install -r requirements.txt
pip install pytest ruff
`

## Ejecutar tests

`ash
pytest tests/ -v
`

## Codigo

- Seguir PEP 8
- Usar uff check . y uff format .
- Type hints donde sea posible

## Commits

Usar convencion de commits:
- eat: nueva funcionalidad
- ix: correccion de bug
- docs: documentacion
- efactor: refactoring
- 	est: tests

## Pull Requests

1. Crear branch desde main
2. Hacer cambios
3. Ejecutar tests
4. Crear PR con descripcion clara
