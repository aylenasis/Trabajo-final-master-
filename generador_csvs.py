import sqlite3
import csv

conexion = sqlite3.connect("elecciones.db")
cursor = conexion.cursor()

# --------------------------------------------------------
# 01_results_diputados_totales_vis.csv
# --------------------------------------------------------

# Total de votos para Diputado
cursor.execute("""
    SELECT SUM(votos_comuna_candidato.cant_votos)
    FROM votos_comuna_candidato
    JOIN candidato ON votos_comuna_candidato.candidato_id = candidato.candidato_id
    WHERE candidato.cargo = 'Diputado'
""")
filas_total = cursor.fetchall()
total_votos_diputado = filas_total[0][0]

# Votos por partido para Diputado
cursor.execute("""
    SELECT partido.nombre,
           partido.orientacion,
           SUM(votos_comuna_candidato.cant_votos)
    FROM votos_comuna_candidato
    JOIN candidato ON votos_comuna_candidato.candidato_id = candidato.candidato_id
    JOIN partido ON candidato.partido_id = partido.partido_id
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
    porcentaje = round(votos * 100.0 / total_votos_diputado, 2)
    writer.writerow([nombre_partido, votos, porcentaje, orientacion])

f.close()

# --------------------------------------------------------
# 02_results_diputados_totales_vis.csv
# --------------------------------------------------------

cursor.execute("""
    SELECT partido.orientacion,
           SUM(votos_comuna_candidato.cant_votos)
    FROM votos_comuna_candidato
    JOIN candidato ON votos_comuna_candidato.candidato_id = candidato.candidato_id
    JOIN partido ON candidato.partido_id = partido.partido_id
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
    porcentaje = round(votos * 100.0 / total_votos_diputado, 2)
    writer.writerow([orientacion, votos, porcentaje])

f.close()

# --------------------------------------------------------
# Datos auxiliares para comunas (Diputado y Senador)
# --------------------------------------------------------

# Totales por comuna para Diputado
cursor.execute("""
    SELECT comuna.comuna_id,
           comuna.nombre,
           SUM(votos_comuna_candidato.cant_votos)
    FROM votos_comuna_candidato
    JOIN candidato ON votos_comuna_candidato.candidato_id = candidato.candidato_id
    JOIN comuna ON votos_comuna_candidato.comuna_id = comuna.comuna_id
    WHERE candidato.cargo = 'Diputado'
    GROUP BY comuna.comuna_id, comuna.nombre
    ORDER BY comuna.comuna_id
""")
filas_totales_dip = cursor.fetchall()
totales_dip_por_comuna = {}
nombres_comuna = {}
for fila in filas_totales_dip:
    comuna_id = fila[0]
    nombre = fila[1]
    total = fila[2]
    totales_dip_por_comuna[comuna_id] = total
    nombres_comuna[comuna_id] = nombre

# Totales por comuna para Senador
cursor.execute("""
    SELECT comuna.comuna_id,
           comuna.nombre,
           SUM(votos_comuna_candidato.cant_votos)
    FROM votos_comuna_candidato
    JOIN candidato ON votos_comuna_candidato.candidato_id = candidato.candidato_id
    JOIN comuna ON votos_comuna_candidato.comuna_id = comuna.comuna_id
    WHERE candidato.cargo = 'Senador'
    GROUP BY comuna.comuna_id, comuna.nombre
    ORDER BY comuna.comuna_id
""")
filas_totales_sen = cursor.fetchall()
totales_sen_por_comuna = {}
for fila in filas_totales_sen:
    comuna_id = fila[0]
    total = fila[2]
    totales_sen_por_comuna[comuna_id] = total

# --------------------------------------------------------
# 03_results_diputados_totales_per_comuna_vis.csv
# --------------------------------------------------------

# Votos por comuna y partido (Diputado)
cursor.execute("""
    SELECT comuna.comuna_id,
           comuna.nombre,
           partido.nombre,
           SUM(votos_comuna_candidato.cant_votos)
    FROM votos_comuna_candidato
    JOIN candidato ON votos_comuna_candidato.candidato_id = candidato.candidato_id
    JOIN partido ON candidato.partido_id = partido.partido_id
    JOIN comuna ON votos_comuna_candidato.comuna_id = comuna.comuna_id
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

for comuna_id in sorted(votos_dip_por_comuna.keys()):
    total_comuna = totales_dip_por_comuna[comuna_id]
    lista_partidos = votos_dip_por_comuna[comuna_id]
    top4 = lista_partidos[:4]
    while len(top4) < 4:
        top4.append(("", 0))

    fila = [nombres_comuna[comuna_id]]
    for nombre_partido, votos in top4:
        if total_comuna > 0:
            porcentaje = round(votos * 100.0 / total_comuna, 2)
        else:
            porcentaje = 0.0
        fila.append(nombre_partido)
        fila.append(porcentaje)
        fila.append(votos)

    writer.writerow(fila)

f.close()

# --------------------------------------------------------
# 04_diff_senadores_per_comuna_vis.csv
# --------------------------------------------------------

# Votos por comuna y partido (Senador)
cursor.execute("""
    SELECT comuna.comuna_id,
           comuna.nombre,
           partido.nombre,
           SUM(votos_comuna_candidato.cant_votos)
    FROM votos_comuna_candidato
    JOIN candidato ON votos_comuna_candidato.candidato_id = candidato.candidato_id
    JOIN partido ON candidato.partido_id = partido.partido_id
    JOIN comuna ON votos_comuna_candidato.comuna_id = comuna.comuna_id
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

# Lat/Lon por comuna
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

for comuna_id in sorted(votos_sen_por_comuna.keys()):
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
# 05_partidos_greater_than_5.csv
# --------------------------------------------------------


cursor.execute("""
    SELECT comuna.comuna_id,
           partido.nombre,
           SUM(votos_comuna_candidato.cant_votos)
    FROM votos_comuna_candidato
    JOIN candidato ON votos_comuna_candidato.candidato_id = candidato.candidato_id
    JOIN partido ON candidato.partido_id = partido.partido_id
    JOIN comuna ON votos_comuna_candidato.comuna_id = comuna.comuna_id
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

# Filtramos partidos que superaron 5% en alguna comuna
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
    fila = [nombre_partido]
    for i in range(1, 16):
        if i in porcentajes_partido_comuna[nombre_partido]:
            fila.append(porcentajes_partido_comuna[nombre_partido][i])
        else:
            fila.append(0.0)
    writer.writerow(fila)

f.close()

# --------------------------------------------------------
# 06_diff_results_diputados_senadores_per_comuna.csv
# --------------------------------------------------------

# Ganador en Diputado por comuna
ganador_dip_por_comuna = {}
for comuna_id in votos_dip_por_comuna:
    lista_partidos = votos_dip_por_comuna[comuna_id]
    nombre_ganador, votos_ganador = lista_partidos[0]
    ganador_dip_por_comuna[comuna_id] = (nombre_ganador, votos_ganador)

# Votos por comuna y partido en Senador
cursor.execute("""
    SELECT comuna.comuna_id,
           partido.nombre,
           SUM(votos_comuna_candidato.cant_votos)
    FROM votos_comuna_candidato
    JOIN candidato ON votos_comuna_candidato.candidato_id = candidato.candidato_id
    JOIN partido ON candidato.partido_id = partido.partido_id
    JOIN comuna ON votos_comuna_candidato.comuna_id = comuna.comuna_id
    WHERE candidato.cargo = 'Senador'
    GROUP BY comuna.comuna_id, partido.partido_id, partido.nombre
""")
filas_sen_again = cursor.fetchall()

votos_sen_por_comuna_y_partido = {}
for fila in filas_sen_again:
    comuna_id = fila[0]
    nombre_partido = fila[1]
    votos = fila[2]
    votos_sen_por_comuna_y_partido[(comuna_id, nombre_partido)] = votos

f = open("06_diff_results_diputados_senadores_per_comuna.csv", "w", newline="", encoding="utf-8")
writer = csv.writer(f)
writer.writerow(["comuna", "percent_diputado", "percent_senador"])

for comuna_id in sorted(ganador_dip_por_comuna.keys()):
    nombre_comuna = nombres_comuna[comuna_id]
    total_dip = totales_dip_por_comuna[comuna_id]

    nombre_ganador = ganador_dip_por_comuna[comuna_id][0]
    votos_ganador_dip = ganador_dip_por_comuna[comuna_id][1]

    if total_dip > 0:
        porcentaje_dip = round(votos_ganador_dip * 100.0 / total_dip, 2)
    else:
        porcentaje_dip = 0.0

    total_sen = totales_sen_por_comuna.get(comuna_id, 0)
    votos_sen_mismo = votos_sen_por_comuna_y_partido.get((comuna_id, nombre_ganador), 0)

    if total_sen > 0:
        porcentaje_sen = round(votos_sen_mismo * 100.0 / total_sen, 2)
    else:
        porcentaje_sen = 0.0

    writer.writerow([nombre_comuna, porcentaje_dip, porcentaje_sen])

f.close()

conexion.close()

print("CSV generados OK")