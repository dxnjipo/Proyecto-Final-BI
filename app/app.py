"""
app.py
------
Aplicación Streamlit para la gestión de Órdenes de Servicio Técnico.

Funcionalidades:
  - Dashboard con KPIs y gráficos
  - CRUD para Clientes, Técnicos, Equipos y Órdenes
  - Múltiples consultas con filtros
  - Formularios con validación
  - Conexión segura a Oracle Cloud
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
from connection import get_connection
import oracledb

# =====================================================================
# CONFIGURACIÓN DE LA PÁGINA
# =====================================================================
st.set_page_config(
    page_title="TecniServ | Gestión de Servicio Técnico",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# CAPA DE ACCESO A DATOS
# Funciones centralizadas para hablar con Oracle.
# Se cachean las lecturas con TTL corto para no saturar la BD.
# =====================================================================

def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Ejecuta un SELECT y devuelve un DataFrame."""
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=params or {})


def run_dml(sql: str, params: dict) -> int:
    """Ejecuta un INSERT/UPDATE/DELETE. Devuelve filas afectadas."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount


@st.cache_data(ttl=30)
def cached_query(sql: str, key: str = "") -> pd.DataFrame:
    """Cache liviano (30s) para consultas frecuentes."""
    return run_query(sql)


def clear_cache():
    """Invalida el cache tras una escritura."""
    cached_query.clear()


# =====================================================================
# CONSULTAS REUTILIZABLES (vistas del negocio)
# =====================================================================

Q_CLIENTES = """
    SELECT c.id_cliente AS "ID",
           c.documento  AS "Documento",
           c.nombre     AS "Nombre",
           c.telefono   AS "Teléfono",
           c.email      AS "Email",
           c.ciudad     AS "Ciudad",
           TO_CHAR(c.fecha_registro,'YYYY-MM-DD') AS "Registrado"
    FROM CLIENTES c
    ORDER BY c.id_cliente
"""

Q_TECNICOS = """
    SELECT t.id_tecnico  AS "ID",
           t.documento   AS "Documento",
           t.nombre      AS "Nombre",
           t.especialidad AS "Especialidad",
           t.telefono    AS "Teléfono",
           TO_CHAR(t.fecha_contratacion,'YYYY-MM-DD') AS "Contratación",
           t.activo      AS "Activo"
    FROM TECNICOS t
    ORDER BY t.id_tecnico
"""

Q_EQUIPOS = """
    SELECT e.id_equipo  AS "ID",
           c.nombre     AS "Cliente",
           e.tipo       AS "Tipo",
           e.marca      AS "Marca",
           e.modelo     AS "Modelo",
           e.serial     AS "Serial",
           e.anio_compra AS "Año"
    FROM EQUIPOS e
    JOIN CLIENTES c ON c.id_cliente = e.id_cliente
    ORDER BY e.id_equipo
"""

Q_ORDENES = """
    SELECT o.id_orden    AS "ID",
           TO_CHAR(o.fecha_ingreso,'YYYY-MM-DD') AS "Ingreso",
           TO_CHAR(o.fecha_entrega,'YYYY-MM-DD') AS "Entrega",
           c.nombre      AS "Cliente",
           e.tipo || ' ' || e.marca AS "Equipo",
           t.nombre      AS "Técnico",
           o.estado      AS "Estado",
           o.prioridad   AS "Prioridad",
           o.costo_mano_obra + o.costo_repuestos AS "Total ($)"
    FROM ORDENES_SERVICIO o
    JOIN EQUIPOS  e ON e.id_equipo  = o.id_equipo
    JOIN CLIENTES c ON c.id_cliente = e.id_cliente
    JOIN TECNICOS t ON t.id_tecnico = o.id_tecnico
    ORDER BY o.fecha_ingreso DESC
"""


# =====================================================================
# PÁGINAS DE LA APP
# =====================================================================

def page_dashboard():
    st.title("📊 Dashboard")
    st.caption("Indicadores generales del taller en tiempo real.")

    # ---- KPIs principales ----
    try:
        kpis = run_query("""
            SELECT
                (SELECT COUNT(*) FROM CLIENTES)                                     AS total_clientes,
                (SELECT COUNT(*) FROM EQUIPOS)                                      AS total_equipos,
                (SELECT COUNT(*) FROM ORDENES_SERVICIO)                             AS total_ordenes,
                (SELECT COUNT(*) FROM ORDENES_SERVICIO
                    WHERE estado NOT IN ('ENTREGADA','CANCELADA'))                  AS ordenes_abiertas,
                (SELECT NVL(SUM(costo_mano_obra + costo_repuestos),0)
                    FROM ORDENES_SERVICIO WHERE estado = 'ENTREGADA')               AS ingresos_total
            FROM dual
        """)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Clientes",        int(kpis["TOTAL_CLIENTES"][0]))
        c2.metric("Equipos",         int(kpis["TOTAL_EQUIPOS"][0]))
        c3.metric("Órdenes totales", int(kpis["TOTAL_ORDENES"][0]))
        c4.metric("Abiertas",        int(kpis["ORDENES_ABIERTAS"][0]))
        c5.metric("Ingresos (COP)",  f"${int(kpis['INGRESOS_TOTAL'][0]):,}")
    except Exception as e:
        st.error(f"No se pudieron cargar los KPIs: {e}")
        return

    st.divider()

    # ---- Distribución por estado ----
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Órdenes por estado")
        df_estados = cached_query("""
            SELECT estado AS "Estado", COUNT(*) AS "Cantidad"
            FROM ORDENES_SERVICIO
            GROUP BY estado
            ORDER BY COUNT(*) DESC
        """, key="estados")
        if df_estados.empty:
            st.info("Sin datos para mostrar.")
        else:
            st.bar_chart(df_estados.set_index("Estado"))

    with col_b:
        st.subheader("Órdenes por técnico")
        df_tec = cached_query("""
            SELECT t.nombre AS "Técnico", COUNT(o.id_orden) AS "Órdenes"
            FROM TECNICOS t
            LEFT JOIN ORDENES_SERVICIO o ON o.id_tecnico = t.id_tecnico
            GROUP BY t.nombre
            ORDER BY COUNT(o.id_orden) DESC
        """, key="tecnicos_carga")
        if df_tec.empty:
            st.info("Sin datos para mostrar.")
        else:
            st.bar_chart(df_tec.set_index("Técnico"))

    st.divider()
    st.subheader("Órdenes recientes")
    df_recientes = run_query(f"""
        SELECT * FROM (
            {Q_ORDENES}
        ) WHERE ROWNUM <= 5
    """)
    st.dataframe(df_recientes, use_container_width=True, hide_index=True)


def page_clientes():
    st.title("👥 Clientes")

    tab_list, tab_new = st.tabs(["📋 Listado", "➕ Nuevo cliente"])

    # ---- Listado con búsqueda ----
    with tab_list:
        search = st.text_input("Buscar por nombre, documento o email", "")
        df = cached_query(Q_CLIENTES, key="clientes")
        if search:
            mask = (
                df["Nombre"].str.contains(search, case=False, na=False)
                | df["Documento"].str.contains(search, case=False, na=False)
                | df["Email"].fillna("").str.contains(search, case=False, na=False)
            )
            df = df[mask]
        st.caption(f"{len(df)} cliente(s) encontrado(s)")
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ---- Formulario de creación ----
    with tab_new:
        with st.form("form_cliente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            documento = col1.text_input("Documento *", max_chars=20)
            nombre    = col2.text_input("Nombre completo *", max_chars=100)
            telefono  = col1.text_input("Teléfono", max_chars=20)
            email     = col2.text_input("Email", max_chars=100)
            direccion = col1.text_input("Dirección", max_chars=200)
            ciudad    = col2.text_input("Ciudad", value="Cali", max_chars=60)
            submitted = st.form_submit_button("Guardar cliente", type="primary")

            if submitted:
                # Validación básica en la app (la BD también valida)
                if not documento.strip() or not nombre.strip():
                    st.error("Documento y Nombre son obligatorios.")
                elif len(nombre.strip()) < 3:
                    st.error("El nombre debe tener al menos 3 caracteres.")
                elif email and ("@" not in email or "." not in email):
                    st.error("Formato de email inválido.")
                else:
                    try:
                        run_dml("""
                            INSERT INTO CLIENTES
                                (id_cliente, documento, nombre, telefono, email, direccion, ciudad)
                            VALUES
                                (seq_cliente.NEXTVAL, :doc, :nom, :tel, :mail, :dir, :ciu)
                        """, {
                            "doc":  documento.strip(),
                            "nom":  nombre.strip(),
                            "tel":  telefono.strip() or None,
                            "mail": email.strip() or None,
                            "dir":  direccion.strip() or None,
                            "ciu":  ciudad.strip() or "Cali",
                        })
                        clear_cache()
                        st.success(f"✅ Cliente '{nombre}' creado correctamente.")
                    except oracledb.IntegrityError as e:
                        st.error(f"❌ Violación de integridad: documento duplicado o datos inválidos.\n\n{e}")
                    except Exception as e:
                        st.error(f"❌ Error al guardar: {e}")


def page_tecnicos():
    st.title("🛠️ Técnicos")

    tab_list, tab_new = st.tabs(["📋 Listado", "➕ Nuevo técnico"])

    with tab_list:
        col_f1, col_f2 = st.columns([1, 1])
        f_esp    = col_f1.selectbox("Especialidad", ["TODAS", "HARDWARE", "SOFTWARE", "REDES", "MIXTO"])
        f_activo = col_f2.selectbox("Estado", ["TODOS", "Activos", "Inactivos"])

        df = cached_query(Q_TECNICOS, key="tecnicos")
        if f_esp != "TODAS":
            df = df[df["Especialidad"] == f_esp]
        if f_activo == "Activos":
            df = df[df["Activo"] == "S"]
        elif f_activo == "Inactivos":
            df = df[df["Activo"] == "N"]
        st.caption(f"{len(df)} técnico(s)")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_new:
        with st.form("form_tecnico", clear_on_submit=True):
            col1, col2 = st.columns(2)
            documento    = col1.text_input("Documento *", max_chars=20)
            nombre       = col2.text_input("Nombre completo *", max_chars=100)
            especialidad = col1.selectbox("Especialidad *", ["HARDWARE", "SOFTWARE", "REDES", "MIXTO"])
            telefono     = col2.text_input("Teléfono", max_chars=20)
            fecha_contr  = col1.date_input("Fecha de contratación *", value=date.today())
            activo       = col2.selectbox("Activo *", ["S", "N"], index=0)
            submitted    = st.form_submit_button("Guardar técnico", type="primary")

            if submitted:
                if not documento.strip() or not nombre.strip():
                    st.error("Documento y Nombre son obligatorios.")
                elif fecha_contr > date.today():
                    st.error("La fecha de contratación no puede ser futura.")
                else:
                    try:
                        run_dml("""
                            INSERT INTO TECNICOS
                                (id_tecnico, documento, nombre, especialidad,
                                 telefono, fecha_contratacion, activo)
                            VALUES
                                (seq_tecnico.NEXTVAL, :doc, :nom, :esp,
                                 :tel, :fc, :act)
                        """, {
                            "doc": documento.strip(),
                            "nom": nombre.strip(),
                            "esp": especialidad,
                            "tel": telefono.strip() or None,
                            "fc":  datetime.combine(fecha_contr, datetime.min.time()),
                            "act": activo,
                        })
                        clear_cache()
                        st.success(f"✅ Técnico '{nombre}' registrado.")
                    except oracledb.IntegrityError as e:
                        st.error(f"❌ Documento duplicado u otro conflicto.\n\n{e}")
                    except Exception as e:
                        st.error(f"❌ Error al guardar: {e}")


def page_equipos():
    st.title("💻 Equipos")

    tab_list, tab_new = st.tabs(["📋 Listado", "➕ Nuevo equipo"])

    with tab_list:
        col_f1, col_f2 = st.columns(2)
        f_tipo  = col_f1.selectbox("Tipo",
            ["TODOS","LAPTOP","DESKTOP","IMPRESORA","CELULAR","TABLET","OTRO"])
        f_marca = col_f2.text_input("Marca contiene", "")

        df = cached_query(Q_EQUIPOS, key="equipos")
        if f_tipo != "TODOS":
            df = df[df["Tipo"] == f_tipo]
        if f_marca:
            df = df[df["Marca"].str.contains(f_marca, case=False, na=False)]
        st.caption(f"{len(df)} equipo(s)")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_new:
        clientes = cached_query("SELECT id_cliente AS id, nombre FROM CLIENTES ORDER BY nombre", key="cli_select")
        if clientes.empty:
            st.warning("Primero registra al menos un cliente.")
            return

        with st.form("form_equipo", clear_on_submit=True):
            cliente_label = st.selectbox(
                "Cliente *",
                clientes.apply(lambda r: f"{r['ID']} - {r['NOMBRE']}", axis=1).tolist()
            )
            cliente_id = int(cliente_label.split(" - ")[0])

            col1, col2 = st.columns(2)
            tipo   = col1.selectbox("Tipo *", ["LAPTOP","DESKTOP","IMPRESORA","CELULAR","TABLET","OTRO"])
            marca  = col2.text_input("Marca *", max_chars=50)
            modelo = col1.text_input("Modelo", max_chars=80)
            serial = col2.text_input("Serial", max_chars=60)
            anio   = col1.number_input("Año de compra", min_value=1990, max_value=2100,
                                       value=date.today().year, step=1)
            submitted = st.form_submit_button("Guardar equipo", type="primary")

            if submitted:
                if not marca.strip():
                    st.error("La marca es obligatoria.")
                else:
                    try:
                        run_dml("""
                            INSERT INTO EQUIPOS
                                (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
                            VALUES
                                (seq_equipo.NEXTVAL, :cli, :tipo, :marca, :mod, :ser, :anio)
                        """, {
                            "cli":   cliente_id,
                            "tipo":  tipo,
                            "marca": marca.strip(),
                            "mod":   modelo.strip() or None,
                            "ser":   serial.strip() or None,
                            "anio":  int(anio),
                        })
                        clear_cache()
                        st.success(f"✅ Equipo {marca} agregado al cliente.")
                    except oracledb.IntegrityError as e:
                        st.error(f"❌ Serial duplicado o cliente inexistente.\n\n{e}")
                    except Exception as e:
                        st.error(f"❌ Error al guardar: {e}")


def page_ordenes():
    st.title("📦 Órdenes de Servicio")

    tab_list, tab_new, tab_upd = st.tabs(
        ["📋 Listado y filtros", "➕ Nueva orden", "✏️ Actualizar estado"]
    )

    # ---- Listado con filtros ----
    with tab_list:
        col_f1, col_f2, col_f3 = st.columns(3)
        f_estado = col_f1.selectbox("Estado",
            ["TODOS","RECIBIDA","EN_DIAGNOSTICO","EN_REPARACION","LISTA","ENTREGADA","CANCELADA"])
        f_prio   = col_f2.selectbox("Prioridad", ["TODAS","ALTA","MEDIA","BAJA"])
        f_busq   = col_f3.text_input("Cliente o técnico contiene", "")

        df = run_query(Q_ORDENES)
        if f_estado != "TODOS":
            df = df[df["Estado"] == f_estado]
        if f_prio != "TODAS":
            df = df[df["Prioridad"] == f_prio]
        if f_busq:
            mask = (df["Cliente"].str.contains(f_busq, case=False, na=False)
                    | df["Técnico"].str.contains(f_busq, case=False, na=False))
            df = df[mask]
        st.caption(f"{len(df)} orden(es)")
        st.dataframe(df, use_container_width=True, hide_index=True)

        if not df.empty:
            total = df["Total ($)"].sum()
            st.metric("Total facturado en la selección (COP)", f"${int(total):,}")

    # ---- Nueva orden ----
    with tab_new:
        equipos  = cached_query("""
            SELECT e.id_equipo AS id,
                   c.nombre || ' | ' || e.tipo || ' ' || e.marca AS label
            FROM EQUIPOS e JOIN CLIENTES c ON c.id_cliente = e.id_cliente
            ORDER BY c.nombre
        """, key="eq_select")
        tecnicos = cached_query(
            "SELECT id_tecnico AS id, nombre FROM TECNICOS WHERE activo='S' ORDER BY nombre",
            key="tec_select"
        )

        if equipos.empty or tecnicos.empty:
            st.warning("Necesitas equipos y técnicos activos antes de crear una orden.")
            return

        with st.form("form_orden", clear_on_submit=True):
            eq_label  = st.selectbox("Equipo *", equipos["LABEL"].tolist())
            eq_id     = int(equipos.loc[equipos["LABEL"] == eq_label, "ID"].iloc[0])

            tec_label = st.selectbox(
                "Técnico asignado *",
                tecnicos.apply(lambda r: f"{r['ID']} - {r['NOMBRE']}", axis=1).tolist()
            )
            tec_id    = int(tec_label.split(" - ")[0])

            descripcion = st.text_area("Descripción del problema *", max_chars=500, height=100)
            col1, col2  = st.columns(2)
            prioridad   = col1.selectbox("Prioridad *", ["BAJA","MEDIA","ALTA"], index=1)
            f_ingreso   = col2.date_input("Fecha de ingreso *", value=date.today())

            submitted = st.form_submit_button("Crear orden", type="primary")

            if submitted:
                if not descripcion.strip():
                    st.error("La descripción del problema es obligatoria.")
                elif f_ingreso > date.today():
                    st.error("La fecha de ingreso no puede ser futura.")
                else:
                    try:
                        run_dml("""
                            INSERT INTO ORDENES_SERVICIO
                                (id_orden, id_equipo, id_tecnico, fecha_ingreso,
                                 descripcion_problema, estado, prioridad)
                            VALUES
                                (seq_orden.NEXTVAL, :eq, :tec, :fi,
                                 :desc, 'RECIBIDA', :prio)
                        """, {
                            "eq":   eq_id,
                            "tec":  tec_id,
                            "fi":   datetime.combine(f_ingreso, datetime.min.time()),
                            "desc": descripcion.strip(),
                            "prio": prioridad,
                        })
                        clear_cache()
                        st.success("✅ Orden creada con estado RECIBIDA.")
                    except Exception as e:
                        st.error(f"❌ Error al crear la orden: {e}")

    # ---- Actualizar estado / diagnóstico / costos ----
    with tab_upd:
        df_abiertas = run_query("""
            SELECT o.id_orden, o.estado, o.diagnostico,
                   o.costo_mano_obra, o.costo_repuestos,
                   c.nombre AS cliente
            FROM ORDENES_SERVICIO o
            JOIN EQUIPOS  e ON e.id_equipo  = o.id_equipo
            JOIN CLIENTES c ON c.id_cliente = e.id_cliente
            WHERE o.estado NOT IN ('ENTREGADA','CANCELADA')
            ORDER BY o.id_orden
        """)

        if df_abiertas.empty:
            st.info("No hay órdenes abiertas para actualizar.")
            return

        label = st.selectbox(
            "Selecciona la orden",
            df_abiertas.apply(
                lambda r: f"#{r['ID_ORDEN']} - {r['CLIENTE']} ({r['ESTADO']})", axis=1
            ).tolist()
        )
        orden_id = int(label.split(" ")[0].lstrip("#"))
        actual   = df_abiertas[df_abiertas["ID_ORDEN"] == orden_id].iloc[0]

        with st.form("form_update", clear_on_submit=False):
            nuevo_estado = st.selectbox(
                "Nuevo estado *",
                ["RECIBIDA","EN_DIAGNOSTICO","EN_REPARACION","LISTA","ENTREGADA","CANCELADA"],
                index=["RECIBIDA","EN_DIAGNOSTICO","EN_REPARACION","LISTA","ENTREGADA","CANCELADA"].index(actual["ESTADO"])
            )
            diagnostico = st.text_area("Diagnóstico", value=actual["DIAGNOSTICO"] or "",
                                       max_chars=500, height=100)
            col1, col2 = st.columns(2)
            mano_obra  = col1.number_input("Costo mano de obra (COP)",
                                            min_value=0.0,
                                            value=float(actual["COSTO_MANO_OBRA"]),
                                            step=1000.0)
            repuestos  = col2.number_input("Costo repuestos (COP)",
                                            min_value=0.0,
                                            value=float(actual["COSTO_REPUESTOS"]),
                                            step=1000.0)
            f_entrega  = st.date_input("Fecha de entrega (si aplica)", value=None)

            submitted = st.form_submit_button("Actualizar orden", type="primary")
            if submitted:
                if nuevo_estado == "ENTREGADA" and not f_entrega:
                    st.error("Para marcar como ENTREGADA debes indicar la fecha de entrega.")
                else:
                    try:
                        run_dml("""
                            UPDATE ORDENES_SERVICIO
                            SET estado          = :est,
                                diagnostico     = :diag,
                                costo_mano_obra = :mo,
                                costo_repuestos = :rep,
                                fecha_entrega   = :fe
                            WHERE id_orden = :id
                        """, {
                            "est":  nuevo_estado,
                            "diag": diagnostico.strip() or None,
                            "mo":   float(mano_obra),
                            "rep":  float(repuestos),
                            "fe":   datetime.combine(f_entrega, datetime.min.time()) if f_entrega else None,
                            "id":   orden_id,
                        })
                        clear_cache()
                        st.success(f"✅ Orden #{orden_id} actualizada.")
                    except oracledb.DatabaseError as e:
                        st.error(f"❌ Error de validación (revisa fechas y costos): {e}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")


# =====================================================================
# RUTEO / MENÚ LATERAL
# =====================================================================

PAGES = {
    "📊 Dashboard":       page_dashboard,
    "👥 Clientes":         page_clientes,
    "🛠️ Técnicos":         page_tecnicos,
    "💻 Equipos":          page_equipos,
    "📦 Órdenes":          page_ordenes,
}

def main():
    with st.sidebar:
        st.title("🔧 TecniServ")
        st.caption("Proyecto Final · BI 2026-I")
        choice = st.radio("Navegación", list(PAGES.keys()), label_visibility="collapsed")
        st.divider()
        if st.button("🔄 Refrescar caché"):
            clear_cache()
            st.success("Caché limpio.")
        st.caption("Conectado a Oracle Cloud")

    PAGES[choice]()


if __name__ == "__main__":
    main()
