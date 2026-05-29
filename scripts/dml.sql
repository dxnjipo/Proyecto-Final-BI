-- =====================================================================
-- PROYECTO FINAL - BI para decisiones estratégicas
-- Archivo: dml.sql
-- Descripción: Datos de prueba representativos para todas las tablas.
--              Cumple con el mínimo de 5 registros por tabla principal.
-- =====================================================================

-- Limpieza para poder re-ejecutar el script
DELETE FROM ORDENES_SERVICIO;
DELETE FROM EQUIPOS;
DELETE FROM TECNICOS;
DELETE FROM CLIENTES;
COMMIT;

-- Resetear secuencias (DROP + CREATE manualmente si se requiere arrancar en 1)
-- En entornos limpios el ddl.sql ya las recrea desde 1.

-- =====================================================================
-- CLIENTES (8 registros)
-- =====================================================================
INSERT INTO CLIENTES (id_cliente, documento, nombre, telefono, email, direccion, ciudad)
VALUES (seq_cliente.NEXTVAL, '1144123456', 'Ana María Restrepo',  '3001234567', 'ana.restrepo@gmail.com',  'Av. 6N #23-45', 'Cali');

INSERT INTO CLIENTES (id_cliente, documento, nombre, telefono, email, direccion, ciudad)
VALUES (seq_cliente.NEXTVAL, '94567890',   'Carlos Andrés Lozano','3109876543', 'clozano@hotmail.com',     'Cra. 100 #15-80', 'Cali');

INSERT INTO CLIENTES (id_cliente, documento, nombre, telefono, email, direccion, ciudad)
VALUES (seq_cliente.NEXTVAL, '900123456-1','Distribuidora El Sol SAS','3215550000','contacto@elsol.com.co','Calle 13 #5-32',  'Cali');

INSERT INTO CLIENTES (id_cliente, documento, nombre, telefono, email, direccion, ciudad)
VALUES (seq_cliente.NEXTVAL, '1130567789', 'Laura Sofía Murillo', '3145557788', 'lmurillo@outlook.com',    'Cra. 66 #11-22', 'Cali');

INSERT INTO CLIENTES (id_cliente, documento, nombre, telefono, email, direccion, ciudad)
VALUES (seq_cliente.NEXTVAL, '16789012',   'Jorge Eliécer Pardo', '3187776655', 'jorgep@gmail.com',        'Calle 5 #38-12', 'Palmira');

INSERT INTO CLIENTES (id_cliente, documento, nombre, telefono, email, direccion, ciudad)
VALUES (seq_cliente.NEXTVAL, '1098765432', 'Diana Patricia Gómez','3023334455', 'dgomez@gmail.com',        'Cra. 80 #3-19',  'Cali');

INSERT INTO CLIENTES (id_cliente, documento, nombre, telefono, email, direccion, ciudad)
VALUES (seq_cliente.NEXTVAL, '901234567-3','Café del Valle Ltda', '3122223344', 'admin@cafedelvalle.co',   'Calle 9 #4-50',  'Cali');

INSERT INTO CLIENTES (id_cliente, documento, nombre, telefono, email, direccion, ciudad)
VALUES (seq_cliente.NEXTVAL, '1144998877', 'Felipe Andrés Cano',  '3009998877', 'fcano@yahoo.com',         'Av. 3N #45-10',  'Yumbo');

-- =====================================================================
-- TECNICOS (5 registros)
-- =====================================================================
INSERT INTO TECNICOS (id_tecnico, documento, nombre, especialidad, telefono, fecha_contratacion, activo)
VALUES (seq_tecnico.NEXTVAL, '1144000111', 'Andrés Felipe Ríos',   'HARDWARE', '3151112233', DATE '2022-03-15', 'S');

INSERT INTO TECNICOS (id_tecnico, documento, nombre, especialidad, telefono, fecha_contratacion, activo)
VALUES (seq_tecnico.NEXTVAL, '1144000222', 'María Camila Ospina',  'SOFTWARE', '3162223344', DATE '2023-01-10', 'S');

INSERT INTO TECNICOS (id_tecnico, documento, nombre, especialidad, telefono, fecha_contratacion, activo)
VALUES (seq_tecnico.NEXTVAL, '1144000333', 'Juan Sebastián Vélez', 'REDES',    '3173334455', DATE '2021-08-20', 'S');

INSERT INTO TECNICOS (id_tecnico, documento, nombre, especialidad, telefono, fecha_contratacion, activo)
VALUES (seq_tecnico.NEXTVAL, '1144000444', 'Valentina Torres',     'MIXTO',    '3184445566', DATE '2024-05-02', 'S');

INSERT INTO TECNICOS (id_tecnico, documento, nombre, especialidad, telefono, fecha_contratacion, activo)
VALUES (seq_tecnico.NEXTVAL, '1144000555', 'Ricardo Mejía',        'HARDWARE', '3195556677', DATE '2020-11-30', 'N');

-- =====================================================================
-- EQUIPOS (10 registros, repartidos entre los clientes)
-- =====================================================================
INSERT INTO EQUIPOS (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
VALUES (seq_equipo.NEXTVAL, 1, 'LAPTOP',    'HP',      'Pavilion 14',    'HP14X-001A', 2021);

INSERT INTO EQUIPOS (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
VALUES (seq_equipo.NEXTVAL, 1, 'IMPRESORA', 'Epson',   'L3250',          'EPS-L3250-22', 2022);

INSERT INTO EQUIPOS (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
VALUES (seq_equipo.NEXTVAL, 2, 'DESKTOP',   'Dell',    'OptiPlex 3090',  'DELL-OPT-3090-77', 2023);

INSERT INTO EQUIPOS (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
VALUES (seq_equipo.NEXTVAL, 3, 'LAPTOP',    'Lenovo',  'ThinkPad E14',   'LNV-TP-E14-512', 2023);

INSERT INTO EQUIPOS (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
VALUES (seq_equipo.NEXTVAL, 3, 'IMPRESORA', 'Brother', 'HL-L2360DW',     'BR-2360-9981', 2020);

INSERT INTO EQUIPOS (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
VALUES (seq_equipo.NEXTVAL, 4, 'CELULAR',   'Samsung', 'Galaxy A54',     'SM-A54-XYZ123', 2024);

INSERT INTO EQUIPOS (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
VALUES (seq_equipo.NEXTVAL, 5, 'LAPTOP',    'Asus',    'VivoBook 15',    'ASUS-VB15-7700', 2022);

INSERT INTO EQUIPOS (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
VALUES (seq_equipo.NEXTVAL, 6, 'TABLET',    'Apple',   'iPad 9th gen',   'IPAD-9G-44521', 2022);

INSERT INTO EQUIPOS (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
VALUES (seq_equipo.NEXTVAL, 7, 'DESKTOP',   'HP',      'EliteDesk 800',  'HP-ED800-3344', 2021);

INSERT INTO EQUIPOS (id_equipo, id_cliente, tipo, marca, modelo, serial, anio_compra)
VALUES (seq_equipo.NEXTVAL, 8, 'LAPTOP',    'Acer',    'Aspire 5',       'ACR-A5-88990', 2023);

-- =====================================================================
-- ORDENES_SERVICIO (12 registros con distintos estados y prioridades)
-- =====================================================================
INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 1, 1, DATE '2026-04-10', DATE '2026-04-12',
        'El equipo no enciende', 'Falla de fuente de poder, se reemplazó',
        'ENTREGADA', 'ALTA', 80000, 120000);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 2, 1, DATE '2026-04-15', DATE '2026-04-16',
        'Atasco de papel constante', 'Limpieza de rodillos y calibración',
        'ENTREGADA', 'MEDIA', 50000, 0);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 3, 2, DATE '2026-05-02', NULL,
        'Sistema operativo no inicia', 'Reinstalación de Windows en curso',
        'EN_REPARACION', 'ALTA', 120000, 0);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 4, 2, DATE '2026-05-05', DATE '2026-05-09',
        'Lentitud extrema al iniciar', 'Disco mecánico migrado a SSD, instalación de Windows 11',
        'ENTREGADA', 'MEDIA', 150000, 320000);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 5, 1, DATE '2026-05-10', NULL,
        'No imprime en color', 'Cabezal obstruido, esperando repuesto',
        'EN_DIAGNOSTICO', 'BAJA', 0, 0);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 6, 4, DATE '2026-05-12', DATE '2026-05-13',
        'Pantalla rota tras caída', 'Cambio de display y vidrio templado',
        'ENTREGADA', 'ALTA', 90000, 280000);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 7, 1, DATE '2026-05-18', NULL,
        'Se apaga solo al jugar', 'Posible recalentamiento, pendiente diagnóstico',
        'RECIBIDA', 'MEDIA', 0, 0);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 8, 2, DATE '2026-05-19', NULL,
        'Pantalla no responde al tacto', 'Cambio de digitalizador requerido',
        'LISTA', 'MEDIA', 70000, 180000);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 9, 3, DATE '2026-05-20', NULL,
        'No se conecta a la red corporativa', 'Configuración de DNS y proxy en proceso',
        'EN_REPARACION', 'ALTA', 60000, 0);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 10, 4, DATE '2026-05-21', NULL,
        'Teclado no responde varias teclas', 'Esperando teclado de reemplazo',
        'EN_DIAGNOSTICO', 'BAJA', 0, 0);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 1, 2, DATE '2026-05-22', NULL,
        'Reinstalación del sistema solicitada por el cliente', NULL,
        'RECIBIDA', 'BAJA', 0, 0);

INSERT INTO ORDENES_SERVICIO (id_orden, id_equipo, id_tecnico, fecha_ingreso, fecha_entrega,
                              descripcion_problema, diagnostico, estado, prioridad,
                              costo_mano_obra, costo_repuestos)
VALUES (seq_orden.NEXTVAL, 3, 3, DATE '2026-04-25', DATE '2026-04-25',
        'Cliente desistió de la reparación', 'Cancelación voluntaria',
        'CANCELADA', 'BAJA', 0, 0);

COMMIT;

-- Verificación rápida (descomentar para usar en SQL*Plus / SQL Developer)
-- SELECT 'CLIENTES' tabla, COUNT(*) total FROM CLIENTES
-- UNION ALL SELECT 'TECNICOS', COUNT(*) FROM TECNICOS
-- UNION ALL SELECT 'EQUIPOS',  COUNT(*) FROM EQUIPOS
-- UNION ALL SELECT 'ORDENES',  COUNT(*) FROM ORDENES_SERVICIO;
