from __future__ import annotations

import json

import streamlit as st

from .language_helpers import LANGUAGE_LABELS, language_config_key, pretty_name

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

    st.iframe(
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
                    transition: top .18s ease;
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
                window.parent.__languagePracticeLayoutFloatingPanels?.();
            }});
            close.addEventListener("click", () => {{
                panel.hidden = true;
                toggle.hidden = false;
                activeField?.focus({{ preventScroll: true }});
                window.parent.__languagePracticeLayoutFloatingPanels?.();
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
        height=1,
    )
