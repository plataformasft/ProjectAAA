import streamlit as st
import pandas as pd
import uuid
from google.cloud import bigquery
from google.oauth2 import service_account
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode




# Configuración de credenciales y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_file("appshandler-423416-66f6cb588a32.json")
client = bigquery.Client(credentials=credentials, project='appshandler-423416')




def load_unique_values(column_name):
    query = f"""
    SELECT DISTINCT {column_name} FROM `appshandler-423416.BigQueryAppHandler.listaprueba`
    ORDER BY {column_name}
    """
    result = client.query(query).to_dataframe()
    return result[column_name].tolist()




def load_data_for_edit(prueba):
    query = f"""
    SELECT id, dieta, tratamiento, empresa FROM `appshandler-423416.BigQueryAppHandler.listaprueba`
    WHERE prueba = '{prueba}'
    """
    return client.query(query).to_dataframe()




def upload_to_bigquery(df, table_id, prueba, merge=False, source_table=None, key_column=None):
    df['prueba'] = prueba  # asegurar que la columna prueba esté correctamente poblada
   
    # Configuración del trabajo de carga
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()




    if merge:
        merge_query = f"""
            MERGE `{source_table}` AS original
            USING `{table_id}` AS updated
            ON original.id = updated.id
            WHEN MATCHED THEN
                UPDATE SET original.dieta = updated.dieta,
                           original.tratamiento = updated.tratamiento,
                           original.empresa = updated.empresa
        """
        client.query(merge_query).result()
        client.delete_table(table_id)  # Eliminar la tabla temporal




def main():
    st.title("Edición de Datos")
    prueba_options = load_unique_values("prueba")
    selected_prueba = st.selectbox("Prueba", options=prueba_options)




    if selected_prueba:
        data_to_edit = load_data_for_edit(selected_prueba)




        gb = GridOptionsBuilder.from_dataframe(data_to_edit)
        gb.configure_pagination()
        gb.configure_side_bar()
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
        grid_options = gb.build()




        response = AgGrid(
            data_to_edit,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True,
            height=300,
            allow_unsafe_jscode=True
        )




        if st.button("Guardar Cambios"):
            updated_df = pd.DataFrame(response['data'])
            temp_table_id = "appshandler-423416.BigQueryAppHandler.temp_updates"
            upload_to_bigquery(updated_df, temp_table_id, selected_prueba, merge=True, source_table="appshandler-423416.BigQueryAppHandler.listaprueba", key_column="id")
            st.success("Datos actualizados correctamente en BigQuery.")




if __name__ == "__main__":
    main()


#######################################################################

import streamlit as st
import smtplib
from email.message import EmailMessage

st.title("Formulario de Solicitud de Cambio 📅")
st.header("Instrucciones")
st.markdown("""
1. Completa el formulario con la información necesaria.
2. Revisa cuidadosamente los datos ingresados antes de enviar. Por favor, detallar el valor anterior y el valor posterior.
3. Si tienes algún inconveniente, contacta a bdonayred@vitapro.com.pe
""")

# Sidebar
st.sidebar.success("Estás en la página de solicitud de cambios")

# Formulario para enviar solicitudes de cambio
with st.form("form_solicitud_cambio"):
    st.write("Por favor, completa los datos para la solicitud de cambio:")
    nombre_remitente = st.text_input("Nombre del Remitente:")
    correo_remitente = st.text_input("Correo corporativo:")
    prueba = st.text_input("Nombre de la Prueba:")
    mensaje_adicional = st.text_area("Mensaje Adicional:")
    submit_button = st.form_submit_button("Enviar Solicitud")

    if submit_button:
        contenido_email = f"""Solicitud de Cambio:
Nombre del Remitente: {nombre_remitente}
Correo: {correo_remitente}
Prueba: {prueba}
Mensaje Adicional: {mensaje_adicional}
"""
        email = EmailMessage()
        email.set_content(contenido_email)
        email['Subject'] = 'Solicitud de Cambio desde la aplicación Streamlit'
        email['From'] = f"{nombre_remitente} <{correo_remitente}>"  # Asegúrate de que el correo es visible
        email['To'] = 'bdonayred@vitapro.com.pe'

        try:
            # Configura aquí tu servidor SMTP y tus credenciales
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login('brunodonayredonayre@gmail.com', 'vjgksshxutcjydod')
            server.send_message(email)
            st.success("Tu solicitud ha sido enviada con éxito.")
        except smtplib.SMTPAuthenticationError as e:
            st.error(f"Error de autenticación al enviar el correo: {e.smtp_error.decode()}. Código de error: {e.smtp_code}")
        except Exception as e:
            st.error(f"Error al enviar el correo: {e}")
        finally:
            server.quit()