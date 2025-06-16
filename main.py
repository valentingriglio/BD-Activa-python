import pymysql
from datetime import datetime

def conectar():
    try:
        return pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='root',
            database='DB',
            port=3306
        )
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def listar_empleados(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, nombre FROM Empleado;")
        empleados = cursor.fetchall()
    print("Empleados:")
    for emp in empleados:
        print(f"ID: {emp[0]}, Nombre: {emp[1]}")

def registrar_ausencia(conn):
    try:
        listar_empleados(conn)
        id_empleado = int(input("ID empleado: "))
        print("Tipos: enfermedad personal, enfermedad familiar, donación de sangre")
        tipo = input("Tipo ausencia: ").strip().lower()
        if tipo not in ('enfermedad personal', 'enfermedad familiar', 'donación de sangre'):
            print("Tipo inválido")
            return
        fecha_inicio = input("Fecha inicio (YYYY-MM-DD): ")
        fecha_fin = input("Fecha fin (YYYY-MM-DD): ")

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Ausencia (id_empleado, tipo, fecha_inicio, fecha_fin)
                VALUES (%s, %s, %s, %s);
            """, (id_empleado, tipo, fecha_inicio, fecha_fin))
            conn.commit()
            print("Ausencia registrada.")
    except Exception as e:
        print(f"Error al registrar ausencia: {e}")

def listar_ausencias(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, e.nombre, a.tipo, a.fecha_inicio, a.fecha_fin
            FROM Ausencia a JOIN Empleado e ON a.id_empleado = e.id
            ORDER BY a.fecha_inicio DESC;
        """)
        ausencias = cursor.fetchall()
    print("Ausencias:")
    for a in ausencias:
        print(f"ID: {a[0]}, Empleado: {a[1]}, Tipo: {a[2]}, Desde: {a[3]}, Hasta: {a[4]}")

def actualizar_ausencia(conn):
    try:
        listar_ausencias(conn)
        id_ausencia = int(input("ID ausencia a modificar: "))

        with conn.cursor() as cursor:
            cursor.execute("SELECT id_empleado, fecha_inicio, fecha_fin FROM Ausencia WHERE id=%s", (id_ausencia,))
            resultado = cursor.fetchone()
            if not resultado:
                print("Ausencia no encontrada")
                return
            id_empleado, old_inicio, old_fin = resultado

        print(f"Fecha inicio actual: {old_inicio}")
        new_inicio = input("Nueva fecha inicio (YYYY-MM-DD): ")
        print(f"Fecha fin actual: {old_fin}")
        new_fin = input("Nueva fecha fin (YYYY-MM-DD): ")
        usuario = input("Nombre usuario que modifica: ")
        fecha_mod = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Ausencia SET fecha_inicio=%s, fecha_fin=%s WHERE id=%s;
            """, (new_inicio, new_fin, id_ausencia))

            cursor.execute("""
                INSERT INTO Auditoria_Ausencia (id_empleado, old_fecha_inicio, new_fecha_inicio,
                old_fecha_fin, new_fecha_fin, usuario, fecha_modificacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (id_empleado, old_inicio, new_inicio, old_fin, new_fin, usuario, fecha_mod))

            conn.commit()
            print("Ausencia actualizada y auditoría registrada.")
    except Exception as e:
        print(f"Error al actualizar ausencia: {e}")

def consultar_vistas(conn):
    vistas = {
        "1": "vw_tipos_ausencias_mas_frecuentes",
        "2": "vw_empleados_mas_5_dias_ausencia",
        "3": "vw_empleado_mas_ausencias_anio_actual"
    }

    print("""
--- Vistas disponibles ---
1) Tipos de ausencias más frecuentes
2) Empleados con más de 5 días totales de ausencia
3) Empleado con más días de ausencia en el año actual
0) Volver al menú
""")
    opcion = input("Elegí una vista para consultar: ")

    if opcion == "0":
        return
    elif opcion in vistas:
        vista = vistas[opcion]
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {vista}")
                columnas = [desc[0] for desc in cursor.description]
                resultados = cursor.fetchall()

                print("\n" + " | ".join(columnas))
                print("-" * 50)
                for fila in resultados:
                    print(" | ".join(str(valor) for valor in fila))
        except Exception as e:
            print(f"Error al consultar la vista: {e}")
    else:
        print("Opción inválida") 

def menu():
    conn = conectar()
    if not conn:
        return

    while True:
        print("""
--- Menú ---
1) Registrar ausencia
2) Listar ausencias
3) Actualizar ausencia
4) Consultar vistas
0) Salir
""")
        opcion = input("Elegí una opción: ")
        if opcion == "1":
            registrar_ausencia(conn)
        elif opcion == "2":
            listar_ausencias(conn)
        elif opcion == "3":
            actualizar_ausencia(conn)
        elif opcion == "4":
            consultar_vistas(conn)
        elif opcion == "0":
            conn.close()
            print("Chau!")
            break
        else:
            print("Opción inválida")


if __name__ == "__main__":
    menu()