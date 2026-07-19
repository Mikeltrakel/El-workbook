from __future__ import annotations

import json

import streamlit as st

from .language_helpers import TRANSLATION_LANGUAGES, language_config_key


def render_focus_preserving_translator(language: str) -> None:
    selected_language_key = language_config_key(language)
    target_code = TRANSLATION_LANGUAGES.get(selected_language_key, "en")
    default_source = "es" if target_code != "es" else "en"
    language_options = {
        "es": "Español",
        "en": "Inglés",
        "de": "Alemán",
        "fr": "Francés",
        "el": "Griego",
        "ru": "Ruso",
    }

    st.iframe(
        f"""
        <script>
        (() => {{
            const doc = window.parent.document;
            const rootId = "focus-preserving-translator";
            doc.getElementById(rootId)?.remove();

            const languageOptions = {json.dumps(language_options, ensure_ascii=False)};
            const defaultSource = {json.dumps(default_source, ensure_ascii=False)};
            const defaultTarget = {json.dumps(target_code, ensure_ascii=False)};
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
            const root = doc.createElement("div");
            root.id = rootId;
            root.style.setProperty("--fpt-bg", panelBackground);
            root.style.setProperty("--fpt-soft-bg", softBackground);
            root.style.setProperty("--fpt-hover-bg", hoverBackground);
            root.style.setProperty("--fpt-text", appColor);
            root.style.setProperty("--fpt-muted", mutedColor);
            root.style.setProperty("--fpt-border", borderColor);
            root.style.setProperty("--fpt-shadow", shadowColor);
            root.style.setProperty("--fpt-primary", primaryColor);
            root.innerHTML = `
                <button class="fpt-toggle" type="button">Traductor</button>
                <section class="fpt-panel" hidden>
                    <div class="fpt-header">
                        <strong>Traductor</strong>
                        <button class="fpt-close" type="button" aria-label="Cerrar">×</button>
                    </div>
                    <div class="fpt-languages">
                        <label>
                            De
                            <select class="fpt-source"></select>
                        </label>
                        <button class="fpt-swap" type="button" aria-label="Intercambiar idiomas">↔</button>
                        <label>
                            A
                            <select class="fpt-target"></select>
                        </label>
                    </div>
                    <label class="fpt-label">
                        Palabra o frase
                        <input class="fpt-query" type="text" placeholder="Escribe una palabra" />
                    </label>
                    <div class="fpt-actions">
                        <button class="fpt-translate" type="button">Traducir</button>
                        <button class="fpt-insert" type="button" disabled>Insertar</button>
                    </div>
                    <div class="fpt-result" aria-live="polite">Selecciona un campo de respuesta para insertar.</div>
                </section>
            `;

            const style = doc.createElement("style");
            style.textContent = `
                #${{rootId}} {{
                    position: fixed;
                    right: 1rem;
                    top: 8.7rem;
                    z-index: 99999;
                    width: min(340px, calc(100vw - 2rem));
                    font-family: "Source Sans Pro", sans-serif;
                    color: var(--fpt-text);
                    transition: top .18s ease;
                }}
                #${{rootId}} .fpt-toggle,
                #${{rootId}} button,
                #${{rootId}} select,
                #${{rootId}} input {{
                    font: inherit;
                }}
                #${{rootId}} .fpt-toggle {{
                    float: right;
                    width: 210px;
                    border: 1px solid var(--fpt-border);
                    border-radius: 8px;
                    padding: .5rem .65rem;
                    background: var(--fpt-bg);
                    color: var(--fpt-text);
                    box-shadow: 0 8px 24px var(--fpt-shadow);
                    cursor: pointer;
                }}
                #${{rootId}} .fpt-toggle:hover,
                #${{rootId}} .fpt-close:hover,
                #${{rootId}} .fpt-swap:hover,
                #${{rootId}} .fpt-actions button:hover:not(:disabled) {{
                    background: var(--fpt-hover-bg);
                    border-color: var(--fpt-primary);
                }}
                #${{rootId}} .fpt-toggle:focus-visible,
                #${{rootId}} button:focus-visible,
                #${{rootId}} select:focus-visible,
                #${{rootId}} input:focus-visible {{
                    outline: 2px solid var(--fpt-primary);
                    outline-offset: 2px;
                }}
                #${{rootId}} .fpt-panel {{
                    clear: both;
                    padding: .85rem;
                    max-height: calc(100vh - 10rem);
                    overflow-y: auto;
                    background: var(--fpt-bg);
                    color: var(--fpt-text);
                    border: 1px solid var(--fpt-border);
                    border-radius: 8px;
                    box-shadow: 0 12px 32px var(--fpt-shadow);
                }}
                #${{rootId}} .fpt-header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: .75rem;
                    margin-bottom: .65rem;
                }}
                #${{rootId}} .fpt-close,
                #${{rootId}} .fpt-swap {{
                    border: 1px solid var(--fpt-border);
                    border-radius: 6px;
                    background: var(--fpt-soft-bg);
                    color: var(--fpt-text);
                    cursor: pointer;
                }}
                #${{rootId}} .fpt-close {{
                    width: 2rem;
                    height: 2rem;
                }}
                #${{rootId}} .fpt-languages {{
                    display: grid;
                    grid-template-columns: minmax(0, 1fr) 2rem minmax(0, 1fr);
                    gap: .45rem;
                    align-items: end;
                    margin-bottom: .65rem;
                }}
                #${{rootId}} label {{
                    display: grid;
                    gap: .3rem;
                    font-size: .9rem;
                }}
                #${{rootId}} select,
                #${{rootId}} input {{
                    width: 100%;
                    box-sizing: border-box;
                    border: 1px solid var(--fpt-border);
                    border-radius: 6px;
                    padding: .45rem;
                    background: var(--fpt-bg);
                    color: var(--fpt-text);
                }}
                #${{rootId}} .fpt-actions {{
                    display: grid;
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    gap: .35rem;
                    margin-top: .65rem;
                }}
                #${{rootId}} .fpt-actions button {{
                    min-height: 2rem;
                    border: 1px solid var(--fpt-border);
                    border-radius: 6px;
                    background: var(--fpt-soft-bg);
                    color: var(--fpt-text);
                    cursor: pointer;
                }}
                #${{rootId}} .fpt-actions button:disabled {{
                    cursor: not-allowed;
                    opacity: .55;
                }}
                #${{rootId}} .fpt-result {{
                    min-height: 2.2rem;
                    margin-top: .65rem;
                    color: var(--fpt-muted);
                    font-size: .9rem;
                    word-break: break-word;
                }}
                #${{rootId}} .fpt-result strong {{
                    color: var(--fpt-text);
                }}
                @media (max-width: 700px) {{
                    #${{rootId}} {{
                        right: .65rem;
                        top: 7.8rem;
                        width: min(320px, calc(100vw - 1.3rem));
                    }}
                }}
            `;
            root.appendChild(style);
            doc.body.appendChild(root);

            const toggle = root.querySelector(".fpt-toggle");
            const panel = root.querySelector(".fpt-panel");
            const close = root.querySelector(".fpt-close");
            const sourceSelect = root.querySelector(".fpt-source");
            const targetSelect = root.querySelector(".fpt-target");
            const swapButton = root.querySelector(".fpt-swap");
            const queryInput = root.querySelector(".fpt-query");
            const translateButton = root.querySelector(".fpt-translate");
            const insertButton = root.querySelector(".fpt-insert");
            const result = root.querySelector(".fpt-result");
            let translatedText = "";

            function rem(value) {{
                const fontSize = Number.parseFloat(window.parent.getComputedStyle(doc.documentElement).fontSize) || 16;
                return value * fontSize;
            }}

            function getDefaultTop() {{
                return rem(window.parent.matchMedia("(max-width: 700px)").matches ? 7.8 : 8.7);
            }}

            function getKeyboardRoot() {{
                return doc.getElementById("focus-preserving-character-keyboard");
            }}

            function isKeyboardPanelOpen() {{
                const keyboardPanel = getKeyboardRoot()?.querySelector(".fpck-panel");
                return Boolean(keyboardPanel && !keyboardPanel.hidden);
            }}

            function updateTranslatorPosition() {{
                if (window.parent.__languagePracticeLayoutFloatingPanels) {{
                    window.parent.__languagePracticeLayoutFloatingPanels();
                    return;
                }}

                const margin = 16;
                const gap = 12;
                const viewportHeight = window.parent.innerHeight;
                const ownHeight = root.offsetHeight || (panel.hidden ? toggle.offsetHeight : panel.offsetHeight);
                const maxTop = Math.max(margin, viewportHeight - ownHeight - margin);
                let nextTop = getDefaultTop();

                if (isKeyboardPanelOpen()) {{
                    const keyboardBottom = getKeyboardRoot().getBoundingClientRect().bottom;
                    nextTop = Math.min(Math.max(keyboardBottom + gap, margin), maxTop);
                }}

                root.style.top = `${{nextTop}}px`;
                panel.style.maxHeight = `${{Math.max(160, viewportHeight - nextTop - margin)}}px`;
            }}

            function fillLanguageSelect(select, selectedValue) {{
                Object.entries(languageOptions).forEach(([code, label]) => {{
                    const option = doc.createElement("option");
                    option.value = code;
                    option.textContent = label;
                    option.selected = code === selectedValue;
                    select.appendChild(option);
                }});
            }}

            function isEditableAnswerField(element) {{
                if (!element) return false;
                const tagName = element.tagName;
                const isTextInput = tagName === "INPUT" && ["text", "search"].includes(element.type);
                return tagName === "TEXTAREA" || isTextInput;
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

            function insertTranslation() {{
                if (!translatedText || !activeField || !doc.body.contains(activeField)) {{
                    result.textContent = translatedText
                        ? "Selecciona un campo de respuesta para insertar."
                        : "Traduce una palabra primero.";
                    return;
                }}

                const start = activeField.selectionStart ?? activeField.value.length;
                const end = activeField.selectionEnd ?? activeField.value.length;
                const value = activeField.value;
                const nextValue = value.slice(0, start) + translatedText + value.slice(end);
                const nextCursor = start + translatedText.length;
                setNativeValue(activeField, nextValue);
                activeField.focus({{ preventScroll: true }});
                activeField.setSelectionRange(nextCursor, nextCursor);
            }}

            async function translate() {{
                const query = queryInput.value.trim();
                translatedText = "";
                insertButton.disabled = true;

                if (!query) {{
                    result.textContent = "Escribe una palabra o frase para traducir.";
                    return;
                }}
                if (sourceSelect.value === targetSelect.value) {{
                    result.textContent = "Elige dos idiomas distintos.";
                    return;
                }}

                result.textContent = "Traduciendo...";
                translateButton.disabled = true;
                try {{
                    const langpair = `${{sourceSelect.value}}|${{targetSelect.value}}`;
                    const url = `https://api.mymemory.translated.net/get?q=${{encodeURIComponent(query)}}&langpair=${{encodeURIComponent(langpair)}}`;
                    const response = await fetch(url);
                    if (!response.ok) throw new Error("HTTP " + response.status);
                    const data = await response.json();
                    translatedText = data?.responseData?.translatedText?.trim() || "";
                    if (!translatedText) throw new Error("Empty translation");
                    const strong = doc.createElement("strong");
                    strong.textContent = translatedText;
                    result.replaceChildren(strong);
                    insertButton.disabled = false;
                }} catch (error) {{
                    result.textContent = "No se pudo traducir ahora. Revisa la conexion o prueba de nuevo.";
                }} finally {{
                    translateButton.disabled = false;
                }}
            }}

            fillLanguageSelect(sourceSelect, defaultSource);
            fillLanguageSelect(targetSelect, defaultTarget);

            doc.addEventListener("focusin", (event) => {{
                if (isEditableAnswerField(event.target) && !root.contains(event.target)) {{
                    activeField = event.target;
                }}
            }});

            toggle.addEventListener("click", () => {{
                panel.hidden = false;
                toggle.hidden = true;
                queryInput.focus();
                updateTranslatorPosition();
            }});
            close.addEventListener("click", () => {{
                panel.hidden = true;
                toggle.hidden = false;
                activeField?.focus({{ preventScroll: true }});
                updateTranslatorPosition();
            }});
            swapButton.addEventListener("click", () => {{
                const previousSource = sourceSelect.value;
                sourceSelect.value = targetSelect.value;
                targetSelect.value = previousSource;
                queryInput.focus();
            }});
            translateButton.addEventListener("click", translate);
            queryInput.addEventListener("keydown", (event) => {{
                if (event.key === "Enter") {{
                    event.preventDefault();
                    translate();
                }}
            }});
            insertButton.addEventListener("mousedown", (event) => event.preventDefault());
            insertButton.addEventListener("click", insertTranslation);

            const keyboardObserver = new MutationObserver(updateTranslatorPosition);
            const observeKeyboard = () => {{
                const keyboardRoot = getKeyboardRoot();
                if (!keyboardRoot) return;
                keyboardObserver.observe(keyboardRoot, {{
                    attributes: true,
                    attributeFilter: ["hidden"],
                    childList: true,
                    subtree: true,
                }});
            }};
            observeKeyboard();
            window.parent.addEventListener("resize", updateTranslatorPosition);
            updateTranslatorPosition();
        }})();
        </script>
        """,
        height=1,
    )
