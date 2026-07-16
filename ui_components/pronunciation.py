from __future__ import annotations

import json

import streamlit.components.v1 as components

from .language_helpers import PRONUNCIATION_LANGUAGES, language_config_key


def render_focus_preserving_pronunciation(language: str) -> None:
    selected_language_key = language_config_key(language)
    default_language = PRONUNCIATION_LANGUAGES.get(selected_language_key, "en-US")

    components.html(
        f"""
        <script>
        (() => {{
            const doc = window.parent.document;
            const rootId = "focus-preserving-pronunciation";
            doc.getElementById(rootId)?.remove();

            const defaultLanguage = {json.dumps(default_language, ensure_ascii=False)};
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
            let availableVoices = [];
            const root = doc.createElement("div");
            root.id = rootId;
            root.style.setProperty("--fpp-bg", panelBackground);
            root.style.setProperty("--fpp-soft-bg", softBackground);
            root.style.setProperty("--fpp-hover-bg", hoverBackground);
            root.style.setProperty("--fpp-text", appColor);
            root.style.setProperty("--fpp-muted", mutedColor);
            root.style.setProperty("--fpp-border", borderColor);
            root.style.setProperty("--fpp-shadow", shadowColor);
            root.style.setProperty("--fpp-primary", primaryColor);
            root.innerHTML = `
                <button class="fpp-toggle" type="button">Pronunciacion</button>
                <section class="fpp-panel" hidden>
                    <div class="fpp-header">
                        <strong>Pronunciacion</strong>
                        <button class="fpp-close" type="button" aria-label="Cerrar">×</button>
                    </div>
                    <label>
                        Texto
                        <textarea class="fpp-text" rows="3" placeholder="Escribe o carga una respuesta"></textarea>
                    </label>
                    <label>
                        Voz
                        <select class="fpp-voice"></select>
                    </label>
                    <label>
                        Velocidad
                        <input class="fpp-rate" type="range" min="0.65" max="1.25" step="0.05" value="0.9" />
                    </label>
                    <div class="fpp-actions">
                        <button class="fpp-load" type="button">Usar respuesta</button>
                        <button class="fpp-speak" type="button">Escuchar</button>
                        <button class="fpp-stop" type="button">Parar</button>
                    </div>
                    <div class="fpp-status" aria-live="polite">Selecciona un campo de respuesta o escribe una frase.</div>
                </section>
            `;

            const style = doc.createElement("style");
            style.textContent = `
                #${{rootId}} {{
                    position: fixed;
                    right: 1rem;
                    top: 12.2rem;
                    z-index: 99998;
                    width: min(340px, calc(100vw - 2rem));
                    font-family: "Source Sans Pro", sans-serif;
                    color: var(--fpp-text);
                    transition: top .18s ease;
                }}
                #${{rootId}} .fpp-toggle,
                #${{rootId}} button,
                #${{rootId}} select,
                #${{rootId}} textarea,
                #${{rootId}} input {{
                    font: inherit;
                }}
                #${{rootId}} .fpp-toggle {{
                    float: right;
                    width: 210px;
                    border: 1px solid var(--fpp-border);
                    border-radius: 8px;
                    padding: .5rem .65rem;
                    background: var(--fpp-bg);
                    color: var(--fpp-text);
                    box-shadow: 0 8px 24px var(--fpp-shadow);
                    cursor: pointer;
                }}
                #${{rootId}} .fpp-toggle:hover,
                #${{rootId}} .fpp-close:hover,
                #${{rootId}} .fpp-actions button:hover {{
                    background: var(--fpp-hover-bg);
                    border-color: var(--fpp-primary);
                }}
                #${{rootId}} .fpp-toggle:focus-visible,
                #${{rootId}} button:focus-visible,
                #${{rootId}} select:focus-visible,
                #${{rootId}} textarea:focus-visible,
                #${{rootId}} input:focus-visible {{
                    outline: 2px solid var(--fpp-primary);
                    outline-offset: 2px;
                }}
                #${{rootId}} .fpp-panel {{
                    clear: both;
                    padding: .85rem;
                    max-height: calc(100vh - 13.5rem);
                    overflow-y: auto;
                    background: var(--fpp-bg);
                    color: var(--fpp-text);
                    border: 1px solid var(--fpp-border);
                    border-radius: 8px;
                    box-shadow: 0 12px 32px var(--fpp-shadow);
                }}
                #${{rootId}} .fpp-header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: .75rem;
                    margin-bottom: .65rem;
                }}
                #${{rootId}} .fpp-close {{
                    width: 2rem;
                    height: 2rem;
                    border: 1px solid var(--fpp-border);
                    border-radius: 6px;
                    background: var(--fpp-soft-bg);
                    color: var(--fpp-text);
                    cursor: pointer;
                }}
                #${{rootId}} label {{
                    display: grid;
                    gap: .3rem;
                    margin-bottom: .65rem;
                    font-size: .9rem;
                }}
                #${{rootId}} select,
                #${{rootId}} textarea {{
                    width: 100%;
                    box-sizing: border-box;
                    border: 1px solid var(--fpp-border);
                    border-radius: 6px;
                    padding: .45rem;
                    background: var(--fpp-bg);
                    color: var(--fpp-text);
                }}
                #${{rootId}} textarea {{
                    resize: vertical;
                    min-height: 4.8rem;
                }}
                #${{rootId}} input[type="range"] {{
                    width: 100%;
                }}
                #${{rootId}} .fpp-actions {{
                    display: grid;
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                    gap: .35rem;
                }}
                #${{rootId}} .fpp-actions button {{
                    min-height: 2rem;
                    border: 1px solid var(--fpp-border);
                    border-radius: 6px;
                    background: var(--fpp-soft-bg);
                    color: var(--fpp-text);
                    cursor: pointer;
                }}
                #${{rootId}} .fpp-status {{
                    min-height: 1.4rem;
                    margin-top: .65rem;
                    color: var(--fpp-muted);
                    font-size: .85rem;
                }}
                @media (max-width: 700px) {{
                    #${{rootId}} {{
                        right: .65rem;
                        top: 11rem;
                        width: min(320px, calc(100vw - 1.3rem));
                    }}
                }}
            `;
            root.appendChild(style);
            doc.body.appendChild(root);

            const toggle = root.querySelector(".fpp-toggle");
            const panel = root.querySelector(".fpp-panel");
            const close = root.querySelector(".fpp-close");
            const textInput = root.querySelector(".fpp-text");
            const voiceSelect = root.querySelector(".fpp-voice");
            const rateInput = root.querySelector(".fpp-rate");
            const loadButton = root.querySelector(".fpp-load");
            const speakButton = root.querySelector(".fpp-speak");
            const stopButton = root.querySelector(".fpp-stop");
            const status = root.querySelector(".fpp-status");

            function rem(value) {{
                const fontSize = Number.parseFloat(window.parent.getComputedStyle(doc.documentElement).fontSize) || 16;
                return value * fontSize;
            }}

            function getDefaultTop() {{
                return rem(window.parent.matchMedia("(max-width: 700px)").matches ? 11 : 12.2);
            }}

            function isEditableAnswerField(element) {{
                if (!element) return false;
                const tagName = element.tagName;
                const isTextInput = tagName === "INPUT" && ["text", "search"].includes(element.type);
                return tagName === "TEXTAREA" || isTextInput;
            }}

            function isOpen(rootSelector, panelSelector) {{
                const otherPanel = doc.querySelector(`${{rootSelector}} ${{panelSelector}}`);
                return Boolean(otherPanel && !otherPanel.hidden);
            }}

            function updatePosition() {{
                const margin = 16;
                const gap = 12;
                const viewportHeight = window.parent.innerHeight;
                const isMobile = window.parent.matchMedia("(max-width: 700px)").matches;
                const floatingPanels = [
                    {{
                        rootId: "focus-preserving-character-keyboard",
                        panelSelector: ".fpck-panel",
                        toggleSelector: ".fpck-toggle",
                        defaultTop: rem(isMobile ? 4.5 : 5.2),
                    }},
                    {{
                        rootId: "focus-preserving-translator",
                        panelSelector: ".fpt-panel",
                        toggleSelector: ".fpt-toggle",
                        defaultTop: rem(isMobile ? 7.8 : 8.7),
                    }},
                    {{
                        rootId,
                        panelSelector: ".fpp-panel",
                        toggleSelector: ".fpp-toggle",
                        defaultTop: getDefaultTop(),
                    }},
                ];
                let nextAvailableTop = margin;

                floatingPanels.forEach((item) => {{
                    const itemRoot = doc.getElementById(item.rootId);
                    if (!itemRoot) return;

                    const itemPanel = itemRoot.querySelector(item.panelSelector);
                    const itemToggle = itemRoot.querySelector(item.toggleSelector);
                    const isPanelOpen = Boolean(itemPanel && !itemPanel.hidden);
                    const currentHeight = itemRoot.offsetHeight
                        || (isPanelOpen ? itemPanel?.offsetHeight : itemToggle?.offsetHeight)
                        || 40;
                    const maxTop = Math.max(margin, viewportHeight - currentHeight - margin);
                    const nextTop = Math.min(
                        Math.max(item.defaultTop, nextAvailableTop),
                        maxTop,
                    );

                    itemRoot.style.top = `${{nextTop}}px`;
                    if (itemPanel) {{
                        itemPanel.style.maxHeight = `${{Math.max(160, viewportHeight - nextTop - margin)}}px`;
                    }}

                    const updatedHeight = itemRoot.offsetHeight
                        || (isPanelOpen ? itemPanel?.offsetHeight : itemToggle?.offsetHeight)
                        || currentHeight;
                    nextAvailableTop = nextTop + updatedHeight + gap;
                }});
            }}

            function refreshVoices() {{
                if (!("speechSynthesis" in window.parent)) {{
                    voiceSelect.replaceChildren();
                    const option = doc.createElement("option");
                    option.textContent = "Voz no disponible";
                    voiceSelect.appendChild(option);
                    status.textContent = "Tu navegador no ofrece sintesis de voz.";
                    return;
                }}

                const voices = window.parent.speechSynthesis.getVoices();
                availableVoices = voices.filter((voice) =>
                    voice.lang?.toLowerCase().startsWith(defaultLanguage.slice(0, 2).toLowerCase())
                );
                if (availableVoices.length === 0) availableVoices = voices;

                voiceSelect.replaceChildren();
                availableVoices.forEach((voice, index) => {{
                    const option = doc.createElement("option");
                    option.value = String(index);
                    option.textContent = `${{voice.name}} (${{voice.lang}})`;
                    option.selected = voice.lang === defaultLanguage || voice.lang?.startsWith(defaultLanguage.slice(0, 2));
                    voiceSelect.appendChild(option);
                }});

                if (availableVoices.length === 0) {{
                    const option = doc.createElement("option");
                    option.textContent = defaultLanguage;
                    voiceSelect.appendChild(option);
                }}
            }}

            function loadActiveField() {{
                if (!activeField || !doc.body.contains(activeField)) {{
                    status.textContent = "Selecciona un campo de respuesta primero.";
                    return;
                }}
                textInput.value = activeField.value || "";
                textInput.focus();
                status.textContent = textInput.value
                    ? "Respuesta cargada."
                    : "El campo seleccionado esta vacio.";
            }}

            function speak() {{
                const text = textInput.value.trim();
                if (!text) {{
                    status.textContent = "Escribe o carga un texto para escucharlo.";
                    return;
                }}
                if (!("speechSynthesis" in window.parent)) {{
                    status.textContent = "Tu navegador no ofrece sintesis de voz.";
                    return;
                }}

                window.parent.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = defaultLanguage;
                utterance.rate = Number(rateInput.value) || 0.9;
                utterance.pitch = 1;
                const selectedVoice = availableVoices[Number(voiceSelect.value)];
                if (selectedVoice) utterance.voice = selectedVoice;
                utterance.onstart = () => {{
                    status.textContent = "Reproduciendo...";
                }};
                utterance.onend = () => {{
                    status.textContent = "Listo.";
                }};
                utterance.onerror = () => {{
                    status.textContent = "No se pudo reproducir la pronunciacion.";
                }};
                window.parent.speechSynthesis.speak(utterance);
            }}

            doc.addEventListener("focusin", (event) => {{
                if (isEditableAnswerField(event.target) && !root.contains(event.target)) {{
                    activeField = event.target;
                }}
            }});

            toggle.addEventListener("click", () => {{
                panel.hidden = false;
                toggle.hidden = true;
                refreshVoices();
                updatePosition();
                textInput.focus();
            }});
            close.addEventListener("click", () => {{
                panel.hidden = true;
                toggle.hidden = false;
                window.parent.speechSynthesis?.cancel();
                activeField?.focus({{ preventScroll: true }});
                updatePosition();
            }});
            loadButton.addEventListener("click", loadActiveField);
            speakButton.addEventListener("click", speak);
            stopButton.addEventListener("click", () => {{
                window.parent.speechSynthesis?.cancel();
                status.textContent = "Reproduccion detenida.";
            }});
            window.parent.speechSynthesis?.addEventListener?.("voiceschanged", refreshVoices);
            window.parent.__languagePracticeLayoutFloatingPanels = updatePosition;
            new MutationObserver(updatePosition).observe(doc.body, {{
                attributes: true,
                attributeFilter: ["hidden"],
                childList: true,
                subtree: true,
            }});
            window.parent.addEventListener("resize", updatePosition);
            refreshVoices();
            updatePosition();
        }})();
        </script>
        """,
        height=0,
    )
