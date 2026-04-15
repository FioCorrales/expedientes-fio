import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import os
from PIL import Image
import io

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
st.write("Complete el formulario. Los datos se encriptarán en la bitácora del estudio.")

# --- FORMULARIO MULTI-PESTAÑA ---
with st.form("registro_maestro"):
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Datos", "⚕️ Salud", "📎 Archivos", "⚖️ Legal"])

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
        st.info("Debe marcar las casillas para confirmar que NO posee las siguientes condiciones limitantes:")
        cond_1 = st.checkbox("NO me encuentro bajo los efectos del alcohol, drogas, ni sustancias psicotrópicas. *")
        cond_2 = st.checkbox("NO padezco de enfermedades infectocontagiosas no notificadas. *")
        cond_3 = st.checkbox("NO estoy embarazada ni en periodo de lactancia. *")

        st.markdown("---")
        st.write("**Marque si padece o ha padecido lo siguiente:**")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            diabetes = st.checkbox("Diabetes")
            epilepsia = st.checkbox("Epilepsia")
            corazon = st.checkbox("Problemas cardíacos")
            hemofilia = st.checkbox("Hemofilia / Problemas coagulación")
        with col_m2:
            alergias = st.checkbox("Alergias a metales, látex o pigmentos")
            queloide = st.checkbox("Cicatrización queloide")
            piel = st.checkbox("Afecciones de la piel en la zona")
        
        detalles_medicos = st.text_area("Detalles adicionales sobre su salud (Opcional)")

    # PESTAÑA 3: ARCHIVOS Y EVIDENCIA
    with tab3:
        st.subheader("Carga de Documentación")
        st.write("Formatos permitidos: JPG, PNG.")
        foto_diseno = st.file_uploader("Diseño / Referencia a realizar", type=["jpg", "jpeg", "png"])
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            id_frente = st.file_uploader("Cédula - Frente *", type=["jpg", "jpeg", "png"])
        with col_f2:
            id_atras = st.file_uploader("Cédula - Atrás *", type=["jpg", "jpeg", "png"])

        if edad < 18:
            st.error("⚠️ REQUISITO PARA MENORES DE EDAD")
            permiso_padre = st.file_uploader("Cédula y Permiso Firmado del Padre/Tutor *", type=["jpg", "jpeg", "png"])

    # PESTAÑA 4: LEGAL Y FIRMA
    with tab4:
        st.subheader("Consentimiento y Aprobación")
        st.write("He revisado y aprobado el diseño, tamaño, ortografía (en caso de letras) y ubicación de la pieza.")
        st.write("Certifico que he recibido la Guía de Cuidados y me comprometo a seguirla.")
        
        autoriza_imagen = st.radio("Autorización de Imagen (Redes Sociales):", ["Sí autorizo", "NO autorizo"], horizontal=True)
        acepta_terminos = st.checkbox("Confirmo que he leído y comprendido toda la información, y acepto los riesgos. *")
        
        submit_btn = st.form_submit_button("VALIDAR Y GENERAR DOCUMENTO OFICIAL")

# --- LÓGICA DE PROCESAMIENTO ---
if submit_btn:
    # Validaciones Estrictas
    faltan_datos = not nombre or not cedula or not telefono
    faltan_checks = not cond_1 or not cond_2 or not cond_3 or not acepta_terminos
    faltan_fotos = not id_frente or not id_atras
    es_menor_sin_permiso = edad < 18 and not permiso_padre

    if faltan_datos:
        st.error("❌ Faltan datos personales obligatorios (*).")
    elif faltan_checks:
        st.error("❌ Debe aceptar las condiciones de salud y los términos legales (*).")
    elif faltan_fotos:
        st.error("❌ Es obligatorio subir las fotografías de la cédula.")
    elif es_menor_sin_permiso:
        st.error("❌ Los menores de edad requieren el documento de permiso del tutor.")
    else:
        # Generación del PDF Exacto al Original
        pdf = PDF()
        pdf.add_page()
        
        # DATOS
        pdf.chapter_title("DATOS DEL CLIENTE")
        pdf.chapter_body(f"Nombre Completo: {nombre}\nCédula / Pasaporte: {cedula}\nTeléfono: {telefono}\nEdad: {edad} años\nFecha: {fecha_hoy}\nProcedimiento: {procedimiento}")
        
        # I. SALUD
        pdf.chapter_title("I. DECLARACIÓN DE SALUD Y APTITUD")
        padecimientos = []
        if diabetes: padecimientos.append("Diabetes")
        if epilepsia: padecimientos.append("Epilepsia")
        if corazon: padecimientos.append("Problemas Cardíacos")
        if hemofilia: padecimientos.append("Hemofilia/Coagulación")
        if alergias: padecimientos.append("Alergias (metales/pigmentos)")
        if queloide: padecimientos.append("Cicatrización Queloide")
        if piel: padecimientos.append("Afecciones de piel")
        
        pad_str = ", ".join(padecimientos) if padecimientos else "Ninguno reportado."
        
        pdf.chapter_body(
            "Declaro bajo juramento que:\n"
            "1. NO me encuentro bajo efectos de alcohol, drogas ni sustancias psicotrópicas.\n"
            "2. NO padezco enfermedades infectocontagiosas no notificadas.\n"
            "3. NO estoy embarazada ni en periodo de lactancia.\n"
            f"Padecimientos marcados: {pad_str}\n"
            f"Detalles adicionales: {detalles_medicos}"
        )

        # II. RIESGOS
        pdf.chapter_title("II. INFORMACIÓN SOBRE EL PROCEDIMIENTO Y RIESGOS")
        pdf.chapter_body(
            "Entiendo que el procedimiento es una modificación permanente. Implica el uso de agujas estériles "
            "y desechables, conllevando un riesgo mínimo de infección si no se siguen los cuidados. "
            "Existe posibilidad de reacciones alérgicas a pigmentos o materiales. "
            "He revisado y aprobado el diseño, tamaño, ortografía y ubicación antes de iniciar."
        )

        # III. CUIDADOS
        pdf.chapter_title("III. COMPROMISO DE CUIDADOS POSTERIORES")
        pdf.chapter_body(
            "Certifico que he recibido la Guía de Cuidados y me comprometo a seguir las instrucciones al pie de la letra. "
            "Entiendo que la mala manipulación exonera al estudio de cualquier responsabilidad."
        )

        # IV. IMAGEN
        pdf.chapter_title("IV. AUTORIZACIÓN DE IMAGEN")
        pdf.chapter_body(f"Uso de material para redes sociales y portafolio: {autoriza_imagen}")

        # V. FIRMAS
        pdf.chapter_title("V. FIRMAS DE CONFORMIDAD")
        pdf.ln(15)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(90, 10, "_________________________________", align="C")
        pdf.cell(90, 10, "_________________________________", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(90, 5, "Firma del Cliente", align="C")
        pdf.cell(90, 5, "Firma del Artista / Técnico", align="C", new_x="LMARGIN", new_y="NEXT")
        
        # Guardar Documento
        os.makedirs("registros", exist_ok=True)
        pdf_filename = f"registros/Consentimiento_{cedula}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
        pdf.output(pdf_filename)

        # Registro en Bitácora (Base de datos CSV)
        nueva_fila = {
            "Fecha": fecha_hoy,
            "Cédula": cedula,
            "Nombre": nombre,
            "Procedimiento": procedimiento,
            "Lote Tinta": lote_tinta,
            "Lote Aguja": lote_aguja,
            "Autoriza Imagen": autoriza_imagen,
            "Archivo PDF": pdf_filename
        }
        df_nueva = pd.DataFrame([nueva_fila])
        archivo_csv = "registros/bitacora_sanitaria.csv"
        
        if not os.path.exists(archivo_csv):
            df_nueva.to_csv(archivo_csv, index=False, encoding='utf-8')
        else:
            df_nueva.to_csv(archivo_csv, mode='a', header=False, index=False, encoding='utf-8')

        st.success("✅ Registro completado exitosamente. Cumplimiento normativo alcanzado.")
        st.balloons()
        
        # Botón para descargar el PDF
        with open(pdf_filename, "rb") as f:
            st.download_button("📥 Descargar Consentimiento Oficial", f, file_name=f"Consentimiento_{nombre}.pdf", mime="application/pdf")
