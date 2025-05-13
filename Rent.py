import streamlit as st
from datetime import datetime, date

class Proyecto:
    ESTADOS_VALIDOS = {"En curso", "Finalizado", "Cancelado"}

    def __init__(self, id_usuario, codigo_proyecto, fecha_inicio, fecha_estimacion_terminacion,
                 horas_jefe, horas_proyectista, costo_subcontratacion, gastos, ingreso,
                 tarifa_hora_jefe, tarifa_hora_proyectista, estado="En curso",
                 fecha_efectiva_terminacion=None):

        self.id_usuario = id_usuario
        self.codigo_proyecto = codigo_proyecto
        self.fecha_inicio = fecha_inicio
        self.fecha_estimacion_terminacion = fecha_estimacion_terminacion
        self.fecha_efectiva_terminacion = fecha_efectiva_terminacion
        self.horas_jefe = horas_jefe
        self.horas_proyectista = horas_proyectista
        self.costo_subcontratacion = costo_subcontratacion
        self.gastos = gastos
        self.ingreso = ingreso
        self.tarifa_hora_jefe = tarifa_hora_jefe
        self.tarifa_hora_proyectista = tarifa_hora_proyectista

        if estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Debe ser uno de {self.ESTADOS_VALIDOS}")
        self.estado = estado

        self.validar_fechas()

    def calcular_costo_total(self):
        return (self.horas_jefe * self.tarifa_hora_jefe) + \
               (self.horas_proyectista * self.tarifa_hora_proyectista) + \
               self.costo_subcontratacion + self.gastos

    def calcular_rentabilidad(self):
        costo_total = self.calcular_costo_total()
        return ((self.ingreso - costo_total) / costo_total) * 100 if costo_total else 0

    def registrar_fecha_efectiva_terminacion(self, fecha_efectiva):
        if fecha_efectiva < self.fecha_inicio:
            raise ValueError("La fecha efectiva no puede ser anterior a la fecha de inicio.")
        self.fecha_efectiva_terminacion = fecha_efectiva
        self.estado = "Finalizado"

    def cancelar_proyecto(self):
        self.estado = "Cancelado"
        self.fecha_efectiva_terminacion = date.today()

    def evaluar_estimacion(self):
        if self.estado != "Finalizado" or not self.fecha_efectiva_terminacion:
            return "Proyecto en curso"
        return "Adecuada" if self.fecha_efectiva_terminacion <= self.fecha_estimacion_terminacion else "Inadecuada"

    def validar_fechas(self):
        if self.fecha_inicio > self.fecha_estimacion_terminacion:
            raise ValueError("La fecha de inicio no puede ser posterior a la estimada de terminación.")
        if self.fecha_efectiva_terminacion and self.fecha_inicio > self.fecha_efectiva_terminacion:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha efectiva de terminación.")

    def resumen_proyecto(self):
        return {
            "Código Proyecto": self.codigo_proyecto,
            "Usuario Responsable": self.id_usuario,
            "Estado": self.estado,
            "Inicio": self.fecha_inicio,
            "Estimado Fin": self.fecha_estimacion_terminacion,
            "Efectivo Fin": self.fecha_efectiva_terminacion,
            "Costo Total": self.calcular_costo_total(),
            "Ingreso": self.ingreso,
            "Rentabilidad (%)": round(self.calcular_rentabilidad(), 2),
            "Evaluación Estimación": self.evaluar_estimacion()
        }

st.title("Gestión de Proyectos - Ashes Fire")

if 'proyectos' not in st.session_state:
    st.session_state.proyectos = []

with st.form("Registrar Proyecto"):
    st.subheader("Registro de Nuevo Proyecto")
    id_usuario = st.text_input("ID Usuario")
    codigo_proyecto = st.text_input("Código Proyecto")
    fecha_inicio = st.date_input("Fecha de Inicio", value=date.today())
    fecha_estimacion = st.date_input("Fecha Estimada de Terminación", value=date.today())
    horas_jefe = st.number_input("Horas Jefe Proyecto", min_value=0.0)
    horas_proyectista = st.number_input("Horas Proyectista", min_value=0.0)
    costo_subcontratacion = st.number_input("Costo Subcontratación", min_value=0.0)
    gastos = st.number_input("Gastos", min_value=0.0)
    ingreso = st.number_input("Ingreso del Proyecto", min_value=0.0)
    tarifa_jefe = st.number_input("Tarifa Hora Jefe", min_value=0.0)
    tarifa_proyectista = st.number_input("Tarifa Hora Proyectista", min_value=0.0)
    submitted = st.form_submit_button("Registrar Proyecto")

    if submitted:
        try:
            nuevo = Proyecto(
                id_usuario, codigo_proyecto, fecha_inicio, fecha_estimacion,
                horas_jefe, horas_proyectista, costo_subcontratacion, gastos,
                ingreso, tarifa_jefe, tarifa_proyectista
            )
            st.session_state.proyectos.append(nuevo)
            st.success("Proyecto registrado exitosamente.")
        except Exception as e:
            st.error(f"Error: {e}")

st.subheader("Listado de Proyectos")

for i, proyecto in enumerate(st.session_state.proyectos):
    resumen = proyecto.resumen_proyecto()
    with st.expander(f"{resumen['Código Proyecto']} - {resumen['Estado']}"):
        for k, v in resumen.items():
            st.write(f"{k}: {v}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Finalizar {i}"):
                try:
                    proyecto.registrar_fecha_efectiva_terminacion(date.today())
                    st.success("Proyecto finalizado.")
                except Exception as e:
                    st.error(f"Error: {e}")
        with col2:
            if st.button(f"Cancelar {i}"):
                proyecto.cancelar_proyecto()
                st.warning("Proyecto cancelado.")
