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
# CONFIGURACIÓN Y FUNCIONES DE SEGURIDAD
# ==========================================
st.set_page_config(page_title="Expedientes | Fio Corrales", layout="centered", page_icon="🖋️")

def limpiar_texto(texto):
    """
    Motor de sanitización. Elimina caracteres que FPDF no soporta
    por defecto, evitando el error UnicodeEncodingException.
    """
    if texto is None:
        return ""
    reemplazos = {
        'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u',
        'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U',
        'ñ':'n', 'Ñ':'N', '₡':'Colones'
    }
    texto_limpio = str(texto)
    for orig, nuevo in reemplazos.items():
        texto_limpio = texto_limpio.replace(orig, nuevo)
    return texto_limpio

# ==========================================
# MOTOR BACKEND - GENERADOR DE PDF
# ==========================================
class ExpedientePDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 16)
        self.cell(0, 10, "Fio Corrales Tattoo & Beauty Studio", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "I", 10)
        # Sello de tiempo automático en zona horaria de Costa Rica
        fecha_cr = datetime.datetime.now(pytz.timezone('America/Costa_Rica')).strftime("%Y-%m-%d %H:%M")
        self.cell(0, 10, f"Expediente Oficial - Generado: {fecha_cr}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

def generar_pdf_pro(datos, firma_array, fotos):
    pdf = ExpedientePDF()
    pdf.add_page()
    
    # 1. Datos Personales
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "1. DATOS DEL CLIENTE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    
    for key, value in datos.items():
        k_clean = limpiar_texto(key)
        v_clean = limpiar_texto(value)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(55, 8, f"{k_clean}:", border=1)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(135, 8, f"{v_clean}", border=1, new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)

    # 2. Consentimiento Informado Legal
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "2. CONSENTIMIENTO Y DECLARACION JURADA", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    texto_legal = limpiar_texto(
        "Declaro bajo juramento que la información medica proporcionada es veridica. "
        "Comprendo los riesgos de bioseguridad asociados al procedimiento de tatuaje o micropigmentación. "
        "Asumo la responsabilidad del cuidado posterior indicado por la artista. "
        "Autorizo el uso de fotografías del procedimiento finalizado con fines de registro y portafolio profesional. "
        "En caso de dudas durante la sanación, contactare unicamente al canal oficial: +506 62165089."
    )
    pdf.multi_cell(0, 5, texto_legal)
    pdf.ln(10)

    # 3. Firma
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "3. FIRMA DEL CLIENTE", new_x="LMARGIN", new_y="NEXT")
    
    if firma_array is not None and np.any(firma_array[:, :, 3] > 0):
        img_canvas = Image.fromarray(firma_array.astype('uint8'), 'RGBA')
        fondo_blanco = Image.new("RGB", img_canvas.size, (255, 255, 255))
        fondo_blanco.paste(img_canvas, mask=img_canvas.split()[3])
        firma_io = io.BytesIO()
        fondo_blanco.save(firma_io, format='PNG')
        pdf.image(firma_io, x=65, w=80)
        pdf.ln(2)
    else:
        pdf.ln(25) # Espacio si falla la carga visual
        
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 5, "__________________________________________________", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, limpiar_texto(datos["Nombre Completo"]), align="C", new_x="LMARGIN", new_y="NEXT")

    # 4. Anexos Fotográficos (Página 2 y 3)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "4. ANEXOS FOTOGRAFICOS", new_x="LMARGIN", new_y="NEXT")
    
    for titulo, archivo in fotos.items():
        if archivo is not None:
            try:
                img = Image.open(archivo).convert('RGB')
                # Optimización para que ninguna imagen desborde el PDF
                img.thumbnail((350, 350))
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG')
                
                pdf.ln(5)
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 8, limpiar_texto(titulo), new_x="LMARGIN", new_y="NEXT")
                pdf.image(img_io, x=20, w=80)
                pdf.ln(80) # Salto de línea para la siguiente imagen
                
                # Si llega muy abajo, crea una nueva página automáticamente
                if pdf.get_y() > 220:
                    pdf.add_page()
            except Exception as e:
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 10, f"Error al cargar {limpiar_texto(titulo)}", new_x="LMARGIN", new_y="NEXT")

    # Retorno en modo binario
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# INTERFAZ FRONTEND - STREAMLIT
# ==========================================

st.markdown("<h1 style='text-align: center;'>Fio Corrales Tattoo & Beauty Studio</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Sistema Profesional de Expedientes</h4>", unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre Completo *")
    cedula = st.text_input("Cédula de Identidad *", placeholder="Ej: 2-0123-0456")
    edad = st.number_input("Edad *", min_value=15, max_value=100, value=18)
with col2:
    whatsapp = st.text_input("WhatsApp *", value="+506 ")
    zona = st.text_input("Zona a tatuar / Procedimiento *")
    precio = st.text_input("Precio Pactado *", placeholder="Ej: 35000")

st.subheader("🩸 Cuestionario Médico")
c1, c2 = st.columns(2)
with c1:
    enf = st.radio("¿Enfermedades infectocontagiosas?", ["No", "Sí"])
    coag = st.radio("¿Problemas de coagulación o diabetes?", ["No", "Sí"])
with c2:
    alergias = st.radio("¿Alergias severas (látex, tintas)?", ["No", "Sí"])
    emb = st.radio("¿Embarazo o lactancia?", ["No", "Sí"])

st.subheader("📸 Archivos Adjuntos")
st.info("Sube las fotografías. El sistema ajustará sus tamaños automáticamente.")
f_frente = st.file_uploader("1. Frente de la Cédula *", type=['jpg','png','jpeg'])
f_atras = st.file_uploader("2. Dorso de la Cédula *", type=['jpg','png','jpeg'])
f_tattoo = st.file_uploader("3. Foto del Trabajo Finalizado *", type=['jpg','png','jpeg'])
f_permiso = st.file_uploader("4. Permiso de Menores (Solo si aplica)", type=['jpg','png','jpeg', 'pdf'])

st.subheader("⚖️ Firma Digital")
st.write("Firma dentro del recuadro blanco:")
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 1)",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=150,
    drawing_mode="freedraw",
    key="canvas",
)

st.divider()

if st.button("Guardar y Generar Expediente PDF", type="primary", use_container_width=True):
    # Validaciones estrictas de "Pro Mode"
    faltan_datos = not nombre or not cedula or not precio or not zona
    faltan_fotos = not f_frente or not f_atras or not f_tattoo
    falta_firma = canvas_result.image_data is None or not np.any(canvas_result.image_data[:, :, 3] > 0)

    if faltan_datos:
        st.error("⚠️ Faltan datos personales obligatorios en el formulario.")
    elif faltan_fotos:
        st.error("⚠️ Debes subir obligatoriamente el frente de la cédula, el dorso y la foto del trabajo.")
    elif falta_firma:
        st.error("⚠️ El cliente debe trazar su firma en el recuadro blanco.")
    else:
        with st.spinner("Compilando expediente inalterable..."):
            datos_dict = {
                "Nombre Completo": nombre,
                "Cédula": cedula,
                "Edad": f"{edad} años",
                "WhatsApp": whatsapp,
                "Procedimiento": zona,
                "Precio Pactado": f"Colones {precio}",
                "Enfermedades": enf,
                "Coagulación o Diabetes": coag,
                "Alergias": alergias,
                "Embarazo o Lactancia": emb
            }
            
            fotos_dict = {
                "Cédula (Frente)": f_frente,
                "Cédula (Dorso)": f_atras,
                "Trabajo Acordado": f_tattoo,
                "Permiso Legal de Menores": f_permiso
            }

            try:
                pdf_final = generar_pdf_pro(datos_dict, canvas_result.image_data, fotos_dict)
                st.success("✅ ¡Expediente compilado con éxito!")
                st.download_button(
                    label="⬇️ Descargar Expediente Legal (PDF)",
                    data=pdf_final,
                    file_name=f"Expediente_{nombre.replace(' ', '_')}_{datetime.date.today()}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error interno al compilar el PDF: {e}")
