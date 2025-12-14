import sqlite3
import csv


# --------------------------------------------------------
# Conexión
# --------------------------------------------------------

def conectar_db(nombre_db):
    conexion = sqlite3.connect(nombre_db)
    cursor = conexion.cursor()
    return conexion, cursor


# --------------------------------------------------------
# CSV 01
# --------------------------------------------------------

def generar_csv_01(cursor):
    cursor.execute("""
        SELECT SUM(votos_comuna_candidato.cant_votos)
        FROM votos_comuna_candidato
        JOIN candidato
            ON votos_comuna_candidato.candidato_id = candidato.candidato_id
        WHERE candidato.cargo = 'Diputado'
    """)
    filas_total = cursor.fetchall()
    total_votos_diputado = filas_total[0][0]

    cursor.execute("""
        SELECT partido.nombre,
               partido.orientacion,
               SUM(votos_comuna_candidato.cant_votos)
        FROM votos_comuna_candidato
        JOIN candidato
            ON votos_comuna_candidato.candidato_id = candidato.candidato_id
        JOIN partido
            ON candidato.partido_id = partido.partido_id
        WHERE candidato.cargo = 'Diputado'
        GROUP BY partido.partido_id, partido.nombre, partido.orientacion
        ORDER BY SUM(votos_comuna_candidato.cant_votos) DESC
    """)
    filas_partidos_dip = cursor.fetchall()

    f = open("01_results_diputados_totales_vis.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(f)
    writer.writerow(["partido_nombre", "votos", "percent", "orientacion"])

    for fila in filas_partidos_dip:
        nombre_partido = fila[0]
        orientacion = fila[1]
        votos = fila[2]

        if total_votos_diputado > 0:
            porcentaje = round(votos * 100.0 / total_votos_diputado, 2)
        else:
            porcentaje = 0.0

        writer.writerow([nombre_partido, votos, porcentaje, orientacion])

    f.close()


# --------------------------------------------------------
# CSV 02
# --------------------------------------------------------

def generar_csv_02(cursor):
    cursor.execute("""
        SELECT SUM(votos_comuna_candidato.cant_votos)
        FROM votos_comuna_candidato
        JOIN candidato
            ON votos_comuna_candidato.candidato_id = candidato.candidato_id
        WHERE candidato.cargo = 'Diputado'
    """)
    filas_total = cursor.fetchall()
    total_votos_diputado = filas_total[0][0]

    cursor.execute("""
        SELECT partido.orientacion,
               SUM(votos_comuna_candidato.cant_votos)
        FROM votos_comuna_candidato
        JOIN candidato
            ON votos_comuna_candidato.candidato_id = candidato.candidato_id
        JOIN partido
            ON candidato.partido_id = partido.partido_id
        WHERE candidato.cargo = 'Diputado'
        GROUP BY partido.orientacion
        ORDER BY SUM(votos_comuna_candidato.cant_votos) DESC
    """)
    filas_orientacion = cursor.fetchall()

    f = open("02_results_diputados_totales_vis.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(f)
    writer.writerow(["orientacion", "votos", "percent"])

    for fila in filas_orientacion:
        orientacion = fila[0]
        votos = fila[1]

        if total_votos_diputado > 0:
            porcentaje = round(votos * 100.0 / total_votos_diputado, 2)
        else:
            porcentaje = 0.0

        writer.writerow([orientacion, votos, porcentaje])

    f.close()


# --------------------------------------------------------
# Auxiliares para comunas
# --------------------------------------------------------

def cargar_totales_por_comuna(cursor, cargo):
    cursor.execute("""
        SELECT comuna.comuna_id,
               comuna.nombre,
               SUM(votos_comuna_candidato.cant_votos)
        FROM votos_comuna_candidato
        JOIN candidato
            ON votos_comuna_candidato.candidato_id = candidato.candidato_id
        JOIN comuna
            ON votos_comuna_candidato.comuna_id = comuna.comuna_id
        WHERE candidato.cargo = ?
        GROUP BY comuna.comuna_id, comuna.nombre
        ORDER BY comuna.comuna_id
    """, (cargo,))

    filas = cursor.fetchall()

    totales_por_comuna = {}
    nombres_comuna = {}

    for fila in filas:
        comuna_id = fila[0]
        nombre = fila[1]
        total = fila[2]
        totales_por_comuna[comuna_id] = total
        nombres_comuna[comuna_id] = nombre

    return totales_por_comuna, nombres_comuna


# --------------------------------------------------------
# CSV 03
# --------------------------------------------------------

def generar_csv_03(cursor, totales_dip_por_comuna, nombres_comuna):
    cursor.execute("""
        SELECT comuna.comuna_id,
               comuna.nombre,
               partido.nombre,
               SUM(votos_comuna_candidato.cant_votos)
        FROM votos_comuna_candidato
        JOIN candidato
            ON votos_comuna_candidato.candidato_id = candidato.candidato_id
        JOIN partido
            ON candidato.partido_id = partido.partido_id
        JOIN comuna
            ON votos_comuna_candidato.comuna_id = comuna.comuna_id
        WHERE candidato.cargo = 'Diputado'
        GROUP BY comuna.comuna_id, comuna.nombre, partido.partido_id, partido.nombre
        ORDER BY comuna.comuna_id, SUM(votos_comuna_candidato.cant_votos) DESC
    """)
    filas_votos_dip = cursor.fetchall()

    votos_dip_por_comuna = {}
    for fila in filas_votos_dip:
        comuna_id = fila[0]
        nombre_partido = fila[2]
        votos = fila[3]

        if comuna_id not in votos_dip_por_comuna:
            votos_dip_por_comuna[comuna_id] = []
        votos_dip_por_comuna[comuna_id].append((nombre_partido, votos))

    f = open("03_results_diputados_totales_per_comuna_vis.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(f)
    writer.writerow([
        "comuna",
        "partido_primero", "porc_primero", "votos_primero",
        "partido_segundo", "porc_segundo", "votos_segundo",
        "partido_tercero", "porc_tercero", "votos_tercero",
        "partido_cuarto", "porc_cuarto", "votos_cuarto"
    ])

    for comuna_id in sorted(votos_dip_por_comuna):
        total_comuna = totales_dip_por_comuna[comuna_id]
        lista_partidos = votos_dip_por_comuna[comuna_id]
        top4 = lista_partidos[:4]

        while len(top4) < 4:
            top4.append(("", 0))

        fila_salida = [nombres_comuna[comuna_id]]

        for nombre_partido, votos in top4:
            if total_comuna > 0:
                porcentaje = round(votos * 100.0 / total_comuna, 2)
            else:
                porcentaje = 0.0

            fila_salida.append(nombre_partido)
            fila_salida.append(porcentaje)
            fila_salida.append(votos)

        writer.writerow(fila_salida)

    f.close()


# --------------------------------------------------------
# CSV 04
# --------------------------------------------------------

def generar_csv_04(cursor, totales_sen_por_comuna):
    cursor.execute("""
        SELECT comuna.comuna_id,
               comuna.nombre,
               partido.nombre,
               SUM(votos_comuna_candidato.cant_votos)
        FROM votos_comuna_candidato
        JOIN candidato
            ON votos_comuna_candidato.candidato_id = candidato.candidato_id
        JOIN partido
            ON candidato.partido_id = partido.partido_id
        JOIN comuna
            ON votos_comuna_candidato.comuna_id = comuna.comuna_id
        WHERE candidato.cargo = 'Senador'
        GROUP BY comuna.comuna_id, comuna.nombre, partido.partido_id, partido.nombre
        ORDER BY comuna.comuna_id, SUM(votos_comuna_candidato.cant_votos) DESC
    """)
    filas_votos_sen = cursor.fetchall()

    votos_sen_por_comuna = {}
    for fila in filas_votos_sen:
        comuna_id = fila[0]
        nombre_partido = fila[2]
        votos = fila[3]

        if comuna_id not in votos_sen_por_comuna:
            votos_sen_por_comuna[comuna_id] = []
        votos_sen_por_comuna[comuna_id].append((nombre_partido, votos))

    cursor.execute("SELECT comuna_id, nombre, lat, long FROM comuna")
    filas_comunas = cursor.fetchall()

    info_comuna = {}
    for fila in filas_comunas:
        comuna_id = fila[0]
        nombre = fila[1]
        lat = fila[2]
        lon = fila[3]
        info_comuna[comuna_id] = (nombre, lat, lon)

    f = open("04_diff_senadores_per_comuna_vis.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(f)
    writer.writerow([
        "comuna", "LAT", "LON",
        "partido_primero", "porc_primero", "votos_primero",
        "partido_segundo", "porc_segundo", "votos_segundo",
        "dif_primero_segundo"
    ])

    for comuna_id in sorted(votos_sen_por_comuna):
        total_comuna = totales_sen_por_comuna[comuna_id]
        lista_partidos = votos_sen_por_comuna[comuna_id]
        top2 = lista_partidos[:2]

        while len(top2) < 2:
            top2.append(("", 0))

        partido1, votos1 = top2[0]
        partido2, votos2 = top2[1]

        if total_comuna > 0:
            porc1 = round(votos1 * 100.0 / total_comuna, 2)
            porc2 = round(votos2 * 100.0 / total_comuna, 2)
        else:
            porc1 = 0.0
            porc2 = 0.0

        diferencia = votos1 - votos2

        nombre_comuna, lat, lon = info_comuna[comuna_id]

        writer.writerow([
            nombre_comuna, lat, lon,
            partido1, porc1, votos1,
            partido2, porc2, votos2,
            diferencia
        ])

    f.close()


# --------------------------------------------------------
# CSV 05
# --------------------------------------------------------

def generar_csv_05(cursor, totales_sen_por_comuna):
    cursor.execute("""
        SELECT comuna.comuna_id,
               partido.nombre,
               SUM(votos_comuna_candidato.cant_votos)
        FROM votos_comuna_candidato
        JOIN candidato
            ON votos_comuna_candidato.candidato_id = candidato.candidato_id
        JOIN partido
            ON candidato.partido_id = partido.partido_id
        JOIN comuna
            ON votos_comuna_candidato.comuna_id = comuna.comuna_id
        WHERE candidato.cargo = 'Senador'
        GROUP BY comuna.comuna_id, partido.partido_id, partido.nombre
        ORDER BY partido.nombre, comuna.comuna_id
    """)
    filas_sen_5 = cursor.fetchall()

    porcentajes_partido_comuna = {}

    for fila in filas_sen_5:
        comuna_id = fila[0]
        nombre_partido = fila[1]
        votos = fila[2]
        total_comuna = totales_sen_por_comuna[comuna_id]

        if total_comuna > 0:
            porcentaje = round(votos * 100.0 / total_comuna, 2)
        else:
            porcentaje = 0.0

        if nombre_partido not in porcentajes_partido_comuna:
            porcentajes_partido_comuna[nombre_partido] = {}

        porcentajes_partido_comuna[nombre_partido][comuna_id] = porcentaje

    partidos_validos = []
    for nombre_partido in porcentajes_partido_comuna:
        valores = list(porcentajes_partido_comuna[nombre_partido].values())
        if len(valores) > 0 and max(valores) > 5.0:
            partidos_validos.append(nombre_partido)

    partidos_validos.sort()

    f = open("05_partidos_greater_than_5.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(f)

    encabezados = ["partido"]
    for i in range(1, 16):
        if i < 10:
            encabezados.append("0" + str(i))
        else:
            encabezados.append(str(i))
    writer.writerow(encabezados)

    for nombre_partido in partidos_validos:
        fila_salida = [nombre_partido]
        for i in range(1, 16):
            if i in porcentajes_partido_comuna[nombre_partido]:
                fila_salida.append(porcentajes_partido_comuna[nombre_partido][i])
            else:
                fila_salida.append(0.0)
        writer.writerow(fila_salida)

    f.close()


# --------------------------------------------------------
# CSV 06
# --------------------------------------------------------

def generar_csv_06(cursor, totales_dip_por_comuna, totales_sen_por_comuna):
    cursor.execute("""
        SELECT
            votos_comuna_candidato.comuna_id,
            partido.partido_id,
            partido.nombre,
            SUM(
                CASE
                    WHEN candidato.cargo = 'Diputado'
                    THEN votos_comuna_candidato.cant_votos
                    ELSE 0
                END
            ) AS votos_diputados,
            SUM(
                CASE
                    WHEN candidato.cargo = 'Senador'
                    THEN votos_comuna_candidato.cant_votos
                    ELSE 0
                END
            ) AS votos_senadores
        FROM votos_comuna_candidato
        JOIN candidato
            ON votos_comuna_candidato.candidato_id = candidato.candidato_id
        JOIN partido
            ON candidato.partido_id = partido.partido_id
        GROUP BY votos_comuna_candidato.comuna_id, partido.partido_id, partido.nombre
        ORDER BY votos_comuna_candidato.comuna_id, partido.partido_id
    """)
    filas_partidos = cursor.fetchall()

    ganador_por_comuna = {}

    for fila in filas_partidos:
        comuna_id = fila[0]
        partido_id = fila[1]
        partido_nombre = fila[2]
        votos_diputados = fila[3]
        votos_senadores = fila[4]
        votos_totales = votos_diputados + votos_senadores

        if comuna_id not in ganador_por_comuna:
            ganador_por_comuna[comuna_id] = (partido_id, partido_nombre, votos_diputados, votos_senadores, votos_totales)
        else:
            datos_actuales = ganador_por_comuna[comuna_id]
            if votos_totales > datos_actuales[4]:
                ganador_por_comuna[comuna_id] = (partido_id, partido_nombre, votos_diputados, votos_senadores, votos_totales)

    f = open("06_diff_results_diputados_senadores_per_comuna.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(f)
    writer.writerow(["comuna", "percent_diputado", "percent_senador"])

    for comuna_id in sorted(ganador_por_comuna):
        datos_ganador = ganador_por_comuna[comuna_id]
        votos_diputados = datos_ganador[2]
        votos_senadores = datos_ganador[3]

        total_dip = totales_dip_por_comuna[comuna_id]
        total_sen = totales_sen_por_comuna[comuna_id]

        if total_dip > 0:
            percent_dip = round(votos_diputados * 100.0 / total_dip, 2)
        else:
            percent_dip = 0.0

        if total_sen > 0:
            percent_sen = round(votos_senadores * 100.0 / total_sen, 2)
        else:
            percent_sen = 0.0

        writer.writerow(["Comuna " + str(comuna_id), percent_dip, percent_sen])

    f.close()


# --------------------------------------------------------
# Programa principal
# --------------------------------------------------------

def main():
    conexion, cursor = conectar_db("elecciones.db")

    generar_csv_01(cursor)
    generar_csv_02(cursor)

    totales_dip_por_comuna, nombres_comuna = cargar_totales_por_comuna(cursor, "Diputado")
    totales_sen_por_comuna, nombres_comuna_sen = cargar_totales_por_comuna(cursor, "Senador")

    generar_csv_03(cursor, totales_dip_por_comuna, nombres_comuna)
    generar_csv_04(cursor, totales_sen_por_comuna)
    generar_csv_05(cursor, totales_sen_por_comuna)
    generar_csv_06(cursor, totales_dip_por_comuna, totales_sen_por_comuna)

    cursor.close()
    conexion.close()

    print("CSV generados OK")


if __name__ == "__main__":
    main()