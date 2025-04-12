import streamlit as st
import pandas as pd
from datetime import datetime

# Función para calcular biomasa raleada y total
def generar_primera_fila_TN(tp):
    fecha_siembra = datetime.strptime(tp["Fecha siembra"], "%Y-%m-%d")
    peso_inicial = tp["Peso transferencia (g)"]
    densidad = tp["Densidad siembra (i/m2)"]
    dens_raleada = 0
    supervivencia = 100.0

    biomasa_lb_ha = peso_inicial * densidad * 10000 * (supervivencia / 100) / 453.6
    biomasa_raleada = dens_raleada * peso_inicial * 22

    return {
        "Piscina": tp["Piscina"],
        "# Día": 1,
        "Fecha": fecha_siembra.strftime("%d/%m/%y"),
        "Día": fecha_siembra.strftime("%A"),
        "Peso proyecto (g)": peso_inicial,
        "Crecimiento lineal (g/día)": 0.00,
        "Supervivencia base (%)": supervivencia,
        "Densidad (i/m2)": densidad,
        "Dens. Raleada (i/m2)": dens_raleada,
        "Dens. Raleada Acum. (i/m2)": 0,
        "Biomasa raleada (lb/Ha)": biomasa_raleada,
        "Biomasa (lb/Ha)": round(biomasa_lb_ha, 2),
        "% Peso Corporal": 7.61,
        "Alimento (Kg/día)": 50,
        "Alimento (Kg/Ha)": 30.67,
        "Tipo de alimento": tp["Tabla de alimentación"],
        "Alimento Acumulado (kg)": 50,
        "FCA": "",
        "Costo AB ($/día)": 72.00,
        "Costo AB Acumulado ($)": 72.00,
        "Costo Total ($)": 3675.93,
        "Costo Biomasa ($/Lb)": 2.56,
        "Venta raleo ($)": 0.00,
        "Ingresos total ($)": 0.00,
        "UP ($/Ha/día)": -2255.17,
        "ROI": "-100%",
        "Costo mix AB ($/kg)": 1.44
    }

# Estado inicial
if "datos_tp" not in st.session_state:
    st.session_state.datos_tp = {}

# Pestañas
#p1, p2 = st.tabs(["1. Configurar ITA", "2. Registrar TP y Generar TN"])
#p1, p2, p3 = st.tabs(["1. Configurar ITA", "2. Registrar TP y Generar TN", "3. Tabla de Alimentación"])
p1, p2, p3, p4 = st.tabs([
    "1. Configurar ITA",
    "2. Registrar TP y Generar TN",
    "3. Tabla de Alimentación",
    "4. Consolidado"
])

with p1:
    st.header("Paso 1: Configurar Informe ITA")
    st.session_state.nombre_ita = st.text_input("Nombre del ITA", "ITA-TECH-EG-2025-01")
    piscinas_disponibles = [f"P{i}" for i in range(1, 13)]
    st.session_state.piscinas_seleccionadas = st.multiselect("Selecciona las piscinas a registrar", piscinas_disponibles)
    if st.session_state.piscinas_seleccionadas:
        st.success("Piscinas seleccionadas. Ve a la siguiente pestaña.")

with p2:
    st.header("Paso 2: Registro TP por Piscina y generación automática de TN")
    if not st.session_state.get("piscinas_seleccionadas"):
        st.warning("Primero selecciona las piscinas en la pestaña 1.")
    else:
        for piscina in st.session_state.piscinas_seleccionadas:
            with st.expander(f"Piscina {piscina}"):
                tp = {}
                tp["Piscina"] = piscina

                col1, col2 = st.columns(2)

                with col1:
                    tp["Finca"] = st.text_input(f"Finca {piscina}", "CEA", key=f"finca_{piscina}")
                    tp["Área (Ha)"] = st.number_input(f"Área (Ha) {piscina}", value=1.63, key=f"area_{piscina}")
                    tp["Fecha siembra"] = st.date_input(f"Fecha siembra {piscina}", value=datetime(2025, 3, 8), key=f"siembra_{piscina}").strftime("%Y-%m-%d")
                    tp["Densidad siembra (i/m2)"] = st.number_input(f"Densidad siembra (i/m2) {piscina}", value=23.7, key=f"densidad_{piscina}")
                    tp["Días ciclo"] = st.number_input(f"Días ciclo {piscina}", value=70, key=f"dias_ciclo_{piscina}")
                    tp["Peso transferencia (g)"] = st.number_input(f"Peso transferencia (g) {piscina}", value=1.69, key=f"peso_{piscina}")
                    tp["Costo larva/juvenil ($/millar)"] = st.number_input(f"Costo larva/juvenil ($/millar) {piscina}", value=7.00, key=f"costo_larva_{piscina}")
                    tp["Múltiplo redondeo alimento"] = st.number_input(f"Múltiplo redondeo alimento {piscina}", value=5, key=f"multiplo_{piscina}")

                with col2:
                    tp["Supervivencia a 30 días (%)"] = st.number_input(f"Supervivencia a 30 días (%) {piscina}", value=90.0, key=f"sup_30_{piscina}")
                    tp["Supervivencia final (%)"] = st.number_input(f"Supervivencia final (%) {piscina}", value=75.0, key=f"sup_final_{piscina}")
                    tp["Capacidad carga (Lb/Ha)"] = st.number_input(f"Capacidad carga (Lb/Ha) {piscina}", value=7500, key=f"capacidad_{piscina}")
                    tp["Tabla de alimentación"] = st.text_input(f"Tabla de alimentación {piscina}", "TA 4", key=f"tabla_alim_{piscina}")
                    tp["Costo fijo ($/Ha/día)"] = st.number_input(f"Costo fijo ($/Ha/día) {piscina}", value=52, key=f"costo_fijo_{piscina}")
                    tp["Día biometría"] = st.text_input(f"Día biometría {piscina}", "Martes", key=f"biometria_{piscina}")
                    tp["Fecha actual"] = st.date_input(f"Fecha actual {piscina}", key=f"fecha_actual_{piscina}").strftime("%Y-%m-%d")
                    tp["Costo insumos proyecto ($/Ha)"] = st.number_input(f"Costo insumos proyecto ($/Ha) {piscina}", value=500.0, key=f"insumos_proj_{piscina}")
                    tp["Costo insumos real ($/Ha)"] = st.number_input(f"Costo insumos real ($/Ha) {piscina}", value=0.0, key=f"insumos_real_{piscina}")

                st.session_state.datos_tp[piscina] = tp

                #anterior como tabla de columna única
                #tp["Finca"] = st.text_input(f"Finca {piscina}", "CEA", key=f"finca_{piscina}")
                #tp["Área (Ha)"] = st.number_input(f"Área (Ha) {piscina}", value=1.63, key=f"area_{piscina}")
                #tp["Fecha siembra"] = st.date_input(f"Fecha siembra {piscina}", value=datetime(2025, 3, 8), key=f"siembra_{piscina}").strftime("%Y-%m-%d")
                #tp["Densidad siembra (i/m2)"] = st.number_input(f"Densidad siembra (i/m2) {piscina}", value=23.7, key=f"densidad_{piscina}")
                #tp["Días ciclo"] = st.number_input(f"Días ciclo {piscina}", value=70, key=f"dias_ciclo_{piscina}")
                #tp["Peso transferencia (g)"] = st.number_input(f"Peso transferencia (g) {piscina}", value=1.69, key=f"peso_{piscina}")
                #tp["Costo larva/juvenil ($/millar)"] = st.number_input(f"Costo larva/juvenil ($/millar) {piscina}", value=7.00, key=f"costo_larva_{piscina}")
                #tp["Múltiplo redondeo alimento"] = st.number_input(f"Múltiplo redondeo alimento {piscina}", value=5, key=f"multiplo_{piscina}")
                #tp["Supervivencia a 30 días (%)"] = st.number_input(f"Supervivencia a 30 días (%) {piscina}", value=90.0, key=f"sup_30_{piscina}")
                #tp["Supervivencia final (%)"] = st.number_input(f"Supervivencia final (%) {piscina}", value=75.0, key=f"sup_final_{piscina}")
                #tp["Capacidad carga (Lb/Ha)"] = st.number_input(f"Capacidad carga (Lb/Ha) {piscina}", value=7500, key=f"capacidad_{piscina}")
                #tp["Tabla de alimentación"] = st.text_input(f"Tabla de alimentación {piscina}", "TA 4", key=f"tabla_alim_{piscina}")
                #tp["Costo fijo ($/Ha/día)"] = st.number_input(f"Costo fijo ($/Ha/día) {piscina}", value=52, key=f"costo_fijo_{piscina}")
                #tp["Día biometría"] = st.text_input(f"Día biometría {piscina}", "Martes", key=f"biometria_{piscina}")
                #tp["Fecha actual"] = st.date_input(f"Fecha actual {piscina}", key=f"fecha_actual_{piscina}").strftime("%Y-%m-%d")
                #tp["Costo insumos proyecto ($/Ha)"] = st.number_input(f"Costo insumos proyecto ($/Ha) {piscina}", value=500.0, key=f"insumos_proj_{piscina}")
                #tp["Costo insumos real ($/Ha)"] = st.number_input(f"Costo insumos real ($/Ha) {piscina}", value=0.0, key=f"insumos_real_{piscina}")

                # Guardar en estado
                #st.session_state.datos_tp[piscina] = tp

        # Generar TN consolidada
        tn_generada = [generar_primera_fila_TN(tp) for tp in st.session_state.datos_tp.values()]
        df_tn = pd.DataFrame(tn_generada)

        #st.subheader("Tabla Nicovita (TN) Generada")
        #st.dataframe(df_tn, use_container_width=True)

        st.subheader("Visualizar Tabla Nicovita (TN) por Piscina")

        if st.session_state.datos_tp:
            piscina_seleccionada = st.radio(
                "Selecciona la piscina para visualizar su TN:",
                list(st.session_state.datos_tp.keys()),
                horizontal=True,
                key="selector_piscina"
            )

            tp = st.session_state.datos_tp[piscina_seleccionada]
            df_tn = pd.DataFrame([generar_primera_fila_TN(tp)])
            st.dataframe(df_tn, use_container_width=True)

#Tabla de alimentacion (tabla numérica)

# Crear DataFrame de ejemplo con datos de la tabla de alimentación
with p3:
    st.header("Tabla de Alimentación por Peso")
    
    pesos = [round(0.1 * i, 2) for i in range(1, 46)]
    ta1 = ["10.40%", "10.20%", "10.00%", "9.82%", "9.63%", "9.46%", "9.29%", "9.13%", "8.98%", "8.83%", 
           "8.68%", "8.54%", "8.41%", "8.28%", "8.16%", "8.04%", "7.93%", "7.82%", "7.71%", "7.61%", 
           "7.52%", "7.42%", "7.33%", "7.25%", "7.16%", "7.08%", "7.01%", "6.93%", "6.86%", "6.79%", 
           "6.73%", "6.66%", "6.60%", "6.55%", "6.49%", "6.44%", "6.38%", "6.33%", "6.29%", "6.24%", 
           "6.20%", "6.15%", "6.11%", "6.07%", "6.04%"]
    ta2 = ["9.15%", "8.98%", "8.80%", "8.64%", "8.48%", "8.32%", "8.18%", "8.04%", "7.90%", "7.77%", 
           "7.64%", "7.52%", "7.40%", "7.29%", "7.18%", "7.08%", "6.98%", "6.88%", "6.79%", "6.70%", 
           "6.61%", "6.53%", "6.45%", "6.38%", "6.30%", "6.23%", "6.17%", "6.10%", "6.04%", "5.98%", 
           "5.92%", "5.86%", "5.81%", "5.76%", "5.71%", "5.66%", "5.62%", "5.57%", "5.53%", "5.49%", 
           "5.45%", "5.42%", "5.38%", "5.35%", "5.31%"]
    ta3 = ta2  # usa la misma lista si son iguales, o reemplaza por su versión real si son distintas
    ta4 = ["9.83%", "9.68%", "9.49%", "9.31%", "9.14%", "8.97%", "8.81%", "8.65%", "8.51%", "8.36%",
           "8.23%", "8.09%", "7.97%", "7.84%", "7.73%", "7.61%", "7.50%", "7.40%", "7.30%", "7.20%",
           "7.11%", "7.02%", "6.93%", "6.85%", "6.77%", "6.69%", "6.62%", "6.55%", "6.48%", "6.42%",
           "6.35%", "6.29%", "6.23%", "6.18%", "6.12%", "6.07%", "6.02%", "5.98%", "5.93%", "5.89%",
           "5.84%", "5.80%", "5.76%", "5.73%", "5.69%"]
    ta5 = ["11.83%", "10.69%", "10.03%", "9.56%", "9.19%", "8.89%", "8.64%", "8.42%", "8.23%", "8.06%",
           "7.90%", "7.76%", "7.63%", "7.51%", "7.39%", "7.29%", "7.19%", "7.10%", "7.01%", "6.92%",
           "6.84%", "6.77%", "6.69%", "6.62%", "6.56%", "6.49%", "6.43%", "6.37%", "6.31%", "6.26%",
           "6.21%", "6.15%", "6.10%", "6.05%", "6.01%", "5.96%", "5.92%", "5.87%", "5.83%", "5.79%",
           "5.75%", "5.71%", "5.67%", "5.63%", "5.60%"]

    df_alimentacion = pd.DataFrame({
        "Pesos": pesos,
        "TA 1": ta1,
        "TA 2": ta2,
        "TA 3": ta3,
        "TA 4": ta4,
        "TA 5": ta5
    })

    st.dataframe(df_alimentacion, use_container_width=True)

with p4:
    st.header("TN Consolidada")
    
    if st.session_state.datos_tp:
        tn_consolidada = [generar_primera_fila_TN(tp) for tp in st.session_state.datos_tp.values()]
        df_consolidada = pd.DataFrame(tn_consolidada)
        st.dataframe(df_consolidada, use_container_width=True)
    else:
        st.info("Aún no se han registrado datos en ninguna piscina.")
