from __future__ import annotations

import io
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"

LANGUAGE_CHARACTERS = {
    "aleman": ["ä", "ö", "ü", "ß", "Ä", "Ö", "Ü"],
    "frances": [
        "à", "â", "æ", "ç", "é", "è", "ê", "ë",
        "î", "ï", "ô", "œ", "ù", "û", "ü", "ÿ",
    ],
    "espanol": ["á", "é", "í", "ó", "ú", "ü", "ñ", "¿", "¡"],
    "griego": list("αβγδεζηθικλμνξοπρστυφχψω"),
    "ruso": list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя"),
}

LANGUAGE_LABELS = {
    "aleman": "Alemán",
    "frances": "Francés",
    "espanol": "Español",
    "griego": "Griego",
    "ruso": "Ruso",
}

st.set_page_config(page_title="Práctica de idiomas", page_icon="📘", layout="wide")

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 4.5rem;
            padding-bottom: 7.5rem;
            max-width: 1100px;
        }
        .app-title {font-size: 2rem; font-weight: 750; margin-bottom: .15rem;}
        .app-subtitle {color: #666; margin-bottom: 1.5rem;}
        .question-number {
            font-size: .85rem; font-weight: 700; opacity: .7;
            letter-spacing: .03em; text-transform: uppercase;
        }
        .result-correct {
            border-left: 5px solid #2eaf62; background: rgba(46,175,98,.10);
            padding: .75rem .9rem; border-radius: 8px; margin-top: .55rem;
        }
        .result-wrong {
            border-left: 5px solid #df4747; background: rgba(223,71,71,.10);
            padding: .75rem .9rem; border-radius: 8px; margin-top: .55rem;
        }
        .result-revealed {
            border-left: 5px solid #d99a1b; background: rgba(217,154,27,.11);
            padding: .75rem .9rem; border-radius: 8px; margin-top: .55rem;
        }
        .st-key-bottom_actions {
            position: fixed; left: 0; right: 0; bottom: 0; z-index: 999;
            padding: .75rem max(1rem, calc((100vw - 1100px) / 2));
            background: var(--background-color);
            border-top: 1px solid rgba(128,128,128,.30);
            box-shadow: 0 -4px 16px rgba(0,0,0,.08);
        }
        .st-key-bottom_actions [data-testid="stHorizontalBlock"] {gap: .6rem;}
        @media (max-width: 700px) {
            .block-container {padding-top: 4rem;}
            .app-title {font-size: 1.55rem;}
            .st-key-bottom_actions {padding: .55rem .65rem;}
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def pretty_name(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip().title()


def list_directories(path: Path) -> list[Path]:
    return sorted(item for item in path.iterdir() if item.is_dir()) if path.exists() else []


def list_json_files(path: Path) -> list[Path]:
    return sorted(path.glob("*.json")) if path.exists() else []


@st.cache_data(show_spinner=False)
def load_exercise(path_string: str) -> dict[str, Any]:
    path = Path(path_string)
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if "questions" not in data or not isinstance(data["questions"], list):
        raise ValueError("El JSON debe contener una lista llamada 'questions'.")

    required = {"id", "prompt", "answer", "explanation"}
    for position, question in enumerate(data["questions"], start=1):
        missing = required.difference(question)
        if missing:
            raise ValueError(
                f"La pregunta {position} no contiene: {', '.join(sorted(missing))}"
            )
    return data


def normalize_text(value: str, ignore_accents: bool = False) -> str:
    value = re.sub(r"\s+", " ", str(value).strip().casefold())
    if ignore_accents:
        value = "".join(
            char
            for char in unicodedata.normalize("NFD", value)
            if unicodedata.category(char) != "Mn"
        )
    return value


def accepted_answers(question: dict[str, Any]) -> list[str]:
    answers = [str(question["answer"])]
    answers.extend(str(item) for item in question.get("accepted_answers", []))
    return answers


def is_correct(question: dict[str, Any], user_answer: str) -> bool:
    ignore_accents = bool(question.get("ignore_accents", False))
    normalized_user = normalize_text(user_answer, ignore_accents)
    if not normalized_user:
        return False
    return any(
        normalized_user == normalize_text(answer, ignore_accents)
        for answer in accepted_answers(question)
    )


def answer_key(question_id: str) -> str:
    return f"answer__{question_id}"


def status_key(question_id: str) -> str:
    return f"status__{question_id}"


def initialize_question_state(questions: list[dict[str, Any]]) -> None:
    for question in questions:
        qid = str(question["id"])
        st.session_state.setdefault(answer_key(qid), "")
        st.session_state.setdefault(status_key(qid), "unanswered")


def clear_question_state(questions: list[dict[str, Any]]) -> None:
    for question in questions:
        qid = str(question["id"])
        st.session_state.pop(answer_key(qid), None)
        st.session_state.pop(status_key(qid), None)


def handle_exercise_change(signature: str, questions: list[dict[str, Any]]) -> None:
    previous = st.session_state.get("exercise_signature")
    if previous != signature:
        clear_question_state(st.session_state.get("loaded_questions", []))
        st.session_state["exercise_signature"] = signature
        st.session_state["loaded_questions"] = questions
    initialize_question_state(questions)


def check_one(question: dict[str, Any]) -> None:
    qid = str(question["id"])
    answer = st.session_state.get(answer_key(qid), "")
    st.session_state[status_key(qid)] = "correct" if is_correct(question, answer) else "wrong"


def reveal_one(question: dict[str, Any]) -> None:
    qid = str(question["id"])
    st.session_state[answer_key(qid)] = str(question["answer"])
    st.session_state[status_key(qid)] = "revealed"


def check_all(questions: list[dict[str, Any]]) -> None:
    for question in questions:
        check_one(question)


def reveal_all(questions: list[dict[str, Any]]) -> None:
    for question in questions:
        reveal_one(question)


def reset_all(questions: list[dict[str, Any]]) -> None:
    for question in questions:
        qid = str(question["id"])
        st.session_state[answer_key(qid)] = ""
        st.session_state[status_key(qid)] = "unanswered"


def language_config_key(language: str) -> str:
    normalized = unicodedata.normalize("NFD", language.casefold())
    without_accents = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )
    return without_accents.replace("_", " ").replace("-", " ").strip()


def render_focus_preserving_keyboard(language: str) -> None:
    language_keys = list(LANGUAGE_CHARACTERS)
    selected_language_key = language_config_key(language)
    default_language = (
        selected_language_key if selected_language_key in language_keys else language_keys[0]
    )
    keyboard_data = {
        key: {
            "label": LANGUAGE_LABELS.get(key, pretty_name(key)),
            "characters": characters,
        }
        for key, characters in LANGUAGE_CHARACTERS.items()
    }

    components.html(
        f"""
        <script>
        (() => {{
            const doc = window.parent.document;
            const keyboardData = {json.dumps(keyboard_data, ensure_ascii=False)};
            const defaultLanguage = {json.dumps(default_language, ensure_ascii=False)};
            const rootId = "focus-preserving-character-keyboard";
            doc.getElementById(rootId)?.remove();

            const app = doc.querySelector(".stApp") || doc.body;
            const rootStyles = window.parent.getComputedStyle(doc.documentElement);
            const appStyles = window.parent.getComputedStyle(app);
            const bodyStyles = window.parent.getComputedStyle(doc.body);
            const themeValue = (name, fallback = "") =>
                appStyles.getPropertyValue(name).trim()
                || rootStyles.getPropertyValue(name).trim()
                || bodyStyles.getPropertyValue(name).trim()
                || fallback;
            const isTransparent = (color) => {{
                if (!color) return true;
                if (color === "transparent") return true;
                const match = color.match(/rgba?\\(\\s*\\d+,\\s*\\d+,\\s*\\d+(?:,\\s*([\\d.]+))?\\s*\\)/);
                return match && match[1] !== undefined && Number(match[1]) === 0;
            }};
            const fallbackBackground = isTransparent(appStyles.backgroundColor)
                ? bodyStyles.backgroundColor
                : appStyles.backgroundColor;
            const appBackground = themeValue("--background-color", fallbackBackground || "rgb(255, 255, 255)");
            const appColor = themeValue("--text-color", appStyles.color || bodyStyles.color || "rgb(49, 51, 63)");
            const isDarkTheme = (() => {{
                const match = appBackground.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                if (!match) return false;
                const red = Number(match[1]);
                const green = Number(match[2]);
                const blue = Number(match[3]);
                return ((red * 299 + green * 587 + blue * 114) / 1000) < 128;
            }})();
            const panelBackground = themeValue(
                "--secondary-background-color",
                isDarkTheme ? "rgb(38, 39, 48)" : "rgb(255, 255, 255)",
            );
            const softBackground = isDarkTheme ? "rgba(255,255,255,.06)" : "rgba(49,51,63,.04)";
            const hoverBackground = isDarkTheme ? "rgba(255,255,255,.12)" : "rgba(49,51,63,.08)";
            const borderColor = isDarkTheme ? "rgba(250,250,250,.22)" : "rgba(49,51,63,.20)";
            const mutedColor = isDarkTheme ? "rgba(250,250,250,.68)" : "rgba(49,51,63,.68)";
            const shadowColor = isDarkTheme ? "rgba(0,0,0,.45)" : "rgba(0,0,0,.16)";
            const primaryColor = themeValue("--primary-color", "rgb(255, 75, 75)");

            let activeField = null;
            let selectedLanguage = defaultLanguage;
            const root = doc.createElement("div");
            root.id = rootId;
            root.style.setProperty("--fpck-bg", panelBackground);
            root.style.setProperty("--fpck-soft-bg", softBackground);
            root.style.setProperty("--fpck-hover-bg", hoverBackground);
            root.style.setProperty("--fpck-text", appColor);
            root.style.setProperty("--fpck-muted", mutedColor);
            root.style.setProperty("--fpck-border", borderColor);
            root.style.setProperty("--fpck-shadow", shadowColor);
            root.style.setProperty("--fpck-primary", primaryColor);
            root.innerHTML = `
                <button class="fpck-toggle" type="button">Caracteres especiales</button>
                <section class="fpck-panel" hidden>
                    <div class="fpck-header">
                        <strong>Caracteres especiales</strong>
                        <button class="fpck-close" type="button" aria-label="Cerrar">×</button>
                    </div>
                    <label class="fpck-label">
                        Idioma
                        <select class="fpck-language"></select>
                    </label>
                    <div class="fpck-status">Selecciona un campo de respuesta.</div>
                    <div class="fpck-grid"></div>
                    <div class="fpck-controls">
                        <button type="button" data-control="space">Espacio</button>
                        <button type="button" data-control="backspace">⌫</button>
                        <button type="button" data-control="clear">Limpiar</button>
                    </div>
                </section>
            `;

            const style = doc.createElement("style");
            style.textContent = `
                #${{rootId}} {{
                    position: fixed;
                    right: 1rem;
                    top: 5.2rem;
                    z-index: 100000;
                    width: min(340px, calc(100vw - 2rem));
                    font-family: "Source Sans Pro", sans-serif;
                    color: var(--fpck-text);
                }}
                #${{rootId}} .fpck-toggle,
                #${{rootId}} button,
                #${{rootId}} select {{
                    font: inherit;
                }}
                #${{rootId}} .fpck-toggle {{
                    float: right;
                    width: 210px;
                    border: 1px solid var(--fpck-border);
                    border-radius: 8px;
                    padding: .5rem .65rem;
                    background: var(--fpck-bg);
                    color: var(--fpck-text);
                    box-shadow: 0 8px 24px var(--fpck-shadow);
                    cursor: pointer;
                }}
                #${{rootId}} .fpck-toggle:hover,
                #${{rootId}} .fpck-close:hover,
                #${{rootId}} .fpck-grid button:hover,
                #${{rootId}} .fpck-controls button:hover {{
                    background: var(--fpck-hover-bg);
                    border-color: var(--fpck-primary);
                }}
                #${{rootId}} .fpck-toggle:focus-visible,
                #${{rootId}} button:focus-visible,
                #${{rootId}} select:focus-visible {{
                    outline: 2px solid var(--fpck-primary);
                    outline-offset: 2px;
                }}
                #${{rootId}} .fpck-panel {{
                    clear: both;
                    padding: .85rem;
                    max-height: calc(100vh - 7rem);
                    overflow-y: auto;
                    background: var(--fpck-bg);
                    color: var(--fpck-text);
                    border: 1px solid var(--fpck-border);
                    border-radius: 8px;
                    box-shadow: 0 12px 32px var(--fpck-shadow);
                }}
                #${{rootId}} .fpck-header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: .75rem;
                    margin-bottom: .65rem;
                }}
                #${{rootId}} .fpck-close {{
                    width: 2rem;
                    height: 2rem;
                    border: 1px solid var(--fpck-border);
                    border-radius: 6px;
                    background: var(--fpck-soft-bg);
                    color: var(--fpck-text);
                    cursor: pointer;
                }}
                #${{rootId}} .fpck-label {{
                    display: grid;
                    gap: .3rem;
                    margin-bottom: .65rem;
                    font-size: .9rem;
                }}
                #${{rootId}} select {{
                    width: 100%;
                    border: 1px solid var(--fpck-border);
                    border-radius: 6px;
                    padding: .45rem;
                    background: var(--fpck-bg);
                    color: var(--fpck-text);
                }}
                #${{rootId}} .fpck-status {{
                    margin-bottom: .65rem;
                    color: var(--fpck-muted);
                    font-size: .85rem;
                }}
                #${{rootId}} .fpck-grid {{
                    display: grid;
                    grid-template-columns: repeat(7, minmax(0, 1fr));
                    gap: .35rem;
                    margin-bottom: .65rem;
                }}
                #${{rootId}} .fpck-grid button,
                #${{rootId}} .fpck-controls button {{
                    min-height: 2rem;
                    border: 1px solid var(--fpck-border);
                    border-radius: 6px;
                    background: var(--fpck-soft-bg);
                    color: var(--fpck-text);
                    cursor: pointer;
                }}
                #${{rootId}} .fpck-controls {{
                    display: grid;
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                    gap: .35rem;
                }}
                @media (max-width: 700px) {{
                    #${{rootId}} {{
                        right: .65rem;
                        top: 4.5rem;
                        width: min(320px, calc(100vw - 1.3rem));
                    }}
                }}
            `;
            root.appendChild(style);
            doc.body.appendChild(root);

            const toggle = root.querySelector(".fpck-toggle");
            const panel = root.querySelector(".fpck-panel");
            const close = root.querySelector(".fpck-close");
            const languageSelect = root.querySelector(".fpck-language");
            const grid = root.querySelector(".fpck-grid");
            const status = root.querySelector(".fpck-status");

            Object.entries(keyboardData).forEach(([key, value]) => {{
                const option = doc.createElement("option");
                option.value = key;
                option.textContent = value.label;
                option.selected = key === selectedLanguage;
                languageSelect.appendChild(option);
            }});

            function isEditableAnswerField(element) {{
                if (!element) return false;
                const tagName = element.tagName;
                const isTextInput = tagName === "INPUT" && ["text", "search"].includes(element.type);
                return tagName === "TEXTAREA" || isTextInput;
            }}

            function updateStatus() {{
                status.textContent = activeField
                    ? "Insertando en la respuesta seleccionada."
                    : "Selecciona un campo de respuesta.";
            }}

            function setNativeValue(element, value) {{
                const valueSetter = Object.getOwnPropertyDescriptor(element, "value")?.set;
                const prototype = Object.getPrototypeOf(element);
                const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, "value")?.set;

                if (prototypeValueSetter && valueSetter !== prototypeValueSetter) {{
                    prototypeValueSetter.call(element, value);
                }} else if (valueSetter) {{
                    valueSetter.call(element, value);
                }} else {{
                    element.value = value;
                }}

                element.dispatchEvent(new InputEvent("input", {{ bubbles: true, inputType: "insertText", data: null }}));
                element.dispatchEvent(new Event("change", {{ bubbles: true }}));
            }}

            function mutateActiveField(operation) {{
                if (!activeField || !doc.body.contains(activeField)) {{
                    updateStatus();
                    return;
                }}

                const start = activeField.selectionStart ?? activeField.value.length;
                const end = activeField.selectionEnd ?? activeField.value.length;
                const value = activeField.value;
                let nextValue = value;
                let nextCursor = start;

                if (operation.type === "insert") {{
                    nextValue = value.slice(0, start) + operation.value + value.slice(end);
                    nextCursor = start + operation.value.length;
                }} else if (operation.type === "backspace") {{
                    if (start !== end) {{
                        nextValue = value.slice(0, start) + value.slice(end);
                        nextCursor = start;
                    }} else if (start > 0) {{
                        nextValue = value.slice(0, start - 1) + value.slice(end);
                        nextCursor = start - 1;
                    }}
                }} else if (operation.type === "clear") {{
                    nextValue = "";
                    nextCursor = 0;
                }}

                setNativeValue(activeField, nextValue);
                activeField.focus({{ preventScroll: true }});
                activeField.setSelectionRange(nextCursor, nextCursor);
                updateStatus();
            }}

            function renderCharacters() {{
                grid.replaceChildren();
                keyboardData[selectedLanguage].characters.forEach((character) => {{
                    const button = doc.createElement("button");
                    button.type = "button";
                    button.textContent = character;
                    button.addEventListener("mousedown", (event) => event.preventDefault());
                    button.addEventListener("click", () => mutateActiveField({{ type: "insert", value: character }}));
                    grid.appendChild(button);
                }});
            }}

            doc.addEventListener("focusin", (event) => {{
                if (isEditableAnswerField(event.target) && !root.contains(event.target)) {{
                    activeField = event.target;
                    updateStatus();
                }}
            }});

            toggle.addEventListener("click", () => {{
                panel.hidden = false;
                toggle.hidden = true;
            }});
            close.addEventListener("click", () => {{
                panel.hidden = true;
                toggle.hidden = false;
                activeField?.focus({{ preventScroll: true }});
            }});
            languageSelect.addEventListener("change", () => {{
                selectedLanguage = languageSelect.value;
                renderCharacters();
                activeField?.focus({{ preventScroll: true }});
            }});
            root.querySelector('[data-control="space"]').addEventListener("mousedown", (event) => event.preventDefault());
            root.querySelector('[data-control="space"]').addEventListener("click", () => mutateActiveField({{ type: "insert", value: " " }}));
            root.querySelector('[data-control="backspace"]').addEventListener("mousedown", (event) => event.preventDefault());
            root.querySelector('[data-control="backspace"]').addEventListener("click", () => mutateActiveField({{ type: "backspace" }}));
            root.querySelector('[data-control="clear"]').addEventListener("mousedown", (event) => event.preventDefault());
            root.querySelector('[data-control="clear"]').addEventListener("click", () => mutateActiveField({{ type: "clear" }}));

            renderCharacters();
            updateStatus();
        }})();
        </script>
        """,
        height=0,
    )


def pdf_safe(text: Any) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def status_label(status: str) -> str:
    return {
        "correct": "Correcta",
        "wrong": "Incorrecta",
        "revealed": "Respuesta mostrada",
        "unanswered": "Sin comprobar",
    }.get(status, status)


def status_color(status: str):
    return {
        "correct": colors.HexColor("#dff3e7"),
        "wrong": colors.HexColor("#f8dddd"),
        "revealed": colors.HexColor("#fff0cf"),
        "unanswered": colors.HexColor("#eeeeee"),
    }.get(status, colors.white)


def build_pdf(exercise: dict[str, Any], language: str, level: str) -> bytes:
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title=str(exercise.get("title", "Ejercicio")),
        author="Aplicación de práctica de idiomas",
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CenteredTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            leading=24,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Question",
            parent=styles["Heading3"],
            fontSize=12,
            leading=15,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11)
    )

    story = [
        Paragraph(pdf_safe(exercise.get("title", "Ejercicio")), styles["CenteredTitle"]),
        Paragraph(
            f"<b>Idioma:</b> {pdf_safe(language)} &nbsp;&nbsp; "
            f"<b>Nivel:</b> {pdf_safe(level)}",
            styles["BodyText"],
        ),
        Spacer(1, 6 * mm),
    ]
    if exercise.get("description"):
        story.extend([
            Paragraph(pdf_safe(exercise["description"]), styles["BodyText"]),
            Spacer(1, 5 * mm),
        ])

    for index, question in enumerate(exercise["questions"], start=1):
        qid = str(question["id"])
        user_answer = st.session_state.get(answer_key(qid), "")
        status = st.session_state.get(status_key(qid), "unanswered")
        story.append(Paragraph(f"{index}. {pdf_safe(question['prompt'])}", styles["Question"]))
        rows = [
            [Paragraph("<b>Tu respuesta</b>", styles["Small"]), Paragraph(pdf_safe(user_answer or "—"), styles["Small"])],
            [Paragraph("<b>Respuesta correcta</b>", styles["Small"]), Paragraph(pdf_safe(question["answer"]), styles["Small"])],
            [Paragraph("<b>Resultado</b>", styles["Small"]), Paragraph(pdf_safe(status_label(status)), styles["Small"])],
            [Paragraph("<b>Explicación</b>", styles["Small"]), Paragraph(pdf_safe(question.get("explanation", "")), styles["Small"])],
        ]
        table = Table(rows, colWidths=[38 * mm, 136 * mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f2f2")),
            ("BACKGROUND", (1, 2), (1, 2), status_color(status)),
            ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#bbbbbb")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([table, Spacer(1, 7 * mm)])

    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()


st.markdown('<div class="app-title">Práctica de idiomas</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Selecciona un idioma, un nivel y un ejercicio. '
    'Puedes comprobar cada respuesta por separado o usar los controles inferiores.</div>',
    unsafe_allow_html=True,
)

languages = list_directories(DATA_DIR)
if not languages:
    st.error("No se encontraron idiomas. Crea carpetas como `data/aleman/A1/`.")
    st.stop()

_, language_column, level_column = st.columns([3.8, 1.4, 1.2])
with language_column:
    selected_language_path = st.selectbox(
        "Idioma", languages, format_func=lambda path: pretty_name(path.name), key="language_selector"
    )

levels = list_directories(selected_language_path)
if not levels:
    st.error(f"No hay niveles dentro de `{selected_language_path.name}`.")
    st.stop()

with level_column:
    selected_level_path = st.selectbox(
        "Titulación", levels, format_func=lambda path: path.name.upper(), key="level_selector"
    )

exercise_files = list_json_files(selected_level_path)
if not exercise_files:
    st.warning(f"No hay ejercicios JSON dentro de `{selected_level_path}`.")
    st.stop()

_, center, _ = st.columns([1.3, 2.4, 1.3])
with center:
    selected_exercise_path = st.selectbox(
        "Selecciona un ejercicio",
        exercise_files,
        format_func=lambda path: pretty_name(path.stem),
        key="exercise_selector",
    )

try:
    exercise = load_exercise(str(selected_exercise_path))
except (OSError, json.JSONDecodeError, ValueError) as error:
    st.error(f"No se pudo cargar el ejercicio: {error}")
    st.stop()

questions = exercise["questions"]
handle_exercise_change(str(selected_exercise_path.resolve()), questions)
render_focus_preserving_keyboard(selected_language_path.name)

st.divider()
st.subheader(exercise.get("title", pretty_name(selected_exercise_path.stem)))
if exercise.get("description"):
    st.write(exercise["description"])

for index, question in enumerate(questions, start=1):
    qid = str(question["id"])
    current_answer_key = answer_key(qid)
    current_status = st.session_state.get(status_key(qid), "unanswered")
    input_type = question.get("type", "text")

    with st.container(border=True):
        st.markdown(f'<div class="question-number">Pregunta {index}</div>', unsafe_allow_html=True)
        st.markdown(f"### {question['prompt']}")
        if question.get("help"):
            st.caption(question["help"])

        if input_type == "multiple_choice":
            options = [""] + [str(option) for option in question.get("options", [])]
            st.selectbox(
                "Tu respuesta",
                options,
                key=current_answer_key,
                label_visibility="collapsed",
                format_func=lambda value: "Selecciona una opción" if value == "" else value,
            )
        elif question.get("multiline", False):
            st.text_area(
                "Tu respuesta",
                key=current_answer_key,
                label_visibility="collapsed",
                placeholder="Escribe tu respuesta…",
                height=110,
            )
        else:
            st.text_input(
                "Tu respuesta",
                key=current_answer_key,
                label_visibility="collapsed",
                placeholder="Escribe tu respuesta…",
            )

        check_column, reveal_column, _ = st.columns([1, 1, 3])
        with check_column:
            st.button(
                "Comprobar",
                key=f"check_button__{qid}",
                on_click=check_one,
                args=(question,),
                use_container_width=True,
            )
        with reveal_column:
            st.button(
                "Ver respuesta",
                key=f"reveal_button__{qid}",
                on_click=reveal_one,
                args=(question,),
                use_container_width=True,
            )

        if current_status == "correct":
            st.markdown('<div class="result-correct"><b>✓ Respuesta correcta.</b></div>', unsafe_allow_html=True)
        elif current_status == "wrong":
            st.markdown(
                '<div class="result-wrong"><b>✗ Respuesta incorrecta.</b> '
                'Puedes intentarlo de nuevo o mostrar la solución.</div>',
                unsafe_allow_html=True,
            )
        elif current_status == "revealed":
            st.markdown(
                f'<div class="result-revealed"><b>Respuesta:</b> {question["answer"]}<br><br>'
                f'<b>Por qué:</b> {question["explanation"]}</div>',
                unsafe_allow_html=True,
            )

correct_count = sum(st.session_state.get(status_key(str(q["id"]))) == "correct" for q in questions)
wrong_count = sum(st.session_state.get(status_key(str(q["id"]))) == "wrong" for q in questions)
revealed_count = sum(st.session_state.get(status_key(str(q["id"]))) == "revealed" for q in questions)
st.caption(
    f"Progreso: {correct_count} correctas · {wrong_count} incorrectas · "
    f"{revealed_count} soluciones mostradas · {len(questions)} preguntas"
)

pdf_data = build_pdf(
    exercise,
    pretty_name(selected_language_path.name),
    selected_level_path.name.upper(),
)
pdf_filename = f"{selected_language_path.name}_{selected_level_path.name}_{selected_exercise_path.stem}.pdf"

with st.container(key="bottom_actions"):
    column_check, column_reveal, column_reset, column_export = st.columns(4)
    with column_check:
        st.button(
            "Comprobar respuestas",
            on_click=check_all,
            args=(questions,),
            use_container_width=True,
            type="primary",
        )
    with column_reveal:
        st.button("Ver respuestas", on_click=reveal_all, args=(questions,), use_container_width=True)
    with column_reset:
        st.button("Resetear ejercicio", on_click=reset_all, args=(questions,), use_container_width=True)
    with column_export:
        st.download_button(
            "Exportar documento",
            data=pdf_data,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True,
        )
