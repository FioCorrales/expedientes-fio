import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import os
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Fio Corrales Studio OS", page_icon="✒️", layout="centered")

# --- ESTILOS CSS SUPREMO ---
st.markdown("""
    <style>
    .main { background-color: #121212; color: #E0E0E0; }
    h1, h2, h3 { color: #D4AF37; font-family: 'Helvetica Neue', sans-serif; }
    .seccion-titulo { color: #D4AF37; border-bottom: 2px solid #D4AF37; padding-bottom: 5px; margin-top: 25px; margin-bottom: 15px;}
    .marco-studio { border: 1px solid #D4AF37; padding: 25px; border-radius: 12px; background-color: #1A1A1A; box-shadow: 0 4px 15px rgba(0,0,0,0.5);}
    div[data-testid="stImage"] { display: flex; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

# --- CLASE PDF PROFESIONAL ---
class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 16)
        self.cell(0, 10, "Fio Corrales Tattoo & Beauty Studio", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 10)
        self.cell(0, 5, "Ciudad Quesada, Costa Rica | +506 62165089", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "B", 11)
        self.cell(0, 8, "DECLARACIÓN JURADA Y CONSENTIMIENTO INFORMADO", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 11)
        self.set_fill_color(212, 175, 55) # Color Oro para el PDF
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def chapter_body(self, text, bold=False):
        style = "B" if bold else ""
        self.set_font("helvetica", style, 10)
        self.multi_cell(0, 5, text)
        self.ln(3)

# --- INICIO DE INTERFAZ ---
try:
    logo = Image.open("IMG-20260408-WA0028.jpg")
    st.image(logo, width=280)
except FileNotFoundError:
    st.warning("⚠️ Logo no detectado.")

st.title("Bienvenido al sistema de registro de Fio Corrales Tattoo & Beauty Studio")
st.write("Complete la declaración jurada a continuación.")

st.markdown('<div class="marco-studio">', unsafe_allow_html=True)

# --- 1. DATOS PERSONALES ---
st.markdown('<h3 class="seccion-titulo">📋 Identificación del Cliente</h3>', unsafe_allow_html=True)
nombre = st.text_input("Nombre Completo *")
col1, col2 = st.columns(2)
with col1:
    cedula = st.text_input("Número de Identificación (Cédula/Pasaporte) *")
    telefono = st.text_input("Número de WhatsApp *")
with col2:
    edad = st.number_input("Edad Real *", min_value=15, max_value=100, step=1)
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    st.text_input("Fecha de Registro", value=fecha_hoy, disabled=True)

procedimiento = st.selectbox("Tipo de Procedimiento:", 
    ["Tatuaje", "Piercing", "Microblading/Cejas", "Delineado Ojos", "Labios", "Micropigmentación"])

st.markdown("**Registro de Trazabilidad Sanitaria**")
col3, col4 = st.columns(2)
with col3:
    lote_tinta = st.text_input("Marca y Lote de Pigmento / Tinta")
with col4:
    lote_aguja = st.text_input("Lote de Aguja (Estéril y Desechable)")

# --- 2. DECLARACIÓN JURADA DE SALUD ---
st.markdown('<h3 class="seccion-titulo">⚕️ Declaración Jurada de Salud</h3>', unsafe_allow_html=True)
st.warning("Usted declara bajo juramento que:")

col_check1, col_check2 = st.columns(2)
with col_check1:
    no_ebrio = st.checkbox("NO me encuentro bajo efectos de alcohol o drogas. *")
    no_embarazo = st.checkbox("NO estoy embarazada ni en periodo de lactancia. *")
with col_check2:
    no_infec = st.checkbox("NO padezco enfermedades infectocontagiosas. *")

st.markdown("**Indique si padece alguna de estas condiciones (si no marca ninguna, se declara que NO las padece):**")
c1, c2, c3 = st.columns(3)
with c1:
    diabetes = st.checkbox("Diabetes")
    epilepsia = st.checkbox("Epilepsia")
with c2:
    corazon = st.checkbox("Cardiopatías")
    hemofilia = st.checkbox("Hemofilia")
with c3:
    alergias = st.checkbox("Alergias")
    queloide = st.checkbox("Queloides")

alergia_lido = st.checkbox("Alergia específica a la Lidocaína")
afeccion_piel = st.checkbox("Afecciones de la piel (zona a tratar)")
detalles_medicos = st.text_area("Detalles médicos adicionales", placeholder="Escriba aquí cualquier otro detalle importante...")

# --- 3. DOCUMENTACIÓN ---
st.markdown('<h3 class="seccion-titulo">📎 Evidencia Documental</h3>', unsafe_allow_html=True)
foto_diseno = st.file_uploader("Diseño Final Aprobado", type=["jpg", "png", "jpeg"])
col_f1, col_f2 = st.columns(2)
with col_f1:
    id_frente = st.file_uploader("Documento Identidad (Frente) *", type=["jpg", "png", "jpeg"])
with col_f2:
    id_atras = st.file_uploader("Documento Identidad (Atrás) *", type=["jpg", "png", "jpeg"])

permiso_padre = None
if edad < 18:
    permiso_padre = st.file_uploader("Permiso Legal del Tutor (Obligatorio) *", type=["jpg", "png", "jpeg"])

# --- 4. CONSENTIMIENTO Y FIRMA ---
st.markdown('<h3 class="seccion-titulo">⚖️ Firma y Consentimiento</h3>', unsafe_allow_html=True)
st.write("**Declaración de Compromiso:**")
st.write("1. Declaro bajo juramento que toda la información brindada es la verdad.")
st.write("2. He recibido las instrucciones sobre los cuidados posteriores de forma clara.")
st.write("3. Acepto los riesgos inherentes al procedimiento (infección, reacciones alérgicas).")
st.write("4. He revisado y aprobado el diseño, ubicación y ortografía.")

autoriza_imagen = st.radio("Autorización de Imagen y Redes Sociales:", ["Sí autorizo", "NO autorizo"], horizontal=True)

st.write("**Firme en el recuadro blanco:**")
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0.3)",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=150,
    width=320,
    drawing_mode="freedraw",
    key="canvas",
)

acepta_terminos = st.checkbox("Acepto los términos y ratifico mi declaración jurada. *")

submit_btn = st.button("GENERAR DOCUMENTO LEGAL DEFINITIVO")
st.markdown('</div>', unsafe_allow_html=True)

# --- PROCESAMIENTO ---
if submit_btn:
    if not nombre or not cedula or not acepta_terminos or not no_ebrio or not no_embarazo:
        st.error("❌ Error: Debe completar los campos obligatorios, confirmar sobriedad y no embarazo.")
    elif canvas_result.image_data is None or np.sum(canvas_result.image_data) == 0:
        st.error("❌ Error: El documento no puede ser generado sin la firma del cliente.")
    else:
        archivos_temp = []
        
        # 1. Preparar Firma
        firma_img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        temp_firma = "temp_firma_pro.png"
        firma_img.save(temp_firma)
        archivos_temp.append(temp_firma)

        # 2. Motor de PDF
        pdf = PDF()
        pdf.add_page()
        
        # SECCIÓN DATOS
        pdf.chapter_title("I. IDENTIFICACIÓN DEL CLIENTE")
        pdf.chapter_body(f"Nombre: {nombre}\nIdentificación: {cedula}\nTeléfono: {telefono}\nEdad: {edad} años\nFecha: {fecha_hoy}")
        pdf.chapter_body(f"Procedimiento: {procedimiento}\nTinta Lote: {lote_tinta} | Aguja Lote: {lote_aguja}")

        # SECCIÓN SALUD - Lógica de Negación Explícita
        pdf.chapter_title("II. DECLARACIÓN JURADA DE SALUD")
        salud_text = "El cliente declara BAJO JURAMENTO lo siguiente:\n"
        salud_text += "- NO se encuentra bajo efectos de alcohol o drogas.\n"
        salud_text += "- NO se encuentra en estado de embarazo ni periodo de lactancia.\n"
        salud_text += "- NO padece de enfermedades infectocontagiosas.\n"
        
        # Mapeo de enfermedades
        enfermedades = [
            (diabetes, "Diabetes"), (epilepsia, "Epilepsia"), 
            (corazon, "Cardiopatías"), (hemofilia, "Hemofilia"),
            (alergias, "Alergias"), (queloide, "Queloides"),
            (alergia_lido, "Alergia a la Lidocaína"), (afeccion_piel, "Afecciones de la piel")
        ]
        
        for estado, nombre_enf in enfermedades:
            if estado:
                salud_text += f"- SÍ PADECE de {nombre_enf}.\n"
            else:
                salud_text += f"- NO PADECE de {nombre_enf}.\n"
        
        salud_text += f"Notas adicionales: {detalles_medicos if detalles_medicos else 'Ninguna.'}"
        pdf.chapter_body(salud_text)

        # SECCIÓN COMPROMISO
        pdf.chapter_title("III. COMPROMISO, RIESGOS Y CUIDADOS")
        compromiso = (
            "1. El cliente DECLARA BAJO JURAMENTO que toda la información brindada es verídica.\n"
            "2. El cliente confirma que RECIBIÓ LAS INSTRUCCIONES y la Guía de Cuidados respectivos.\n"
            "3. El cliente ACEPTA LOS RIESGOS inherentes (infecciones, alergias, variaciones de pigmento).\n"
            "4. El cliente ratifica haber revisado y aprobado el diseño, ubicación y ortografía de la pieza."
        )
        pdf.chapter_body(compromiso, bold=True)
        pdf.chapter_body(f"Autorización de Imagen: {autoriza_imagen}")

        # FIRMA
        pdf.chapter_title("IV. RATIFICACIÓN DE FIRMA")
        pdf.ln(2)
        pdf.image(temp_firma, x=55, y=pdf.get_y(), w=100)
        pdf.ln(25)
        pdf.cell(0, 10, "_________________________________", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 5, f"Firma Digital del Cliente: {nombre}", align="C")

        # ANEXOS
        anexos_list = [
            (foto_diseno, "DISEÑO APROBADO"),
            (id_frente, "ID FRENTE"),
            (id_atras, "ID ATRÁS")
        ]
        if edad < 18 and permiso_padre:
            anexos_list.append((permiso_padre, "PERMISO TUTOR"))

        for archivo, titulo in anexos_list:
            if archivo:
                pdf.add_page()
                pdf.chapter_title(f"ANEXO: {titulo}")
                img = Image.open(archivo).convert('RGB')
                img.thumbnail((800, 800))
                t_name = f"temp_{titulo.replace(' ', '')}.jpg"
                img.save(t_name, "JPEG")
                archivos_temp.append(t_name)
                pdf.image(t_name, x=30, w=150)

        # GUARDADO
        os.makedirs("registros", exist_ok=True)
        pdf_path = f"registros/Declaracion_{cedula}_{datetime.now().strftime('%H%M%S')}.pdf"
        pdf.output(pdf_path)
        
        # BITÁCORA
        pd.DataFrame([{"Fecha": datetime.now(), "Nombre": nombre, "ID": cedula}]).to_csv(
            "registros/bitacora_legal.csv", mode='a', header=not os.path.exists("registros/bitacora_legal.csv"), index=False
        )

        st.success("✅ Documento Jurado Generado.")
        st.balloons()
        with open(pdf_path, "rb") as f:
            st.download_button("📥 DESCARGAR EXPEDIENTE LEGAL", f, file_name=f"Expediente_{nombre}.pdf")
        
        for f in archivos_temp:
            if os.path.exists(f): os.remove(f)
