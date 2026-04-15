import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import datetime
from fpdf import FPDF
from PIL import Image
import io
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz

# ==========================================
# MÓDULO 2: BACKEND - GENERACIÓN DE PDF
# ==========================================
class ConsentimientoPDF(FPDF):
    def header(self):
        # Membrete automático
        self.set_font("helvetica", "B", 16)
        self.cell(0, 10, "Fio Corrales Tattoo & Beauty Studio", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "I", 10)
        # Sello de tiempo (Hora de Costa Rica)
        cr_time = datetime.datetime.now(pytz.timezone('America/Costa_Rica')).strftime("%Y-%m-%d %H:%M:%S")
        self.cell(0, 10, f"Documento Legal Generado: {cr_time}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generar_pdf_legal(datos_cliente, firma_array, imgs_evidencia):
    pdf = ConsentimientoPDF()
    pdf.add_page()
    
    # 1. Datos del Cliente (Página 1)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "1. Datos del Cliente", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    
    # Tabla estilizada
    for key, value in datos_cliente.items():
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(50, 8, str(key) + ":", border=1)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(140, 8, str(value), border=1, new_x="LMARGIN", new_y="NEXT")
        
    pdf.ln(5)

    # 2. Consentimiento Legal
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "2. Declaración Jurada y Consentimiento Informado", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 9)
    texto_legal = (
        "Comprendo los riesgos de bioseguridad asociados al procedimiento de tatuaje/micropigmentación. "
        "Declaro bajo juramento que la información médica proporcionada es verídica y asumo la responsabilidad "
        "por cualquier omisión. Autorizo el uso de fotografías del procedimiento finalizado con fines de "
        "registro y portafolio profesional. En caso de dudas durante el proceso de sanación, me comprometo "
        "a contactar únicamente al canal oficial de Fio Corrales Tattoo & Beauty Studio: +506 62165089."
    )
    pdf.multi_cell(0, 5, texto_legal)
    pdf.ln(15)

    # 3. Firma del Cliente
    pdf.cell(0, 10, "Firma del Cliente:", new_x="LMARGIN", new_y="NEXT")
    
    # Procesar el array de la firma (Streamlit Canvas devuelve RGBA)
    if firma_array is not None:
        # Convertir array RGBA a imagen PIL, crear fondo blanco y pegar usando canal alfa
        img_canvas = Image.fromarray(firma_array.astype('uint8'), 'RGBA')
        fondo_blanco = Image.new("RGB", img_canvas.size, (255, 255, 255))
        fondo_blanco.paste(img_canvas, mask=img_canvas.split()[3]) # Usar alpha como máscara
        
        # Guardar en buffer de memoria
        firma_img_io = io.BytesIO()
        fondo_blanco.save(firma_img_io, format='PNG')
        
        # Insertar en PDF
        pdf.image(firma_img_io, x=60, y=pdf.get_y(), w=80)
        pdf.ln(40)
        pdf.line(60, pdf.get_y(), 140, pdf.get_y())

    # 4. Anexos y Evidencia (Página 2)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "3. Anexos y Evidencia Fotográfica", new_x="LMARGIN", new_y="NEXT")
    
    y_offset = pdf.get_y() + 5
    for nombre_archivo, archivo_subido in imgs_evidencia.items():
        if archivo_subido is not None:
            try:
                # Manejo robusto de la imagen
                img = Image.open(archivo_subido)
                img = img.convert('RGB') # Evitar problemas con PNGs transparentes
                
                # Ajustar tamaño para no deformar (max width 80, max height 80)
                img.thumbnail((80, 80))
                
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG')
                
                pdf.set_font("helvetica", "I", 10)
                pdf.cell(0, 10, f"Documento: {nombre_archivo}", new_x="LMARGIN", new_y="NEXT")
                pdf.image(img_io, x=20, y=pdf.get_y(), w=img.width*0.26, h=img.height*0.26) # 0.26 convierte px a mm aprox
                pdf.ln(90) # Espacio para la siguiente imagen
                
            except Exception as e:
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 10, f"Error al cargar la imagen {nombre_archivo}: {e}", new_x="LMARGIN", new_y="NEXT")

    # Retornar el PDF como bytes
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# MÓDULO 3: BASE DE DATOS Y AUTOMATIZACIÓN
# ==========================================
def guardar_en_sheets(datos_cliente, url_pdf_generado, url_carpeta_drive="N/A"):
    # Requiere que st.secrets contenga las credenciales de GCP:
    # [gcp_service_account]
    # type = "service_account"
    # project_id = "..."
    # etc...
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Usando credenciales inyectadas de forma segura desde los secretos de Streamlit
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Conectar con la hoja (Asegúrate de compartir el sheet con el correo de la cuenta de servicio)
        sheet = client.open("Registro_Clientes_FioCorrales").sheet1 
        
        timestamp = datetime.datetime.now(pytz.timezone('America/Costa_Rica')).strftime("%Y-%m-%d %H:%M:%S")
        
        fila = [
            timestamp,
            datos_cliente["Nombre"],
            datos_cliente["Cédula"],
            datos_cliente["WhatsApp"],
            datos_cliente["Precio Pactado (₡)"],
            url_carpeta_drive,
            url_pdf_generado
        ]
        
        sheet.append_row(fila)
        return True
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}. Verifique st.secrets.")
        return False

# SCRIPT EXTRA: Automatización de WhatsApp (Ejemplo comentado)
"""
import pywhatkit as kit
import time

def enviar_cuidados_posteriores(numero_cliente):
    # Formato requerido: +506XXXXXXXX
    mensaje = (
        "¡Hola! Gracias por confiar en Fio Corrales Tattoo & Beauty Studio. 🖤\n"
        "Recuerda seguir estas instrucciones de cuidados posteriores:\n"
        "1. Lava con jabón neutro.\n"
        "2. Aplica una capa fina de la crema recomendada.\n"
        "3. Evita el sol, piscinas y rascar la zona.\n"
        "Cualquier consulta, escríbenos por este medio: +506 62165089."
    )
    try:
        # Envía el mensaje instantáneamente (requiere tener WhatsApp Web abierto en el servidor/máquina)
        kit.sendwhatmsg_instantly(numero_cliente, mensaje, wait_time=15)
    except Exception as e:
        print(f"Error enviando WhatsApp: {e}")
"""

# ==========================================
# MÓDULO 1: INTERFAZ FRONTEND (Streamlit)
# ==========================================
st.set_page_config(page_title="Gestión de Expedientes | Fio Corrales", layout="centered")

# 1. Encabezado
st.markdown("<h1 style='text-align: center; color: #2E2E2E;'>Fio Corrales Tattoo & Beauty Studio</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #5E5E5E;'>Sistema de Expedientes y Consentimiento Informado</h4>", unsafe_allow_html=True)
st.divider()

# Inicializar variables de estado para validación
if 'pdf_generado' not in st.session_state:
    st.session_state.pdf_generado = False

# 2. Formulario de Cliente
st.subheader("📝 Datos del Cliente")
col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input("Nombre Completo *")
    cedula = st.text_input("Cédula (Formato CR: x-xxxx-xxxx) *")
    fecha_nacimiento = st.date_input("Fecha de Nacimiento *", min_value=datetime.date(1920, 1, 1))

with col2:
    whatsapp = st.text_input("WhatsApp *", value="+506 ", max_chars=13)
    zona_cuerpo = st.selectbox("Zona del Cuerpo *", ["Brazo", "Antebrazo", "Pierna", "Espalda", "Pecho", "Rostro (Micropigmentación)", "Otro"])
    precio = st.number_input("Precio Pactado (₡) *", min_value=0, step=1000)

# Validación de edad
edad = (datetime.date.today() - fecha_nacimiento).days // 365
if edad < 18:
    st.warning("El cliente es menor de edad. Se requiere autorización y presencia de un tutor legal.")

st.divider()

# 3. Cuestionario de Bioseguridad
st.subheader("🩸 Cuestionario de Bioseguridad")
enf_infecciosas = st.radio("¿Padece alguna enfermedad infectocontagiosa? *", ("Sí", "No"), index=1)
coagulacion = st.radio("¿Tiene problemas de coagulación o diabetes? *", ("Sí", "No"), index=1)
alergias = st.radio("¿Tiene alergias severas (tintas, látex, etc)? *", ("Sí", "No"), index=1)
embarazo = st.radio("¿Está en periodo de embarazo o lactancia? *", ("Sí", "No"), index=1)

st.divider()

# 4. Carga de Evidencia
st.subheader("📸 Evidencia Fotográfica")
foto_cedula = st.file_uploader("Foto de Cédula (Anverso y Reverso) *", type=["jpg", "png", "jpeg"])
foto_procedimiento = st.file_uploader("Foto del Procedimiento Finalizado *", type=["jpg", "png", "jpeg"])
permiso_menores = st.file_uploader("Permiso Legal para Menores (Si aplica)", type=["jpg", "png", "jpeg", "pdf"])

st.divider()

# 5. Consentimiento Legal
st.subheader("⚖️ Consentimiento Informado")
texto_legal_ui = """
*Al firmar este documento, declaro que:*
1. Comprendo los riesgos de bioseguridad asociados al procedimiento.
2. Toda la información médica proporcionada es verídica.
3. Autorizo el uso de fotografías del procedimiento finalizado con fines de portafolio.
4. Me comprometo a contactar **únicamente al canal oficial: +506 62165089** en caso de dudas sobre la sanación.
"""
st.info(texto_legal_ui)

# 6. Captura de Firma
st.write("**Firma del Cliente o Tutor Legal (Traza en el recuadro blanco):**")
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

# 7. Botón de Envío y Lógica Maestra
if st.button("Guardar Expediente y Generar PDF", type="primary", use_container_width=True):
    # Validaciones obligatorias
    errores = []
    if not nombre or not cedula or whatsapp == "+506 ": errores.append("Faltan datos personales.")
    if not foto_cedula or not foto_procedimiento: errores.append("Faltan fotografías de evidencia.")
    
    # Validar que se haya dibujado algo en el canvas
    firma_valida = False
    if canvas_result.image_data is not None:
        # Verifica si la imagen no está en blanco (todos los píxeles alpha en 0)
        if np.any(canvas_result.image_data[:, :, 3] > 0):
            firma_valida = True
            
    if not firma_valida:
        errores.append("Falta la firma del cliente.")

    if errores:
        for error in errores:
            st.error(f"⚠️ {error}")
    else:
        with st.spinner("Compilando expediente legal..."):
            # Empaquetar datos
            datos_dict = {
                "Nombre": nombre,
                "Cédula": cedula,
                "WhatsApp": whatsapp,
                "Edad": f"{edad} años",
                "Zona": zona_cuerpo,
                "Precio Pactado (₡)": f"₡ {precio:,}",
                "Infectocontagiosas": enf_infecciosas,
                "Problemas Coagulación": coagulacion,
                "Alergias": alergias,
                "Embarazo/Lactancia": embarazo
            }
            
            evidencias_dict = {
                "Identificación": foto_cedula,
                "Tatuaje/Micropigmentación": foto_procedimiento,
                "Permiso Menores": permiso_menores
            }

            # Ejecutar Motor Backend
            pdf_bytes = generar_pdf_legal(datos_dict, canvas_result.image_data, evidencias_dict)
            
            # (Opcional) Guardar en Sheets - Se comenta para evitar crash si no hay st.secrets configurado
            # url_generada_dummy = "https://drive.google.com/..." # Aquí iría la lógica de subida a Drive
            # guardar_en_sheets(datos_dict, url_generada_dummy)
            
            st.success("✅ Expediente generado y validado con éxito.")
            
            # Botón de descarga
            st.download_button(
                label="⬇️ Descargar Bitácora PDF",
                data=pdf_bytes,
                file_name=f"Expediente_{nombre.replace(' ', '_')}_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )
