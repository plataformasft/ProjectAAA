import streamlit as st
import pandas as pd
import numpy as np
import datetime
from datetime import date
from datetime import datetime
import logging
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from datetime import date
import plotly.express as px  # Importar Plotly Express para gráficos
import plotly.graph_objects as go  # Importar para usar objetos gráficos
from google.cloud import bigquery
from google.oauth2 import service_account
import uuid
# CSS para personalizar la ubicación de la imagen
st.markdown("""
<style>
.sidebar .sidebar-content {
    padding-top: 150px;  # Aumenta el espacio en la parte superior del sidebar para acomodar la imagen
}
.sidebar img {
    width: 80%;  # Ajusta el ancho de la imagen a 80% del ancho del sidebar
    margin-left: auto;  # Centra la imagen horizontalmente
    margin-right: auto;
    display: block;  # Asegura que la imagen se trate como bloque y no como inline
}
</style>
""", unsafe_allow_html=True)
# Ruta a la imagen, ajusta según tu ubicación de archivo o URL
image_path = "vitapro_2.png"
# Coloca la imagen en el sidebar
# Colocar la imagen en el sidebar con un ancho específico
st.sidebar.image(image_path, width=250)  # Ajusta el ancho a 150 píxeles

# Configura tus credenciales de GCP
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "appshandler-423416-66f6cb588a32.json"
# Configuración de credenciales y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_file(
    "appshandler-423416-66f6cb588a32.json"  # Cambia a tu archivo JSON de credenciales
)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

def load_data():
    query = """
    SELECT * FROM `appshandler-423416.BigQueryAppHandler.listaprueba`
    """
    return client.query(query).to_dataframe()

def upload_to_bigquery(dataset_id, table_id, data):
    """Sube datos actualizados a Google BigQuery."""
    table_full_path = f"{client.project}.{dataset_id}.{table_id}"
    job = client.load_table_from_dataframe(data, table_full_path)
    job.result()
    return "Datos cargados a BigQuery exitosamente!" if job.errors is None else f"Errores durante la carga: {job.errors}"

def get_next_label(fechainicio):
    year = fechainicio.year
    if 'label_count' not in st.session_state or st.session_state.label_year != year:
        st.session_state.label_count = 1
        st.session_state.label_year = year
    else:
        st.session_state.label_count += 1
    letter = chr(64 + st.session_state.label_count) if st.session_state.label_count <= 26 else chr(64 + (st.session_state.label_count % 26))
    quarter = (fechainicio.month - 1) // 3 + 1
    return f"{year}Q{quarter}{letter}"

# Diccionario que mapea CEAs a sus salas correspondientes
cea_to_salas = {
    "Tumbes": ["a", "b", "c", "d", "e", "s8t"],
    "Trujillo": ["trujillo"],
    "UCSUR": ["ucsur"]
}


#def check_sala_availability(data, cea_to_salas, current_date):
#    current_timestamp = pd.Timestamp(current_date)
#    data = data.sort_values(by=['sala', 'fechafinal'], ascending=[True, False])
#    data['fechafinal'] = pd.to_datetime(data['fechafinal'])
#    data['fechainicio'] = pd.to_datetime(data['fechainicio'])

    # Determinar disponibilidad y estado
#    data['disponible'] = data.apply(
#        lambda row: "No Disponible" if row['fechainicio'] <= current_timestamp <= row['fechafinal'] else "Disponible", axis=1
#    )
#    data['estado'] = data.apply(
#        lambda row: "En curso" if row['fechainicio'] <= current_timestamp <= row['fechafinal'] else "Programado" if row['fechainicio'] > current_timestamp else "Finalizado", axis=1
#    )

#    all_salas = []
#    for cea, salas in cea_to_salas.items():
#        for sala in salas:
#            if sala in data['sala'].values:
#                sala_data = data[data['sala'] == sala].iloc[0]
#                all_salas.append({
#                    'cea': cea,
#                    'sala': sala,
#                    'estado': sala_data['estado'],
#                    'disponible': sala_data['disponible']
#                })
#            else:
#                all_salas.append({
#                    'cea': cea,
#                    'sala': sala,
#                    'estado': 'Libre',
#                    'disponible': 'Disponible'
#                })
#    return pd.DataFrame(all_salas)

def check_sala_availability(data, cea_to_salas, current_date):
    current_timestamp = pd.Timestamp(current_date)
    data = data.sort_values(by=['sala', 'fechafinal'], ascending=[True, False])
    data['fechafinal'] = pd.to_datetime(data['fechafinal'])
    data['fechainicio'] = pd.to_datetime(data['fechainicio'])

    # Determinar estado y disponibilidad
    data['estado'] = data.apply(
        lambda row: "En curso" if row['fechainicio'] <= current_timestamp <= row['fechafinal']
                    else "Programado" if row['fechainicio'] > current_timestamp
                    else "Finalizado", axis=1
    )
    data['disponible'] = data.apply(
        lambda row: "No Disponible" if row['estado'] in ["En curso", "Programado"] else "Disponible", axis=1
    )

    all_salas = []
    for cea, salas in cea_to_salas.items():
        for sala in salas:
            if sala in data['sala'].values:
                # Tomar la información de la última prueba de la sala
                sala_data = data[data['sala'] == sala].iloc[0]
                all_salas.append({
                    'cea': cea,
                    'sala': sala,
                    'estado': sala_data['estado'],
                    'disponible': sala_data['disponible'],
                    'fecha_inicio_ultima_prueba': sala_data['fechainicio'].date(),  # Convertir a formato de fecha
                    'prueba': sala_data['prueba'],  # Asumiendo que 'prueba' es una columna en tu DataFrame
                    'etiqueta': sala_data.get('etiqueta', 'Default')  # Suponiendo que 'etiqueta' es opcional
                })
            else:
                # Si no hay datos de pruebas para una sala, rellenar con valores predeterminados
                all_salas.append({
                    'cea': cea,
                    'sala': sala,
                    'estado': 'Libre',
                    'disponible': 'Disponible',
                    'fecha_inicio_ultima_prueba': None,  # Mantener como None si no hay fecha
                    'prueba': 'Ninguna',  # Valor predeterminado para pruebas
                    'etiqueta': 'Sin Datos'  # Valor predeterminado para etiqueta
                })
    return pd.DataFrame(all_salas)

# Extraer la última fecha de prueba para cada sala seleccionada
def get_last_test_dates(data):
    # Supongamos que 'data' tiene una columna 'fechafinal' que indica la fecha final de cada prueba
    last_test_dates = data.groupby('sala')['fechafinal'].max().reset_index()
    last_test_dates.rename(columns={'fechafinal': 'fecha_ultima_prueba'}, inplace=True)
    return last_test_dates

# Selección de la página
page = st.sidebar.selectbox('Selecciona la página', ['📝 Ingreso de datos','🌍 Disponibilidad de salas', '📊 Dashboard'])

def get_filtered_options(column, data, filter_column=None, filter_value=None):
    if filter_column and filter_value:
        filtered_data = data[data[filter_column] == filter_value]
    else:
        filtered_data = data
    return ['All'] + sorted(filtered_data[column].dropna().unique().tolist())


if page == '📝 Ingreso de datos':
    # Página de entrada de datos
    st.header("Registro de datos 🤖")
    # Agregando un párrafo debajo del encabezado
    st.write("Por favor, ingresa los datos necesarios en el formulario a continuación para continuar con el registro.")
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({
            "cea": [], "sala": [], "prueba": [], "estado": [],
            "fechasiembre": [], "fechainicio": [], "fechafinal": [],
            "empresa": [], "dieta": [], "tratamiento": [], "etiqueta": [],
        })

    #cea = st.text_input("CEA")
    #cea = st.selectbox("CEA", ["tumbes", "trujillo", "ucsur"])
    # Simulación de datos: diccionario que mapea CEAs a una lista de salas
    # Diccionario que mapea CEAs a sus salas correspondientes
    cea_to_salas = {
        "tumbes": ["a", "b", "c", "d", "e", "s8t"],
        "trujillo": ["trujillo"],
        "ucsur": ["ucsur"]
    }

    # Selección del CEA usando un desplegable en Streamlit
    cea = st.selectbox("Seleccione el CEA", list(cea_to_salas.keys()))

    # Una vez seleccionado el CEA, mostrar un desplegable con las salas correspondientes
    salas_options = cea_to_salas[cea]  # Obtener las salas para el CEA seleccionado
    #sala = st.selectbox("Seleccione la Sala", salas_options)

    #sala = st.text_input("Sala")
    sala = st.selectbox("Sala", ["Seleccione sala"] + salas_options)
    prueba = st.text_input("Nombre de la prueba")
    estado = st.selectbox("Estado",["prueba programada","prueba en curso","prueba finalizada"])
    #etiqueta = st.text_input("Etiqueta de la prueba")
    fechasiembre = st.date_input("Fecha de siembra")
    fechainicio = st.date_input("Fecha de inicio")
    fechafinal = st.date_input("Fecha final")

    data_entries = st.text_area("Ingrese Empresa, Dieta, Tratamiento separados por comas (una línea por entrada)")

    if st.button("Añadir al Registro"):
        entries = data_entries.split('\n')
        new_rows = []
        for entry in entries:
            try:
                empresa, dieta, tratamiento = [x.strip() for x in entry.split(',')]
                etiqueta = get_next_label(fechainicio)
                new_row = {
                    "id": str(uuid.uuid4()),  # Generar un ID único para cada fila
                    "cea": cea,
                    "sala": sala,
                    "prueba": prueba,
                    "estado": estado,
                    "fechasiembre": pd.to_datetime(fechasiembre, format='%d/%m/%Y', errors='coerce').normalize(),
                    "fechainicio": pd.to_datetime(fechainicio, format='%d/%m/%Y', errors='coerce').normalize(),
                    "fechafinal": pd.to_datetime(fechafinal, format='%d/%m/%Y', errors='coerce').normalize(),
                    "empresa": empresa,
                    "dieta": dieta,
                    "tratamiento": tratamiento,
                    "etiqueta": etiqueta
                }
                new_rows.append(new_row)
            except ValueError:
                st.error("Asegúrese de que cada línea tenga exactamente tres elementos separados por comas.")
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)

    ############################################################################################################
    # Mostrar el DataFrame y permitir la eliminación de registros
    st.dataframe(st.session_state.data)
    selected_indices = st.multiselect("Seleccionar registros para eliminar (por ID)", st.session_state.data.index)
    if st.button("Eliminar Registros Seleccionados"):
        st.session_state.data = st.session_state.data.drop(selected_indices)
        st.session_state.data.reset_index(drop=True, inplace=True)
    ############################################################################################################

    if st.button("Enviar a BigQuery"):
        if not st.session_state.data.empty:
            table_id = "appshandler-423416.BigQueryAppHandler.listaprueba"
            job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
            job = client.load_table_from_dataframe(st.session_state.data, table_id, job_config=job_config)
            job.result()
            st.success("Datos enviados con éxito a BigQuery")
            st.session_state.data = pd.DataFrame(columns=st.session_state.data.columns)
        else:
            st.error("El DataFrame está vacío. Añada datos antes de enviar.")


 # Muestra el DataFrame con dimensiones específicas
     # Calcula un ancho dinámico basado en el número de columnas
    # Asumiendo un ancho estimado de 150 píxeles por columna
    dynamic_width = len(st.session_state.data.columns) * 500
    st.dataframe(st.session_state.data, width=dynamic_width)

#########################Dashboard
elif page == '📊 Dashboard':
    # Página de visualización de datos

    st.header("Visualización de datos 🚀")

    # Agregando un párrafo debajo del encabezado
    st.write("Detalle de visualización de los datos ingresados.")

    data = load_data()

    cea_choice = st.sidebar.selectbox('Filtrar por CEA', get_filtered_options('cea', data))
    # Actualizar data según cea_choice
    filtered_data = data if cea_choice == 'All' else data[data['cea'] == cea_choice]
    
    sala_options = get_filtered_options('sala', filtered_data, 'cea', cea_choice if cea_choice != 'All' else None)
    sala_choice = st.sidebar.selectbox('Filtrar por Sala', sala_options)
    # Actualizar data según sala_choice
    filtered_data = filtered_data if sala_choice == 'All' else filtered_data[filtered_data['sala'] == sala_choice]
    
    prueba_options = get_filtered_options('prueba', filtered_data, 'sala', sala_choice if sala_choice != 'All' else None)
    prueba_choice = st.sidebar.selectbox('Filtrar por Prueba', prueba_options)
    # Actualizar data según prueba_choice
    filtered_data = filtered_data if prueba_choice == 'All' else filtered_data[filtered_data['prueba'] == prueba_choice]
    
    estado_options = get_filtered_options('estado', filtered_data, 'prueba', prueba_choice if prueba_choice != 'All' else None)
    estado_choice = st.sidebar.selectbox('Filtrar por Estado', estado_options)
    # Actualizar data según estado_choice
    filtered_data = filtered_data if estado_choice == 'All' else filtered_data[filtered_data['estado'] == estado_choice]

    # Muestra el DataFrame con dimensiones específicas
    #st.dataframe(data, width=5000)

    # Asumiendo un ancho estimado de 150 píxeles por columna
    #dynamic_width = len(filtered_data.columns) * 150
    #st.dataframe(filtered_data, width=dynamic_width)

    # Reordenar columnas según el orden específico requerido
    column_order = ['etiqueta', 'prueba', 'cea', 'estado', 'sala', 'fechasiembre', 'fechainicio', 'fechafinal', 'dieta', 'tratamiento', 'empresa', 'id']
    # Asegurarse de que todas las columnas estén presentes antes de reordenar
    if all(col in filtered_data.columns for col in column_order):
        filtered_data = filtered_data[column_order]
    else:
        st.error("Algunas columnas requeridas no están presentes en los datos.")

    # Asumiendo un ancho estimado de 150 píxeles por columna
    dynamic_width = len(filtered_data.columns) * 150
    st.dataframe(filtered_data, width=dynamic_width)

    ###################################################################################
    ########################Gráfico de Gantt usando los datos filtrados
    # Gráfico de Gantt usando los datos filtrados
    if not filtered_data.empty:
        filtered_data['cea_prueba'] = "CEA: " + filtered_data['cea'] + " - Prueba: " + filtered_data['prueba']
        dietas = filtered_data.groupby('cea_prueba')['dieta'].apply(lambda x: ', '.join(x.unique())).reset_index()
        dietas_dict = {k: f"Dietas:\n{v}\nSala: {filtered_data[filtered_data['cea_prueba'] == k]['sala'].iloc[0]}" for k, v in dietas.set_index('cea_prueba')['dieta'].to_dict().items()}
        
        fig = px.timeline(
            filtered_data,
            x_start="fechainicio",
            x_end="fechafinal",
            y="cea_prueba",
            title="Timeline de Pruebas",
            labels={"cea": "CEA", "prueba": "Prueba", "fechainicio": "Fecha Inicio", "fechafinal": "Fecha Final"},
            color="estado",
            height=600,
            width=1000
        )
        fig.update_yaxes(categoryorder="total ascending")

        for i, row in filtered_data.iterrows():
            dieta_text = dietas_dict.get(row['cea_prueba'], 'No disponible')
            fig.add_annotation(
                x=row['fechafinal'],
                y=row['cea_prueba'],
                text=dieta_text,
                showarrow=False,
                xshift=50,
                textangle=0,
                align='left',
                font=dict(family="Arial", size=12, color="white")
            )

            fecha_siembra = row['fechasiembre'].strftime('%Y-%m-%d')  # Formato correcto
            # Anotaciones de fecha de siembra
            #fecha_siembra = row['fechasiembre']
            #if isinstance(fecha_siembra, datetime.datetime):
            #    fecha_siembra = fecha_siembra.strftime('%Y-%m-%d')
            #else:
            #    try:
            #        fecha_siembra = datetime.datetime.strptime(fecha_siembra, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            #    except ValueError:
            #        pass  # Ignora errores si la fecha está mal formateada o ya está correcta

            fig.add_trace(go.Scatter(
                x=[fecha_siembra],
                y=[row['cea_prueba']],
                text=[f"Siembra: {fecha_siembra}"],
                mode='markers+text',
                marker=dict(size=12, color='gold'),
                textposition="top center",
                textfont=dict(family="Arial", size=10, color="white"),
                showlegend=False
            ))

        fig.update_layout(
            xaxis_title='Fecha',
            yaxis_title='CEA - Prueba',
            legend_title="Estado",
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No hay datos para mostrar en el gráfico de Gantt.")

####################################################################################
####pages

elif page == '🌍 Disponibilidad de salas':

    # Cargar datos y configurar fecha actual
    data = load_data()
    today = pd.Timestamp.now()
    # Diccionario que mapea CEAs a sus salas correspondientes
    cea_to_salas = {
        "Tumbes": ["a", "b", "c", "d", "e", "s8t"],
        "Trujillo": ["trujillo"],
        "UCSUR": ["ucsur"]
    }

    # Obtener datos de disponibilidad de salas
    availability_data = check_sala_availability(data, cea_to_salas, today)

    # Seleccionar CEA y filtrar salas disponibles
    #cea = st.selectbox("Seleccione el CEA", list(cea_to_salas.keys()))
    #filtered_salas = availability_data[(availability_data['cea'] == cea) & (availability_data['disponible'] == 'Disponible')]

    #st.write("Salas disponibles en", cea)
    #st.dataframe(filtered_salas[['sala', 'estado', 'disponible']])

    ########################################################################
    # Obtener las últimas fechas de prueba y fusionarlas con los datos de disponibilidad
    last_test_dates = get_last_test_dates(data)
    extended_availability_data = pd.merge(availability_data, last_test_dates, on='sala', how='left')

    # Seleccionar CEA y filtrar salas disponibles
    # Seleccionar CEA y filtrar salas disponibles
    cea = st.selectbox("Seleccione el CEA", list(cea_to_salas.keys()), key='cea_select_box')

    filtered_salas = extended_availability_data[(extended_availability_data['cea'] == cea)]

    # Mostrar las salas disponibles
    st.write("Salas disponibles en", cea)
    st.dataframe(filtered_salas[['sala', 'estado', 'disponible','fecha_inicio_ultima_prueba', 'fecha_ultima_prueba','prueba','etiqueta']])
    

    #####################################GRAFICO

    import matplotlib.pyplot as plt
    import pandas as pd
    import streamlit as st

    # Agrupar los datos por CEA y estado para contar las salas
    # Agrupar los datos por CEA y estado para contar las salas
   # Agrupar los datos por CEA y estado para contar las salas
    status_counts = availability_data.groupby(['cea', 'estado']).size().unstack(fill_value=0)

    # Definir una paleta de colores personalizada para los estados
    colors = {
        'Disponible': 'green',
        'Libre': 'lightgreen',
        'No Disponible': 'red',
        'Programado': 'orange',
        'En curso': 'blue',
        'Finalizado': 'gray'
    }

    # Crear la figura con Plotly
    fig = go.Figure()

    # Añadir una barra para cada estado con etiquetas de datos y colores personalizados
    for estado in status_counts.columns:
        fig.add_trace(go.Bar(
            x=status_counts.index,
            y=status_counts[estado],
            name=estado,
            text=status_counts[estado],  # Añadir texto de las etiquetas
            textposition='inside',
            textfont=dict(size=14),  # Aumentar el tamaño de la fuente de las etiquetas de datos
            marker_color=colors.get(estado, 'black')  # Asignar colores personalizados
        ))

    # Actualizar el diseño para hacer las barras apiladas
    fig.update_layout(
        barmode='stack',
        title='Disponibilidad de Salas por CEA',
        xaxis_title='CEA',
        yaxis_title='Número de Salas',
        legend_title='Estado'
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)
