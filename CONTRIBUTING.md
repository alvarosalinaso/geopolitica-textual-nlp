# Contribuir

## Configuración del entorno

```bash
pip install -r requirements.txt
pip install pytest ruff
```

## Ejecutar tests

```bash
pytest tests/ -v
```

## Código

- Seguir PEP 8
- Usar `ruff check .` y `ruff format .`
- Type hints donde sea posible

## Commits

Usar convención de commits:
- `feat`: nueva funcionalidad
- `fix`: corrección de bug
- `docs`: documentación
- `refactor`: refactoring
- `test`: tests

## Pull Requests

1. Crear branch desde main
2. Hacer cambios
3. Ejecutar tests
4. Crear PR con descripción clara