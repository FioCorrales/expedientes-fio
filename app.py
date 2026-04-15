import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import datetime
from fpdf import FPDF
from PIL import Image
import io
import numpy as np
import pytz

# ==========================================
# CONFIGURACIÓN Y UTILIDADES PRO
# ==========================================
st.set_page_config(page_title="Gestión de Expedientes | Fio Corrales", layout="centered")

def limpiar_texto(texto):
    """Limpia tildes y símbolos para evitar errores en el PDF básico."""
    if texto is None: return ""
    reemplazos = {
        'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u',
        'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U',
        'ñ':'n', 'Ñ':'N', '₡':'Colones'
    }
    t = str(texto)
    for orig, nuevo in reemplazos.items():
        t = t.replace(orig, nuevo)
    return t

# ==========================================
# MOTOR BACKEND - GENERACIÓN DE PDF (ESTILO CLÍNICO)
# ==========================================
class ConsentimientoPDF(FPDF):
    def header(self):
        # Membrete profesional del estudio
        self.set_font("helvetica", "B", 16)
        self.cell(0, 10, "Fio Corrales Tattoo & Beauty Studio", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "I", 10)
        # Hora exacta de Costa Rica
        fecha_cr = datetime.datetime.now(pytz.timezone('America/Costa_Rica')).strftime("%Y-%m-%d %H:%M:%S")
        self.cell(0, 10, f"Bitacora de Bioseguridad - Generada: {fecha_cr}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

def generar_pdf_legal(datos_cliente, firma_array, imgs_evidencia):
    pdf = ConsentimientoPDF()
    pdf.add_page()
    
    # 1. Tabla de Datos del Cliente
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "1. INFORMACION GENERAL", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    
    for key, value in datos_cliente.items():
        k = limpiar_texto(key)
        v = limpiar_texto(value)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(50, 8, f"{k}:", border=1)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(140, 8, f"{v}", border=1, new_x="LMARGIN", new_y="NEXT")
        
    pdf.ln(5)

    # 2. Consentimiento Legal
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "2. DECLARACION JURADA Y CONSENTIMIENTO", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 9)
    # Texto legal fijo sanitizado
    texto_legal = (
        "Comprendo los riesgos de bioseguridad asociados al procedimiento. Declaro que la informacion "
        "medica brindada es real. Autorizo el uso de imagen para portafolio profesional. En caso de dudas "
        "durante la sanacion, contactare al canal oficial del estudio: +506 62165089."
    )
    pdf.multi_cell(0, 5, texto_legal)
    pdf.ln(10)

    # 3. Firma con procesamiento de canal alfa
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 10, "FIRMA DEL CLIENTE:", new_x="LMARGIN", new_y="NEXT")
    if firma_array is not None and np.any(firma_array[:, :, 3] > 0):
        img_canvas = Image.fromarray(firma_array.astype('uint8'), 'RGBA')
        fondo_blanco = Image.new("RGB", img_canvas.size, (255, 255, 255))
        fondo_blanco.paste(img_canvas, mask=img_canvas.split()[3])
        firma_io = io.BytesIO()
        fondo_blanco.save(firma_io, format='PNG')
        pdf.image(firma_io, x=60, w=80)
        pdf.ln(2)
    
    pdf.cell(0, 5, "________________________________________", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, limpiar_texto(datos_cliente["Nombre"]), align="C", new_x="LMARGIN", new_y="NEXT")

    # 4. Anexos y Evidencia (Páginas extra)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "3. ANEXOS Y EVIDENCIA FOTOGRAFICA", new_x="LMARGIN", new_y="NEXT")
    
    for titulo, archivo in imgs_evidencia.items():
        if archivo is not None:
            try:
                img = Image.open(archivo).convert('RGB')
                img.thumbnail((400, 400))
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG')
                pdf.ln(5)
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 10, f"Documento: {limpiar_texto(titulo)}", new_x="LMARGIN", new_y="NEXT")
                pdf.image(img_io, x=20, w=100)
                pdf.ln(100)
                if pdf.get_y() > 200: pdf.add_page()
            except:
                pass

    return bytes(pdf.output())

# ==========================================
# INTERFAZ FRONTEND (STREAMLIT)
# ==========================================
# Usamos session_state para mantener la persistencia de la App
if 'guardado' not in st.session_state:
    st.session_state.guardado = False

st.markdown("<h1 style='text-align: center; color: #1E1E1E;'>Fio Corrales Tattoo & Beauty Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Gesti&oacute;n de Expedientes y Consentimiento Informado</p>", unsafe_allow_html=True)
st.divider()

# Formulario de Cliente
st.subheader("📝 Datos del Cliente
