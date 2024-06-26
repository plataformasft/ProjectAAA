# PageOne contents
import streamlit as st
import smtplib
from email.message import EmailMessage
import streamlit as stm

stm.title("Página de instrucciones 💡")
stm.header("Protocolo")
stm.markdown("1. Registrar las pruebas con el detalle de empresa, dieta y tratamiento \n"
             "2. Para revisar la disponibilidad de salas, ir a la sección correspondiente\n"
             "3. Para visualizar los datos en tabla estructurada, revisar sección Dashboard\n"
             "4. Para revisar gráfico Gantt, ingresar a la sección Dashboard \n"
             "5. De tener inconvenientes, contactarse con bdonayred@vitapro.com.pe \n")

stm.sidebar.success("Estas revisando las instrucciones")

# Formulario para enviar quejas por correo

import streamlit as st
from email.message import EmailMessage



# Formulario para enviar quejas por correo
import streamlit as st
from email.message import EmailMessage
import smtplib

with st.form("form_quejas"):
    st.write("Envía tu queja:")
    nombre_remitente = st.text_input("Nombre del Remitente:")  # Campo para el nombre del remitente
    correo_remitente = st.text_input("Correo corporativo:")  # Campo para el nombre del remitente
    mensaje_queja = st.text_area("Escribe tu mensaje aquí...")
    submit_button = st.form_submit_button("Enviar Queja")

    if submit_button:
        # Formatear el contenido del correo con el nombre del remitente
        contenido_email = f"Queja enviada por: {nombre_remitente}, con correo {correo_remitente}\n\n{mensaje_queja}"
        
        email = EmailMessage()
        email.set_content(contenido_email)
        email['Subject'] = 'Queja desde la aplicación Streamlit'
        email['From'] = f"{nombre_remitente} <brunodonayredonayre@gmail.com>"  # Incluye el nombre del remitente en el campo From
        email['To'] = 'bdonayred@vitapro.com.pe'

        try:
            # Configura aquí tu servidor SMTP y tus credenciales
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login('brunodonayredonayre@gmail.com', 'vjgksshxutcjydod')  # Asegúrate de que la contraseña de aplicación no tenga espacios
            server.send_message(email)
            st.success("Tu queja ha sido enviada con éxito.")
        except smtplib.SMTPAuthenticationError as e:
            st.error(f"Error de autenticación al enviar el correo: {e.smtp_error.decode()}. Código de error: {e.smtp_code}")
        except Exception as e:
            st.error(f"Error al enviar el correo: {e}")
        finally:
            server.quit()


