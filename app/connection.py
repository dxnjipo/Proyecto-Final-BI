"""
connection.py
-------------
Módulo de conexión a Oracle Database para el proyecto final.

Soporta:
  - Oracle Cloud Autonomous Database (con wallet)
  - Oracle Database tradicional (con DSN o EZCONNECT)
  - Modo thick (con Oracle Instant Client) o thin (puro Python)

Las credenciales se leen de variables de entorno (archivo .env).
NUNCA se hardcodean en el código.
"""

import os
import oracledb
from dotenv import load_dotenv

# Cargar variables del .env si existe
load_dotenv()

# Flag para inicializar el cliente Oracle una sola vez
_oracle_client_initialized = False


def _init_oracle_client() -> None:
    """
    Inicializa el cliente Oracle en modo thick si así se solicita.
    Idempotente: solo corre la primera vez.
    """
    global _oracle_client_initialized
    if _oracle_client_initialized:
        return

    use_thick = os.getenv("ORACLE_THICK_MODE", "true").lower() == "true"

    if use_thick:
        lib_dir = os.getenv("ORACLE_CLIENT_LIB_DIR")  # ej: C:\oracle\instantclient_21_12
        try:
            if lib_dir:
                oracledb.init_oracle_client(lib_dir=lib_dir)
            else:
                oracledb.init_oracle_client()  # busca el client en PATH/LD_LIBRARY_PATH
        except oracledb.ProgrammingError:
            # Ya estaba inicializado en este proceso
            pass

    _oracle_client_initialized = True


def get_connection() -> oracledb.Connection:
    """
    Retorna una conexión nueva a Oracle.

    Variables de entorno requeridas:
        ORACLE_USER      - usuario de la base
        ORACLE_PASSWORD  - contraseña
        ORACLE_DSN       - DSN o nombre TNS (ej: 'tecniserv_high' o 'host:1521/SERVICE')

    Variables opcionales:
        ORACLE_THICK_MODE      - 'true' (default) | 'false'
        ORACLE_CLIENT_LIB_DIR  - ruta al Oracle Instant Client (modo thick)
        ORACLE_WALLET_DIR      - carpeta del wallet (Oracle Cloud)
        ORACLE_WALLET_PASSWORD - clave del wallet (si aplica)
    """
    _init_oracle_client()

    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")

    if not all([user, password, dsn]):
        raise RuntimeError(
            "Faltan variables de entorno: ORACLE_USER, ORACLE_PASSWORD y "
            "ORACLE_DSN son obligatorias. Revisa tu archivo .env."
        )

    kwargs = {"user": user, "password": password, "dsn": dsn}

    wallet_dir = os.getenv("ORACLE_WALLET_DIR")
    if wallet_dir:
        # Oracle Cloud Autonomous Database
        kwargs["config_dir"] = wallet_dir
        kwargs["wallet_location"] = wallet_dir
        wallet_pw = os.getenv("ORACLE_WALLET_PASSWORD")
        if wallet_pw:
            kwargs["wallet_password"] = wallet_pw

    return oracledb.connect(**kwargs)


def test_connection() -> bool:
    """Prueba rápida: intenta conectarse y ejecutar SELECT 1."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM dual")
                return cur.fetchone()[0] == 1
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False


if __name__ == "__main__":
    # Ejecutar `python connection.py` para verificar la conexión
    print("Probando conexión a Oracle...")
    if test_connection():
        print("✓ Conexión exitosa")
    else:
        print("✗ No se pudo conectar. Revisa tus variables de entorno.")
