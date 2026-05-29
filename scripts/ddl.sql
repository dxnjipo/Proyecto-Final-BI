-- =====================================================================
-- PROYECTO FINAL - BI para decisiones estratégicas
-- Sistema: Gestión de Órdenes de Servicio Técnico (TecniServ)
-- Archivo: ddl.sql
-- Descripción: Definición del esquema relacional con restricciones
--              justificadas por las reglas del negocio.
-- =====================================================================

-- ---------------------------------------------------------------------
-- LIMPIEZA: permite correr el script desde cero (DROP + CREATE)
-- Se borran en orden inverso a las dependencias.
-- ---------------------------------------------------------------------
BEGIN
    FOR t IN (SELECT table_name FROM user_tables
              WHERE table_name IN ('ORDENES_SERVICIO','EQUIPOS','TECNICOS','CLIENTES'))
    LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS';
    END LOOP;
END;
/

BEGIN
    FOR s IN (SELECT sequence_name FROM user_sequences
              WHERE sequence_name IN ('SEQ_CLIENTE','SEQ_TECNICO','SEQ_EQUIPO','SEQ_ORDEN'))
    LOOP
        EXECUTE IMMEDIATE 'DROP SEQUENCE ' || s.sequence_name;
    END LOOP;
END;
/

-- =====================================================================
-- TABLA: CLIENTES
-- Almacena los clientes (personas o empresas) que llevan equipos al
-- taller. El documento es único porque identifica legalmente al cliente
-- y el email tiene formato validado.
-- =====================================================================
CREATE TABLE CLIENTES (
    id_cliente      NUMBER(10)      NOT NULL,
    documento       VARCHAR2(20)    NOT NULL,
    nombre          VARCHAR2(100)   NOT NULL,
    telefono        VARCHAR2(20),
    email           VARCHAR2(100),
    direccion       VARCHAR2(200),
    ciudad          VARCHAR2(60)    DEFAULT 'Cali' NOT NULL,
    fecha_registro  DATE            DEFAULT SYSDATE NOT NULL,

    CONSTRAINT pk_clientes        PRIMARY KEY (id_cliente),
    CONSTRAINT uk_clientes_doc    UNIQUE (documento),
    CONSTRAINT ck_clientes_email  CHECK (email IS NULL OR email LIKE '%_@_%._%'),
    CONSTRAINT ck_clientes_nombre CHECK (LENGTH(TRIM(nombre)) >= 3)
);

COMMENT ON TABLE  CLIENTES               IS 'Clientes registrados en el taller';
COMMENT ON COLUMN CLIENTES.documento     IS 'Cédula o NIT, único en el sistema';
COMMENT ON COLUMN CLIENTES.fecha_registro IS 'Fecha en que el cliente fue creado';

-- =====================================================================
-- TABLA: TECNICOS
-- Personal del taller. La especialidad restringe los tipos de
-- intervención y el estado activo/inactivo permite mantener histórico
-- sin eliminar técnicos que ya no trabajan.
-- =====================================================================
CREATE TABLE TECNICOS (
    id_tecnico          NUMBER(10)    NOT NULL,
    documento           VARCHAR2(20)  NOT NULL,
    nombre              VARCHAR2(100) NOT NULL,
    especialidad        VARCHAR2(20)  NOT NULL,
    telefono            VARCHAR2(20),
    fecha_contratacion  DATE          DEFAULT SYSDATE NOT NULL,
    activo              CHAR(1)       DEFAULT 'S' NOT NULL,

    CONSTRAINT pk_tecnicos          PRIMARY KEY (id_tecnico),
    CONSTRAINT uk_tecnicos_doc      UNIQUE (documento),
    CONSTRAINT ck_tecnicos_esp      CHECK (especialidad IN ('HARDWARE','SOFTWARE','REDES','MIXTO')),
    CONSTRAINT ck_tecnicos_activo   CHECK (activo IN ('S','N'))
);

COMMENT ON TABLE  TECNICOS              IS 'Técnicos que atienden las órdenes de servicio';
COMMENT ON COLUMN TECNICOS.especialidad IS 'Área de competencia del técnico';
COMMENT ON COLUMN TECNICOS.activo       IS 'S=activo, N=inactivo (no se elimina por integridad histórica)';

-- =====================================================================
-- TABLA: EQUIPOS
-- Equipos que pertenecen a los clientes. Un cliente puede tener varios
-- equipos. ON DELETE CASCADE: si se borra un cliente, se borran sus
-- equipos (los equipos no tienen sentido sin dueño).
-- =====================================================================
CREATE TABLE EQUIPOS (
    id_equipo    NUMBER(10)    NOT NULL,
    id_cliente   NUMBER(10)    NOT NULL,
    tipo         VARCHAR2(20)  NOT NULL,
    marca        VARCHAR2(50)  NOT NULL,
    modelo       VARCHAR2(80),
    serial       VARCHAR2(60),
    anio_compra  NUMBER(4),

    CONSTRAINT pk_equipos        PRIMARY KEY (id_equipo),
    CONSTRAINT fk_equipos_cli    FOREIGN KEY (id_cliente)
                                 REFERENCES CLIENTES (id_cliente)
                                 ON DELETE CASCADE,
    CONSTRAINT uk_equipos_serial UNIQUE (serial),
    CONSTRAINT ck_equipos_tipo   CHECK (tipo IN ('LAPTOP','DESKTOP','IMPRESORA','CELULAR','TABLET','OTRO')),
    CONSTRAINT ck_equipos_anio   CHECK (anio_compra IS NULL OR anio_compra BETWEEN 1990 AND 2100)
);

COMMENT ON TABLE  EQUIPOS        IS 'Equipos en custodia del taller, asociados a un cliente';
COMMENT ON COLUMN EQUIPOS.serial IS 'Serial de fábrica, único cuando se conoce';

-- =====================================================================
-- TABLA: ORDENES_SERVICIO
-- Núcleo del negocio. Cada orden vincula un equipo con un técnico.
-- ON DELETE RESTRICT (comportamiento por defecto) para equipo y técnico:
-- no se permite borrar un equipo o técnico que tenga órdenes asociadas,
-- porque se perdería el histórico contable y operativo.
-- =====================================================================
CREATE TABLE ORDENES_SERVICIO (
    id_orden              NUMBER(10)     NOT NULL,
    id_equipo             NUMBER(10)     NOT NULL,
    id_tecnico            NUMBER(10)     NOT NULL,
    fecha_ingreso         DATE           DEFAULT SYSDATE NOT NULL,
    fecha_entrega         DATE,
    descripcion_problema  VARCHAR2(500)  NOT NULL,
    diagnostico           VARCHAR2(500),
    estado                VARCHAR2(20)   DEFAULT 'RECIBIDA' NOT NULL,
    prioridad             VARCHAR2(10)   DEFAULT 'MEDIA'    NOT NULL,
    costo_mano_obra       NUMBER(10,2)   DEFAULT 0          NOT NULL,
    costo_repuestos       NUMBER(10,2)   DEFAULT 0          NOT NULL,

    CONSTRAINT pk_ordenes         PRIMARY KEY (id_orden),
    CONSTRAINT fk_ordenes_equipo  FOREIGN KEY (id_equipo)
                                  REFERENCES EQUIPOS (id_equipo),
    CONSTRAINT fk_ordenes_tecnico FOREIGN KEY (id_tecnico)
                                  REFERENCES TECNICOS (id_tecnico),
    CONSTRAINT ck_ordenes_estado    CHECK (estado IN
        ('RECIBIDA','EN_DIAGNOSTICO','EN_REPARACION','LISTA','ENTREGADA','CANCELADA')),
    CONSTRAINT ck_ordenes_prioridad CHECK (prioridad IN ('BAJA','MEDIA','ALTA')),
    CONSTRAINT ck_ordenes_mano_obra CHECK (costo_mano_obra >= 0),
    CONSTRAINT ck_ordenes_repuestos CHECK (costo_repuestos >= 0),
    CONSTRAINT ck_ordenes_fechas    CHECK (fecha_entrega IS NULL
                                           OR fecha_entrega >= fecha_ingreso)
);

COMMENT ON TABLE  ORDENES_SERVICIO                IS 'Órdenes de servicio técnico';
COMMENT ON COLUMN ORDENES_SERVICIO.estado         IS 'Flujo: RECIBIDA -> EN_DIAGNOSTICO -> EN_REPARACION -> LISTA -> ENTREGADA';
COMMENT ON COLUMN ORDENES_SERVICIO.costo_mano_obra IS 'Valor en COP cobrado por la labor del técnico';

-- =====================================================================
-- SECUENCIAS para generar las claves primarias.
-- (En Oracle 12c+ podríamos usar GENERATED AS IDENTITY, pero usar
--  secuencias explícitas es más portable y didáctico.)
-- =====================================================================
CREATE SEQUENCE seq_cliente START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_tecnico START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_equipo  START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_orden   START WITH 1 INCREMENT BY 1 NOCACHE;

-- =====================================================================
-- ÍNDICES adicionales sobre claves foráneas y campos de búsqueda.
-- Oracle no crea índices automáticos sobre FKs, y sin ellos los joins
-- y los DELETE de padres se vuelven lentos.
-- =====================================================================
CREATE INDEX idx_equipos_cliente  ON EQUIPOS (id_cliente);
CREATE INDEX idx_ordenes_equipo   ON ORDENES_SERVICIO (id_equipo);
CREATE INDEX idx_ordenes_tecnico  ON ORDENES_SERVICIO (id_tecnico);
CREATE INDEX idx_ordenes_estado   ON ORDENES_SERVICIO (estado);

COMMIT;
