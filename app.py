import streamlit as st
import numpy as np
from PIL import Image
from fpdf import FPDF
import io
import pytz
from datetime import datetime
import unicodedata
from streamlit_drawable_canvas import st_canvas

# ==========================================
# 1. FUNCIONES DE UTILIDAD Y SANITIZACIÓN
# ==========================================

def limpiar_texto(texto):
    """
    Limpia el texto de tildes, caracteres especiales, y la ñ para evitar
    que FPDF2 colapse por problemas de Unicode.
    """
    if not isinstance(texto, str):
        texto = str(texto)
    
    # Reemplazo estricto solicitado
    texto = texto.replace('₡', 'Colones')
    texto = texto.replace('ñ', 'n').replace('Ñ', 'N')
    
    # Eliminar tildes y diacríticos
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    
    return texto

# ==========================================
# 2. MOTOR BACKEND: CLASE Y GENERADOR PDF
# ==========================================

class PDFConsentimiento(FPDF):
    def header(self):
        # Membrete clínico y limpio
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'Fio Corrales Tattoo & Beauty Studio', border=False, ln=True, align='C')
        
        # Fecha y hora exacta de Costa Rica
        self.set_font('Helvetica', 'I', 10)
        cr_tz = pytz.timezone('America/Costa_Rica')
        fecha_actual = datetime.now(cr_tz).strftime('%d/%m/%Y %H:%M:%S')
        self.cell(0, 10, f'Fecha y Hora (CR): {fecha_actual}', border=False, ln=True, align='C')
        self.ln(5)

    def footer(self):
        # Número de página en el pie
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_pdf(datos, firma_array, fotos):
    """
    Genera el documento PDF procesando los datos sanitizados, la firma en RGBA
    y las imágenes adjuntas, devolviendo los bytes puros para Streamlit.
    """
    pdf = PDFConsentimiento()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PÁGINA 1: DATOS Y CUESTIONARIO ---
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'DATOS DEL CLIENTE', ln=True)
    pdf.set_font('Helvetica', '', 11)
    
    for key, value in datos['personales'].items():
        texto_limpio = limpiar_texto(f"{key}: {value}")
        pdf.multi_cell(0, 8, texto_limpio)
        
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'CUESTIONARIO DE SALUD', ln=True)
    pdf.set_font('Helvetica', '', 11)
    
    for key, value in datos['salud'].items():
        texto_limpio = limpiar_texto(f"{key}: {value}")
        pdf.multi_cell(0, 8, texto_limpio)

    # --- TEXTO LEGAL ---
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 11)
    texto_legal = (
        "Declaro que la informacion es veridica. Acepto los riesgos de bioseguridad "
        "y autorizo el uso de fotografias para portafolio. En caso de dudas, "
        "contactare al +506 62165089."
    )
    pdf.multi_cell(0, 6, texto_legal)
    
    # --- PROCESAMIENTO DE FIRMA (RGBA a RGB) ---
    pdf.ln(15)
    pdf.cell(0, 10, 'Firma del Cliente:', ln=True)
    
    try:
        # Extraer alpha y poner fondo blanco
        firma_img = Image.fromarray(firma_array.astype('uint8'), 'RGBA')
        fondo_blanco = Image.new("RGB", firma_img.size, (255, 255, 255))
        fondo_blanco.paste(firma_img, mask=firma_img.split()[3]) # Usar canal alpha como máscara
        
        # Guardar en memoria
        firma_io = io.BytesIO()
        fondo_blanco.save(firma_io, format='PNG')
        firma_io.seek(0)
        
        # Insertar en PDF (ancho 80mm)
        pdf.image(firma_io, w=80)
        pdf.cell(80, 0, '________________________________', ln=True)
    except Exception as e:
        pdf.cell(0, 10, f'[Error al procesar la firma: {str(e)}]', ln=True)

    # --- PÁGINAS ANEXAS: EVIDENCIA ---
    if fotos:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'ANEXOS: EVIDENCIA FOTOGRAFICA', ln=True)
        
        for nombre_foto, archivo in fotos.items():
            if archivo is not None:
                try:
                    # Redimensionamiento temporal para evitar desbordamiento A4
                    img = Image.open(archivo)
                    img.thumbnail((450, 450)) # Tamaño seguro
                    
                    # Convertir a RGB por si acaso (ej. PNG con transparencia o RGBA)
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                        
                    img_io = io.BytesIO()
                    img.save(img_io, format='JPEG')
                    img_io.seek(0)
                    
                    pdf.ln(5)
                    pdf.set_font('Helvetica', 'B', 11)
                    pdf.cell(0, 10, limpiar_texto(nombre_foto), ln=True)
                    pdf.image(img_io, w=100) # Ancho controlado
                    pdf.ln(5)
                except Exception as e:
                    pdf.set_font('Helvetica', '', 10)
                    pdf.cell(0, 10, f'[Error al procesar la imagen {nombre_foto}: {str(e)}]', ln=True)

    # Retorno estricto de bytes puro para Streamlit Download Button
    return bytes(pdf.output())

# ==========================================
# 3. INTERFAZ FRONTEND (STREAMLIT)
# ==========================================

st.set_page_config(page_title="Consentimiento - Fio Corrales", layout="centered")

# Encabezado Clínico
st.markdown("<h1 style='text-align: center; color: #2C3E50;'>Fio Corrales Tattoo & Beauty Studio</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #7F8C8D;'>Expediente y Consentimiento Informado</h4>", unsafe_allow_html=True)
st.divider()

# Formulario de Datos Personales (2 Columnas)
st.subheader("Datos Personales")
col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input("Nombre completo")
    cedula = st.text_input("Cédula / ID")
    fecha_nac = st.date_input("Fecha de nacimiento")

with col2:
    whatsapp = st.text_input("WhatsApp (+506)")
    zona_tatuar = st.text_input("Zona a tatuar / trabajar")
    precio = st.text_input("Precio Pactado (₡)")

st.divider()

# Cuestionario de Salud
st.subheader("Cuestionario de Salud")
c1, c2 = st.columns(2)
with c1:
    enf_infecto = st.radio("¿Padece enfermedades infectocontagiosas?", ["No", "Sí"])
    coagulacion = st.radio("¿Problemas de coagulación o diabetes?", ["No", "Sí"])
with c2:
    alergias = st.radio("¿Alergias severas (látex, tintas, anestesia)?", ["No", "Sí"])
    embarazo = st.radio("¿Embarazo o lactancia?", ["No", "Sí"])

st.divider()

# Módulos de Carga de Archivos
st.subheader("Evidencia Fotográfica")
st.caption("Formatos aceptados: JPG, JPEG, PNG")
foto_frente = st.file_uploader("1. Frente de la Cédula (Obligatorio)", type=["jpg", "jpeg", "png"])
foto_dorso = st.file_uploader("2. Dorso de la Cédula (Obligatorio)", type=["jpg", "jpeg", "png"])
foto_trabajo = st.file_uploader("3. Trabajo Finalizado (Obligatorio)", type=["jpg", "jpeg", "png"])
foto_menor = st.file_uploader("4. Permiso de menores (Opcional)", type=["jpg", "jpeg", "png"])

st.divider()

# Firma Digital
st.subheader("Firma del Cliente")
st.caption("Dibuje su firma en el recuadro blanco:")
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 1)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=150,
    drawing_mode="freedraw",
    key="canvas",
)

st.divider()

# ==========================================
# 4. LÓGICA DE VALIDACIÓN Y GENERACIÓN
# ==========================================

if st.button("Generar Expediente PDF", use_container_width=True, type="primary"):
    
    # 1. Validar campos obligatorios de texto
    if not all([nombre, cedula, whatsapp, zona_tatuar, precio]):
        st.error("⚠️ Por favor, complete todos los campos de texto obligatorios.")
    
    # 2. Validar fotos obligatorias
    elif not all([foto_frente, foto_dorso, foto_trabajo]):
        st.error("⚠️ Faltan fotografías obligatorias (Cédula frente/dorso o Trabajo finalizado).")
    
    # 3. Validar firma (Comprobar si el array está vacío o si todos los pixeles son 0)
    elif canvas_result.image_data is None or np.sum(canvas_result.image_data) == 0:
        st.error("⚠️ La firma es obligatoria.")
        
    else:
        with st.spinner("Procesando documento..."):
            # Construir diccionarios
            datos_generales = {
                "personales": {
                    "Nombre": nombre,
                    "Cedula": cedula,
                    "Fecha de Nacimiento": str(fecha_nac),
                    "WhatsApp": whatsapp,
                    "Zona": zona_tatuar,
                    "Precio": precio
                },
                "salud": {
                    "Enfermedades infectocontagiosas": enf_infecto,
                    "Problemas coagulacion/diabetes": coagulacion,
                    "Alergias": alergias,
                    "Embarazo/lactancia": embarazo
                }
            }
            
            diccionario_fotos = {
                "Frente de la Cedula": foto_frente,
                "Dorso de la Cedula": foto_dorso,
                "Trabajo Finalizado": foto_trabajo,
                "Permiso de Menores": foto_menor # Puede ser None
            }
            
            # Invocar al motor backend
            try:
                pdf_bytes = generar_pdf(
                    datos=datos_generales,
                    firma_array=canvas_result.image_data,
                    fotos=diccionario_fotos
                )
                
                st.success("✅ ¡Expediente generado con éxito!")
                
                # Descarga sin errores (retorna bytes crudos)
                st.download_button(
                    label="📥 Descargar PDF Legal",
                    data=pdf_bytes,
                    file_name=f"Expediente_{nombre.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
            except Exception as e:
                st.error(f"❌ Error crítico al generar el PDF: {str(e)}")

