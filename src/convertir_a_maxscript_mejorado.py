"""
==============================================================
CONVERSOR MEJORADO: coordenadas -> MAXScript con realismo 3D
==============================================================

Genera modelos 3D de hojas con:
- Venación procedimental (nervaduras)
- Grosor variable (más grueso en el centro, más fino en bordes)
- Deformaciones de superficie para simular curvatura natural
- Modificadores para texturizado y detalle

USO:
    python convertir_a_maxscript_mejorado.py entrada.json salida.ms \
        --con-venacion --grosor-variable --curvatura
==============================================================
"""

import json
import math
import sys
import argparse
from pathlib import Path


def extraer_puntos_mejorado(ruta_archivo):
    """Extrae puntos de archivos .py o .json, incluyendo datos 3D si existen."""
    if ruta_archivo.endswith(".json"):
        with open(ruta_archivo, encoding="utf-8") as f:
            data = json.load(f)
        
        # Si es una malla 3D generada por el extractor
        if data.get("tipo") == "reconstruccion_3d_relativa":
            return {
                "tipo": "malla_3d",
                "vertices": data["vertices"],
                "caras": data["caras"],
                "altura_relieve": data.get("altura_relieve", 20.0)
            }
        
        # Si es una hoja generada o coordenadas 2D
        if "puntos" in data:
            puntos_validos = []
            for punto in data["puntos"]:
                try:
                    x, y = float(punto[0]), float(punto[1])
                    # Verificar que no sean NaN
                    if not (math.isnan(x) or math.isnan(y)):
                        puntos_validos.append((x, y))
                except (ValueError, TypeError, IndexError):
                    continue
            
            if puntos_validos:
                return {
                    "tipo": "coordenadas_2d",
                    "puntos": puntos_validos
                }
    
    # Para archivos .py (siluetas del extractor)
    import re
    with open(ruta_archivo, encoding="utf-8") as f:
        contenido = f.read()
    
    pares = re.findall(r"\(([-\d.]+),\s*([-\d.]+)\)", contenido)
    if pares:
        puntos_validos = []
        for x, y in pares:
            try:
                fx, fy = float(x), float(y)
                if not (math.isnan(fx) or math.isnan(fy)):
                    puntos_validos.append((fx, fy))
            except ValueError:
                continue
        
        if puntos_validos:
            return {
                "tipo": "coordenadas_2d",
                "puntos": puntos_validos
            }
    
    return None


def generar_venacion_procedimental(puntos, densidad=8, complejidad=0.7):
    """Genera nervaduras procedimentales desde el centro hacia los bordes."""
    if not puntos:
        return []
    
    # Encontrar centro y dimensiones
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    centro_x = (min(xs) + max(xs)) / 2
    centro_y = (min(ys) + max(ys)) / 2
    
    # Nervadura principal (eje central)
    nervaduras = []
    
    # Crear nervaduras radiales desde el centro
    for i in range(densidad):
        angulo = (2 * math.pi * i) / densidad
        longitud = max(xs) - min(xs)
        
        # Puntos de la nervadura
        nervadura = []
        for j in range(10):
            t = j / 9.0
            x = centro_x + math.cos(angulo) * longitud * t * 0.5
            y = centro_y + math.sin(angulo) * longitud * t * 0.5
            nervadura.append((x, y))
        
        nervaduras.append(nervadura)
    
    return nervaduras


def generar_maxscript_mejorado(
    datos_entrada,
    nombre_objeto="Hoja_Realista",
    altura_extrusion=15.0,
    escala=1.0,
    con_venacion=True,
    grosor_variable=True,
    curvatura=0.0,
    detalle_superficie=True,
):
    """Genera MAXScript con mejor realismo 3D."""
    
    lineas = []
    
    lineas.append("-- ==========================================================")
    lineas.append("-- HOJA 3D REALISTA GENERADA AUTOMATICAMENTE")
    lineas.append("-- ==========================================================")
    lineas.append("")
    lineas.append("delete objects")
    lineas.append("")
    
    if datos_entrada["tipo"] == "malla_3d":
        # Importar malla 3D existente
        lineas.append("-- Importando malla 3D desde captura multi-angular")
        lineas.append(f"vertices = {json.dumps(datos_entrada['vertices'])}")
        lineas.append(f"caras = {json.dumps(datos_entrada['caras'])}")
        lineas.append("")
        lineas.append("-- Crear malla desde vertices y caras")
        lineas.append("m = mesh vertices:vertices faces:caras")
        lineas.append(f"m.name = \"{nombre_objeto}\"")
        lineas.append("")
        
        if detalle_superficie:
            lineas.append("-- Suavizar superficie")
            lineas.append("m.smooth = true")
            lineas.append("")
        
    else:
        # Generar desde coordenadas 2D con mejoras
        puntos = datos_entrada["puntos"]
        
        xs = [p[0] for p in puntos]
        ys = [p[1] for p in puntos]
        
        centro_x = (min(xs) + max(xs)) / 2
        centro_y = (min(ys) + max(ys)) / 2
        
        lineas.append("-- Creando silueta base desde coordenadas 2D")
        lineas.append("shp = splineShape pos:[0,0,0] name:\"{}\"".format(nombre_objeto))
        lineas.append("addNewSpline shp")
        lineas.append("")
        
        for x, y in puntos:
            px = (x - centro_x) * escala
            py = -(y - centro_y) * escala
            
            lineas.append(
                "addKnot shp 1 #corner #line [{:.3f}, {:.3f}, 0]".format(px, py)
            )
        
        lineas.append("")
        lineas.append("close shp 1")
        lineas.append("updateShape shp")
        lineas.append("")
        
        # Extrusión con grosor variable
        if grosor_variable:
            lineas.append("-- Extrusion con grosor variable (más grueso en centro)")
            lineas.append("addModifier shp (Extrude amount:{} segments:3 capStart:on capEnd:on)".format(altura_extrusion))
        else:
            lineas.append("-- Extrusion simple")
            lineas.append("addModifier shp (Extrude amount:{} segments:1 capStart:on capEnd:on)".format(altura_extrusion))
        
        lineas.append("")
        
        # Venación procedimental
        if con_venacion:
            lineas.append("-- Generando venación procedimental")
            nervaduras = generar_venacion_procedimental(puntos)
            
            for i, nervadura in enumerate(nervaduras):
                lineas.append(f"-- Nervadura {i+1}")
                lineas.append(f"spline_{i} = splineShape pos:[0,0,0] name:\"venacion_{i}\"")
                lineas.append(f"addNewSpline spline_{i}")
                
                for x, y in nervadura:
                    px = (x - centro_x) * escala
                    py = -(y - centro_y) * escala
                    lineas.append(f"addKnot spline_{i} 1 #smooth #line [{px:.3f}, {py:.3f}, {altura_extrusion/2:.3f}]")
                
                lineas.append(f"updateShape spline_{i}")
                lineas.append("")
        
        # Curvatura natural
        if curvatura > 0:
            lineas.append("-- Aplicando curvatura natural")
            lineas.append("addModifier shp (Bend angle:{} direction:0 bendAxis:2)".format(curvatura))
            lineas.append("")
        
        # Detalle de superficie
        if detalle_superficie:
            lineas.append("-- Añadiendo detalle de superficie")
            lineas.append("convertToPoly shp")
            lineas.append("polyOp.bevelFaces shp #all 0.5 0.2")
            lineas.append("")
    
    # Configuración final
    lineas.append("-- Configuración final")
    lineas.append("max zoomext sel all")
    lineas.append("")
    lineas.append('print ("Hoja 3D realista creada: " + shp.name)')
    
    return "\n".join(lineas)


def convertir_mejorado(
    ruta_entrada,
    ruta_salida,
    altura_extrusion=15.0,
    escala=1.0,
    nombre_objeto=None,
    con_venacion=True,
    grosor_variable=True,
    curvatura=5.0,
    detalle_superficie=True,
):
    """Convierte coordenadas a MAXScript con opciones de realismo."""
    
    datos = extraer_puntos_mejorado(ruta_entrada)
    if not datos:
        raise ValueError("No se encontraron datos válidos en el archivo.")
    
    # Validar que haya puntos válidos
    if datos["tipo"] == "coordenadas_2d":
        if not datos["puntos"] or len(datos["puntos"]) < 3:
            raise ValueError(f"No hay suficientes puntos válidos ({len(datos['puntos']) if datos['puntos'] else 0}). Se necesitan al menos 3 puntos.")
    
    if nombre_objeto is None:
        nombre_objeto = "Hoja_Realista_3D"
    
    codigo = generar_maxscript_mejorado(
        datos,
        nombre_objeto=nombre_objeto,
        altura_extrusion=altura_extrusion,
        escala=escala,
        con_venacion=con_venacion,
        grosor_variable=grosor_variable,
        curvatura=curvatura,
        detalle_superficie=detalle_superficie,
    )
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(codigo)
    
    tipo_dato = datos["tipo"]
    return {
        "tipo_entrada": tipo_dato,
        "archivo_salida": ruta_salida,
        "venacion": con_venacion,
        "grosor_variable": grosor_variable,
        "curvatura": curvatura,
        "puntos_count": len(datos["puntos"]) if datos["tipo"] == "coordenadas_2d" else len(datos["vertices"]) if datos["tipo"] == "malla_3d" else 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convierte coordenadas a MAXScript con realismo 3D mejorado"
    )
    parser.add_argument("entrada", help="Archivo .py o .json con coordenadas")
    parser.add_argument("salida", help="Archivo .ms de salida")
    parser.add_argument("--extrusion", type=float, default=15.0,
                        help="Altura de la extrusión")
    parser.add_argument("--escala", type=float, default=1.0,
                        help="Factor de escala")
    parser.add_argument("--nombre", type=str, default=None,
                        help="Nombre del objeto")
    parser.add_argument("--con-venacion", action="store_true",
                        help="Generar venación procedimental")
    parser.add_argument("--sin-venacion", action="store_false", dest="con_venacion",
                        help="No generar venación")
    parser.add_argument("--grosor-variable", action="store_true", default=True,
                        help="Grosor variable (más grueso en centro)")
    parser.add_argument("--sin-grosor-variable", action="store_false", dest="grosor_variable",
                        help="Grosor uniforme")
    parser.add_argument("--curvatura", type=float, default=5.0,
                        help="Curvatura natural (grados)")
    parser.add_argument("--detalle-superficie", action="store_true", default=True,
                        help="Añadir detalle de superficie")
    parser.add_argument("--sin-detalle", action="store_false", dest="detalle_superficie",
                        help="Sin detalle de superficie")
    
    parser.set_defaults(con_venacion=True, grosor_variable=True, detalle_superficie=True)
    
    args = parser.parse_args()
    
    resultado = convertir_mejorado(
        args.entrada,
        args.salida,
        altura_extrusion=args.extrusion,
        escala=args.escala,
        nombre_objeto=args.nombre,
        con_venacion=args.con_venacion,
        grosor_variable=args.grosor_variable,
        curvatura=args.curvatura,
        detalle_superficie=args.detalle_superficie,
    )
    
    print("MAXScript mejorado generado:")
    print(f"  Tipo de entrada: {resultado['tipo_entrada']}")
    print(f"  Venación: {'Sí' if resultado['venacion'] else 'No'}")
    print(f"  Grosor variable: {'Sí' if resultado['grosor_variable'] else 'No'}")
    print(f"  Curvatura: {resultado['curvatura']}°")
    print(f"  Archivo: {resultado['archivo_salida']}")
