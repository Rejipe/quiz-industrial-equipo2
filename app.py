import json
import random
import streamlit as st


# ------------------------ Config ------------------------
st.set_page_config(page_title="Quiz Industrial", page_icon="✅", layout="centered")
st.title("✅ Quiz Industrial")


# ------------------------ Helpers ------------------------
@st.cache_data
def cargar_preguntas(path: str = "preguntas.json") -> list[dict]:
    """Carga preguntas desde un JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validaciones mínimas
    if not isinstance(data, list):
        raise ValueError("El archivo preguntas.json debe contener una LISTA de preguntas.")

    for i, q in enumerate(data, start=1):
        if "pregunta" not in q or "opciones" not in q or "correcta" not in q:
            raise ValueError(f"Pregunta #{i} no tiene las claves requeridas: 'pregunta', 'opciones', 'correcta'.")
        if not isinstance(q["opciones"], dict):
            raise ValueError(f"Pregunta #{i}: 'opciones' debe ser un diccionario con A/B/C.")
        for k in ["A", "B", "C"]:
            if k not in q["opciones"]:
                raise ValueError(f"Pregunta #{i}: falta la opción '{k}' dentro de 'opciones'.")
        if q["correcta"] not in ["A", "B", "C"]:
            raise ValueError(f"Pregunta #{i}: 'correcta' debe ser 'A', 'B' o 'C'.")

    return data


def iniciar_quiz():
    """Selecciona 4 preguntas al azar y reinicia estado."""
    preguntas = st.session_state["banco_preguntas"]
    if len(preguntas) < 10:
        st.warning("⚠️ Recuerda: el banco debe tener mínimo 10 preguntas.")
    seleccion = random.sample(preguntas, k=min(4, len(preguntas)))

    st.session_state["quiz"] = seleccion
    st.session_state["respuestas_usuario"] = {}  # idx -> "A"/"B"/"C"
    st.session_state["enviado"] = False


# ------------------------ Cargar banco ------------------------
try:
    banco = cargar_preguntas("preguntas.json")
except FileNotFoundError:
    st.error("No se encontró 'preguntas.json' en el repositorio. Súbelo junto con app.py.")
    st.stop()
except Exception as e:
    st.error(f"Error al cargar preguntas.json: {e}")
    st.stop()

st.session_state.setdefault("banco_preguntas", banco)

# ------------------------ Estado inicial ------------------------
if "quiz" not in st.session_state:
    iniciar_quiz()

# ------------------------ Controles ------------------------
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Reiniciar (nuevas preguntas)"):
        iniciar_quiz()
        st.rerun()

with col2:
    st.caption("Se seleccionan 4 preguntas aleatorias sin repetir.")


st.divider()

# ------------------------ Mostrar preguntas ------------------------
quiz = st.session_state["quiz"]

for idx, q in enumerate(quiz, start=1):
    st.subheader(f"Pregunta {idx}")
    st.write(q["pregunta"])

    opciones = q["opciones"]  # {"A": "...", "B": "...", "C": "..."}
    labels = [f"A) {opciones['A']}", f"B) {opciones['B']}", f"C) {opciones['C']}"]
    map_label_to_key = {"A": labels[0], "B": labels[1], "C": labels[2]}
    map_key_to_label = {v: k for k, v in map_label_to_key.items()}

    # Valor actual guardado
    key_state = f"q_{idx}"
    prev_key = st.session_state["respuestas_usuario"].get(idx)
    prev_label = map_label_to_key.get(prev_key, None)

    seleccion_label = st.radio(
        "Elige una opción:",
        labels,
        index=labels.index(prev_label) if prev_label in labels else 0,
        key=key_state,
        disabled=st.session_state.get("enviado", False),
        label_visibility="collapsed",
    )

    # Guardar como A/B/C
    st.session_state["respuestas_usuario"][idx] = map_key_to_label[seleccion_label]

    st.divider()

# ------------------------ Enviar / Resultados ------------------------
if not st.session_state.get("enviado", False):
    if st.button("✅ Enviar respuestas"):
        st.session_state["enviado"] = True
        st.rerun()
else:
    puntos = 0
    st.header("📊 Resultados")

    for idx, q in enumerate(quiz, start=1):
        correcta = q["correcta"]
        user = st.session_state["respuestas_usuario"].get(idx)

        if user == correcta:
            puntos += 1
            st.success(f"Pregunta {idx}: Correcta ✅ (Elegiste {user})")
        else:
            st.error(f"Pregunta {idx}: Incorrecta ❌ (Elegiste {user} | Correcta: {correcta})")

    calificacion = (puntos / 4) * 10 if len(quiz) >= 4 else (puntos / max(len(quiz), 1)) * 10

    st.subheader(f"✅ Puntos: {puntos} / 4")
    st.subheader(f"🎓 Calificación: {calificacion:.1f} / 10")

    st.info("Si das clic en **Reiniciar**, se seleccionan 4 preguntas nuevas al azar.")
