# Aplicación de práctica de idiomas

## Estructura

```text
streamlit_language_quiz/
├── app.py
├── requirements.txt
└── data/
    ├── aleman/
    │   └── A1/
    │       └── fundamentos.json
    └── ingles/
        └── A1/
            └── basics.json
```

Puedes añadir tantos idiomas, niveles y ejercicios como necesites.

## Instalación

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Formato JSON

```json
{
  "title": "Nombre del ejercicio",
  "description": "Descripción opcional",
  "questions": [
    {
      "id": "identificador_unico",
      "type": "text",
      "prompt": "Texto de la pregunta",
      "answer": "respuesta correcta",
      "accepted_answers": ["otra forma válida"],
      "explanation": "Explicación pedagógica de la solución",
      "ignore_accents": false,
      "multiline": false,
      "help": "Pista opcional"
    }
  ]
}
```

Para selección múltiple:

```json
{
  "id": "pregunta_2",
  "type": "multiple_choice",
  "prompt": "Selecciona una opción",
  "options": ["opción 1", "opción 2", "opción 3"],
  "answer": "opción 2",
  "explanation": "Explicación de la respuesta."
}
```

## Notas

- `id` debe ser único dentro del ejercicio.
- `accepted_answers` permite aceptar variantes equivalentes.
- `ignore_accents` está desactivado por defecto.
- La comparación es exacta tras normalizar mayúsculas y espacios.
- Para redacciones libres conviene evaluar criterios concretos o integrar posteriormente un corrector lingüístico.
