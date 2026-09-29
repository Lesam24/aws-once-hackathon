# data/

Datasets del proyecto (docs/ARCHITECTURE.md §10). Estructura versionada:

```text
data/
├── raw/          # imágenes originales sin anotar (ignorado por git)
├── annotations/  # etiquetas por imagen
└── curated/vN/   # datasets curados y versionados para entrenamiento (ignorado por git)
```

Reglas:

- Las imágenes muy similares de un mismo tablero **no** deben repartirse entre train y test
  (evitar inflar métricas artificialmente).
- Los datos de feedback de usuarios pasan por **curación** antes de entrar en `curated/`.
- El consentimiento y los controles de acceso deben respetarse antes de publicar datos.
