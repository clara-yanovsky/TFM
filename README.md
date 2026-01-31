# Mundial FIFA 2026 – Preparación de Datos (TFM)

Este repositorio contiene los outputs de limpieza, preparación y generación de variables desarrollados para el Trabajo Fin de Máster (TFM), cuyo objetivo es la predicción de resultados del Mundial de la FIFA 2026.

## Alcance
El objetivo de esta etapa es entregar un conjunto de datos limpio, consistente y reproducible, apto para su posterior modelado predictivo, de conformidad con los requerimientos de la Asignatura 5: Obtención de Datos para el TFM.

## Dataset base
El proceso de preparación de datos se realizó a partir de un dataset curado de partidos internacionales de fútbol (`matches_final_curated.csv`), generado previamente durante la fase de integración de fuentes.

## Resumen metodológico
- Eliminación de duplicados mediante un identificador único de partido (`match_key`)
- Validación de reglas básicas de consistencia (equipos, fechas y marcadores)
- Tratamiento de valores faltantes y disponibilidad de ranking
- Filtro temporal a partir de 1993 (inicio del ranking FIFA moderno)
- Creación de variables derivadas mediante ventanas móviles (últimos 5 y 10 partidos)
- Prevención de fuga de información (*data leakage*) mediante el uso de cálculos con `lag`

## Estructura del repositorio


├── data/
│   ├── raw/            # Datos originales (inmutables)
│   ├── processed/      # Datos finales listos para modelado
│   └── curated/        # Resultados intermedios
├── data_to_model/      # Input modelos
├── notebooks/          # Cuadernos Jupyter para exploración (EDA)
├── src/                # Código fuente en .py (scripts de limpieza, entrenamiento)
├── models/             # Modelos entrenados, predicciones o archivos binarios
│   └── output/         # Archivos finales modelo


Se incluyen versiones en formato CSV y RDS para garantizar transparencia y reproducibilidad del proceso.

## Herramientas utilizadas
- Python: fase de obtención e integración de datos
- RStudio: limpieza, validación y generación de variables

## Reproducibilidad
Todos los datasets incluidos en este repositorio derivan de la misma fuente curada y pueden ser reproducidos siguiendo la metodología documentada.
