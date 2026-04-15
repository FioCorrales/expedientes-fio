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

# --- ESTILOS CSS PRO ---
st.markdown("""
    <style>
    .main { background-color: #121212; color: #E0E0E0; }
    h1, h2, h3 { color: #D4AF37; font-family: 'Helvetica Neue', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #1E1E1E; border-radius: 4px 4px 0px 0px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #D4AF37; color: black !important; font-weight: bold; }
    div[data-testid="stForm"] { border: 1px solid #D4AF37; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CLASE PDF PERSONALIZADA ---
class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 16)
        self.cell(0, 10, "Fio Corrales Tattoo & Beauty Studio", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 10)
        self.cell(0, 6, "Ciudad Quesada, Costa Rica | +506 62165089", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "CONSENTIMIENTO INFORMADO PARA PROCEDIMIENTOS ESTÉTICOS", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 11)
        self.set_fill_color(200, 200, 200)
        self.cell(0, 8, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def chapter_body(self, text):
        self.set_font("helvetica", "", 10)
        self.multi_cell(0, 5, text)
        self.ln(3)

# --- CABECERA ---
st.title("✒️ Plataforma de Registro Legal")
st.write("Registro Digital y Consentimiento Informado.")

# --- FORMULARIO MULTI-PESTAÑA ---
with st.form("registro_maestro"):
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Datos", "⚕️ Salud", "📎 Archivos", "⚖️ Legal & Firma"])

    # PESTAÑA 1: DATOS PERSONALES
    with tab1:
        st.subheader("Datos del Cliente")
        nombre = st.text_input("Nombre Completo *")
        col1, col2 = st.columns(2)
        with col1:
            cedula = st.text_input("Cédula / Pasaporte *")
            telefono = st.text_input("Teléfono *")
        with col2:
            edad = st.number_input("Edad *", min_value=15, max_value=100, step=1)
            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
            st.text_input("Fecha", value=fecha_hoy, disabled=True)
        
        procedimiento = st.selectbox("Procedimiento a realizar:", 
            ["Tatuaje", "Piercing", "Microblading/Cejas", "Delineado Ojos", "Labios"])
        
        st.subheader("Datos de Trazabilidad (Uso Interno)")
        col3, col4 = st.columns(2)
        with col3:
            lote_tinta = st.text_input("Lote/Marca de Pigmento")
        with col4:
            lote_aguja = st.text_input("Lote de Aguja")

    # PESTAÑA 2: CUESTIONARIO MÉDICO
    with tab2:
        st.subheader("Declaración de Salud y Aptitud")
        st.info("Debe confirmar que NO posee las siguientes condiciones:")
        cond_1 = st.checkbox("NO estoy bajo efectos de alcohol o drogas. *")
        cond_2 = st.checkbox("NO padezco enfermedades infectocontagiosas. *")
        cond_3 = st.checkbox("NO estoy embarazada ni lactando. *")

        st.markdown("---")
        st.write("**Marque si padece o ha padecido lo siguiente:**")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            diabetes = st.checkbox("Diabetes")
            epilepsia = st.checkbox("Epilepsia")
            corazon = st.checkbox("Problemas cardíacos")
            hemofilia = st.checkbox("Hemofilia")
        with col_m2:
            alergias = st.checkbox("Alergias (Látex/Pigmentos)")
            queloide = st.checkbox("Cicatrización queloide")
            piel = st.checkbox("Afecciones de la piel")
        
        detalles_medicos = st.text_area("Notas médicas adicionales")

    # PESTAÑA 3: ARCHIVOS
    with tab3:
        st.subheader("Documentación Visual")
        foto_diseno = st.file_uploader("Diseño de referencia", type=["jpg", "png"])
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            id_frente = st.file_uploader("Cédula - Frente *", type=["jpg", "png"])
        with col_f2:
            id_atras = st.file_uploader("Cédula - Atrás *", type=["jpg", "png"])

        if edad < 18:
            permiso_padre = st.file_uploader("Permiso del Tutor (PDF/Imagen) *", type=["jpg", "png", "pdf"])

    # PESTAÑA 4: LEGAL Y FIRMA DIGITAL
    with tab4:
        st.subheader("Consentimiento y Firma")
        st.write("Certifico que he revisado el diseño y acepto los riesgos del procedimiento.")
        autoriza_imagen = st.radio("Autorización de Imagen:", ["Sí autorizo", "NO autorizo"], horizontal=True)
        
        # --- COMPONENTE DE FIRMA ---
        st.write("**Firme en el recuadro de abajo:**")
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0.3)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=150,
            width=400,
            drawing_mode="freedraw",
            key="canvas",
        )
        st.caption("Use su dedo o lápiz óptico para firmar.")
        
        acepta_terminos = st.checkbox("Confirmo que he leído y acepto los términos. *")
        submit_btn = st.form_submit_button("VALIDAR Y GENERAR DOCUMENTO")

# --- PROCESAMIENTO ---
if submit_btn:
    if not nombre or not cedula or not acepta_terminos or canvas_result.image_data is None:
        st.error("❌ Por favor complete los campos obligatorios y firme el documento.")
    else:
        # 1. Procesar la Firma
        firma_array = canvas_result.image_data
        firma_image = Image.fromarray(firma_array.astype('uint8'), 'RGBA')
        
        # 2. Generar PDF
        pdf = PDF()
        pdf.add_page()
        
        pdf.chapter_title("DATOS DEL CLIENTE")
        pdf.chapter_body(f"Nombre: {nombre}\nCédula: {cedula}\nTeléfono: {telefono}\nEdad: {edad}\nProcedimiento: {procedimiento}")
        
        pdf.chapter_title("I. SALUD")
        pdf.chapter_body(f"Condiciones reportadas: {'Diabetes ' if diabetes else ''}{'Epilepsia ' if epilepsia else ''}{'Alergias' if alergias else ''}\nNotas: {detalles_medicos}")

        pdf.chapter_title("II. RIESGOS Y CUIDADOS")
        pdf.chapter_body("El cliente acepta los riesgos permanentes y se compromete a seguir la Guía de Cuidados proporcionada.")

        pdf.chapter_title("III. AUTORIZACIÓN DE IMAGEN")
        pdf.chapter_body(f"Consentimiento para redes sociales: {autoriza_imagen}")

        # IV. ESPACIO DE FIRMA
        pdf.chapter_title("IV. FIRMA DIGITAL")
        pdf.ln(5)
        
        # Guardar firma temporalmente para insertarla en el PDF
        temp_firma = "temp_firma.png"
        firma_image.save(temp_firma)
        
        # Posicionar la imagen de la firma sobre la línea
        pdf.image(temp_firma, x=55, y=pdf.get_y(), w=100)
        pdf.ln(25)
        pdf.cell(0, 10, "_________________________________", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 5, f"Firma Digital de {nombre}", align="C")

        # Guardar y Registrar
        os.makedirs("registros", exist_ok=True)
        pdf_filename = f"registros/Consentimiento_{cedula}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
        pdf.output(pdf_filename)
        
        # Registrar en CSV
        nueva_fila = {"Fecha": datetime.now(), "Cédula": cedula, "Nombre": nombre, "Archivo": pdf_filename}
        pd.DataFrame([nueva_fila]).to_csv("registros/bitacora.csv", mode='a', header=not os.path.exists("registros/bitacora.csv"), index=False)

        st.success("✅ Documento generado con firma digital.")
        with open(pdf_filename, "rb") as f:
            st.download_button("📥 Descargar PDF Firmado", f, file_name=f"Consentimiento_{nombre}.pdf")
        
        # Limpiar archivo temporal
        if os.path.exists(temp_firma):
            os.remove(temp_firma)
