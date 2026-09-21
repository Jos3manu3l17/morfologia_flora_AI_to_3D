import cv2
import json
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os


# ==========================================================
# EXTRACTOR DE SILUETAS PROFESIONAL
#
# Imagen
#   ->
# OpenCV
#   ->
# Mascara
#   ->
# Contorno exterior
#   ->
# Huecos interiores
#   ->
# Jerarquia completa
#   ->
# Coordenadas
#   ->
# Codigo Python
#   ->
# Reconstruccion
#
# Conserva el maximo detalle posible.
# ==========================================================


# ==========================================================
# CONFIGURACION
# ==========================================================

# Umbral para separar hoja/fondo
UMBRAL = 200

# ----------------------------------------------------------
# 0 = maxima cantidad de puntos
#
# No simplifica el contorno.
#
# Si el archivo generado queda demasiado grande puedes
# probar:
#
# 0.0001
# 0.0005
# 0.001
# ----------------------------------------------------------

APROXIMACION = 0


# ----------------------------------------------------------
# Tamano de la ventana de reconstruccion
# ----------------------------------------------------------

ANCHO_VENTANA = 1000
ALTO_VENTANA = 800


# ----------------------------------------------------------
# Margen alrededor de la hoja
# ----------------------------------------------------------

MARGEN = 40


# ----------------------------------------------------------
# Area minima para ignorar ruido
# ----------------------------------------------------------

AREA_MINIMA = 100

# ----------------------------------------------------------
# Parametros de reconstruccion 3D relativa
# ----------------------------------------------------------

RESOLUCION_MALLA = 120
ALTURA_RELIEVE = 20.0
PROFUNDIDAD_MINIMA = 0.05


# ==========================================================
# SELECCIONAR IMAGEN
# ==========================================================

def seleccionar_imagenes():

    root = tk.Tk()

    root.withdraw()

    rutas = filedialog.askopenfilenames(
        title="Selecciona una o varias fotos de la hoja",
        filetypes=[
            (
                "Imagenes",
                "*.png *.jpg *.jpeg *.bmp *.webp"
            ),
            (
                "Todos los archivos",
                "*.*"
            )
        ]
    )

    root.destroy()

    return list(rutas)


def seleccionar_imagen():
    """Compatibilidad con el nombre original: devuelve una sola ruta."""
    rutas = seleccionar_imagenes()
    return rutas[0] if rutas else ""


# ==========================================================
# CARGAR IMAGEN
# ==========================================================

def cargar_imagen(ruta):

    imagen = cv2.imread(
        ruta,
        cv2.IMREAD_GRAYSCALE
    )

    if imagen is None:

        raise ValueError(
            "No fue posible cargar la imagen."
        )

    return imagen


def cargar_imagenes(rutas):
    """Carga y valida todas las vistas en escala de grises."""
    imagenes = [cargar_imagen(ruta) for ruta in rutas]
    if not imagenes:
        raise ValueError("No se seleccionaron imagenes.")

    forma = imagenes[0].shape
    return [
        imagen if imagen.shape == forma else cv2.resize(
            imagen, (forma[1], forma[0]), interpolation=cv2.INTER_AREA
        )
        for imagen in imagenes
    ]


def alinear_vistas(imagenes):
    """Alinea vistas con transformaciones afines para comparar iluminacion."""
    referencia = imagenes[0]
    alineadas = [referencia]
    referencia_float = referencia.astype(np.float32) / 255.0

    for imagen in imagenes[1:]:
        imagen_float = imagen.astype(np.float32) / 255.0
        matriz = np.eye(2, 3, dtype=np.float32)
        try:
            cv2.findTransformECC(
                referencia_float,
                imagen_float,
                matriz,
                cv2.MOTION_AFFINE,
                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 80, 1e-5),
            )
            alineada = cv2.warpAffine(
                imagen,
                matriz,
                (referencia.shape[1], referencia.shape[0]),
                flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                borderMode=cv2.BORDER_REFLECT,
            )
        except cv2.error:
            # Una vista sin textura suficiente no debe detener el proceso.
            alineada = imagen
        alineadas.append(alineada)

    return alineadas


def estimar_profundidad_sombreado(imagenes, mascara):
    """Estima relieve relativo a partir de cambios de iluminacion."""
    pila = np.stack([imagen.astype(np.float32) / 255.0 for imagen in imagenes])
    brillo = np.median(pila, axis=0)
    brillo = cv2.GaussianBlur(brillo, (0, 0), 2.0)

    dentro = mascara > 0
    if not np.any(dentro):
        return np.zeros_like(brillo, dtype=np.float32)

    valores = brillo[dentro]
    minimo, maximo = float(valores.min()), float(valores.max())
    if maximo - minimo < 1e-6:
        return np.zeros_like(brillo, dtype=np.float32)

    # En una hoja opaca, las zonas relativamente oscuras se interpretan
    # como relieve alto. El resultado es relativo porque no hay luces calibradas.
    profundidad = 1.0 - (brillo - minimo) / (maximo - minimo)
    profundidad = cv2.GaussianBlur(profundidad, (0, 0), 1.2)
    profundidad[~dentro] = 0.0
    return np.clip(profundidad, 0.0, 1.0).astype(np.float32)


def estimar_profundidad_fotogrametrica(imagenes, mascara):
    """Obtiene disparidad relativa entre las dos primeras vistas, si es posible."""
    if len(imagenes) < 2:
        return None

    ancho = imagenes[0].shape[1]
    num_disparidades = max(16, (ancho // 8) // 16 * 16)
    num_disparidades = min(num_disparidades, 128)

    try:
        stereo = cv2.StereoSGBM_create(
            minDisparity=0,
            numDisparities=num_disparidades,
            blockSize=5,
            P1=8 * 5 * 5,
            P2=32 * 5 * 5,
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY,
        )
        disparidad = stereo.compute(imagenes[0], imagenes[1]).astype(np.float32)
        disparidad /= 16.0
        valido = (disparidad > 1.0) & (mascara > 0)
        if np.count_nonzero(valido) < 100:
            return None

        profundidad = np.zeros_like(disparidad, dtype=np.float32)
        profundidad[valido] = 1.0 / disparidad[valido]
        valores = profundidad[valido]
        minimo, maximo = float(np.percentile(valores, 5)), float(np.percentile(valores, 95))
        if maximo - minimo < 1e-6:
            return None
        profundidad = np.clip((profundidad - minimo) / (maximo - minimo), 0.0, 1.0)
        profundidad[~(mascara > 0)] = 0.0
        return cv2.GaussianBlur(profundidad, (0, 0), 1.0)
    except cv2.error:
        return None


def construir_malla_3d(profundidad, mascara, ancho_mundo=100.0):
    """Convierte el mapa de profundidad relativo en vertices y caras."""
    alto, ancho = profundidad.shape
    paso = max(1, int(max(alto, ancho) / RESOLUCION_MALLA))
    ys = range(0, alto, paso)
    xs = range(0, ancho, paso)
    vertices = []
    indices = {}

    for y in ys:
        for x in xs:
            if mascara[y, x] == 0:
                continue
            indice = len(vertices)
            indices[(y, x)] = indice
            px = (x - ancho / 2) * ancho_mundo / max(ancho, 1)
            py = (alto / 2 - y) * ancho_mundo / max(ancho, 1)
            pz = float(profundidad[y, x]) * ALTURA_RELIEVE
            vertices.append([round(px, 4), round(py, 4), round(pz, 4)])

    caras = []
    for y in ys:
        for x in xs:
            puntos = [
                indices.get((y, x)),
                indices.get((y, x + paso)),
                indices.get((y + paso, x + paso)),
                indices.get((y + paso, x)),
            ]
            if all(indice is not None for indice in puntos):
                caras.append([indice + 1 for indice in puntos])

    return vertices, caras


def guardar_reconstruccion_3d(ruta_imagen, vertices, caras, profundidad_origen):
    """Guarda una malla OBJ y sus metadatos JSON junto a la primera foto."""
    carpeta = os.path.dirname(ruta_imagen)
    nombre = os.path.splitext(os.path.basename(ruta_imagen))[0]
    ruta_obj = os.path.join(carpeta, nombre + "_3d.obj")
    ruta_json = os.path.join(carpeta, nombre + "_3d.json")

    with open(ruta_obj, "w", encoding="utf-8") as archivo:
        archivo.write("# Malla 3D relativa generada desde multiples vistas\n")
        for x, y, z in vertices:
            archivo.write("v {:.4f} {:.4f} {:.4f}\n".format(x, y, z))
        for cara in caras:
            archivo.write("f {}\n".format(" ".join(map(str, cara))))

    datos = {
        "tipo": "reconstruccion_3d_relativa",
        "vertices": vertices,
        "caras": caras,
        "altura_relieve": ALTURA_RELIEVE,
        "profundidad_minima": PROFUNDIDAD_MINIMA,
    }
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)

    return ruta_obj, ruta_json


# ==========================================================
# CREAR MASCARA
# ==========================================================

def crear_mascara(imagen):

    _, mascara = cv2.threshold(
        imagen,
        UMBRAL,
        255,
        cv2.THRESH_BINARY_INV
    )

    return mascara


# ==========================================================
# LIMPIAR MASCARA
# ==========================================================

def limpiar_mascara(mascara):

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    mascara = cv2.morphologyEx(
        mascara,
        cv2.MORPH_OPEN,
        kernel
    )

    return mascara


# ==========================================================
# ENCONTRAR CONTORNOS
#
# RETR_TREE es importante.
#
# Permite obtener toda la jerarquia:
#
# exterior
#   |-- hueco
#        |-- detalle
#             |-- hueco
#
# ==========================================================

def encontrar_contornos(mascara):

    resultado = cv2.findContours(
        mascara,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_NONE
    )

    if len(resultado) == 2:

        contornos, jerarquia = resultado

    else:

        _, contornos, jerarquia = resultado

    return contornos, jerarquia


# ==========================================================
# ENCONTRAR CONTORNO PRINCIPAL
# ==========================================================

def encontrar_contorno_principal(
    contornos,
    jerarquia
):

    if jerarquia is None:

        return None

    jerarquia = jerarquia[0]

    candidatos = []

    for indice, contorno in enumerate(contornos):

        area = abs(
            cv2.contourArea(contorno)
        )

        if area < AREA_MINIMA:
            continue

        padre = jerarquia[indice][3]

        # Solo buscamos contornos exteriores
        if padre == -1:

            candidatos.append(
                (
                    indice,
                    area
                )
            )

    if not candidatos:

        return None

    # El contorno exterior mas grande
    # sera nuestra hoja principal.

    candidatos.sort(
        key=lambda elemento: elemento[1],
        reverse=True
    )

    return candidatos[0][0]


# ==========================================================
# OBTENER TODA LA JERARQUIA DEL CONTORNO
# PRINCIPAL
# ==========================================================

def obtener_descendientes(
    indice_principal,
    contornos,
    jerarquia
):

    jerarquia = jerarquia[0]

    seleccionados = []

    def recorrer(indice):

        # Agregar este contorno
        seleccionados.append(indice)

        # Buscar hijos directos
        hijo = jerarquia[indice][2]

        while hijo != -1:

            area = abs(
                cv2.contourArea(
                    contornos[hijo]
                )
            )

            if area >= AREA_MINIMA:

                recorrer(hijo)

            # Siguiente hermano
            hijo = jerarquia[hijo][0]

    recorrer(indice_principal)

    return seleccionados


# ==========================================================
# CALCULAR PROFUNDIDAD DEL CONTORNO
#
# Ejemplo:
#
# profundidad 0 = exterior
# profundidad 1 = hueco
# profundidad 2 = detalle negro
# profundidad 3 = hueco
#
# Esto permite reconstruir correctamente espacios
# dentro de otros espacios.
# ==========================================================

def calcular_profundidad(
    indice,
    jerarquia
):

    jerarquia = jerarquia[0]

    profundidad = 0

    padre = jerarquia[indice][3]

    while padre != -1:

        profundidad += 1

        padre = jerarquia[padre][3]

    return profundidad


# ==========================================================
# CONVERTIR CONTORNO A COORDENADAS
# ==========================================================

def convertir_coordenadas(
    contorno,
    ancho,
    alto
):

    puntos = []

    for punto in contorno:

        x = float(
            punto[0][0]
        )

        y = float(
            punto[0][1]
        )

        # --------------------------------------------------
        # Centrar imagen
        # --------------------------------------------------

        x = x - ancho / 2

        y = alto / 2 - y

        puntos.append(
            (
                round(x, 2),
                round(y, 2)
            )
        )

    return puntos


# ==========================================================
# EXTRAER COORDENADAS
# ==========================================================

def extraer_coordenadas(
    contornos,
    indices,
    jerarquia,
    ancho,
    alto
):

    resultado = []

    for indice in indices:

        contorno = contornos[indice]

        # --------------------------------------------------
        # Simplificacion opcional
        # --------------------------------------------------

        if APROXIMACION > 0:

            epsilon = (
                APROXIMACION
                *
                cv2.arcLength(
                    contorno,
                    True
                )
            )

            contorno = cv2.approxPolyDP(
                contorno,
                epsilon,
                True
            )

        puntos = convertir_coordenadas(
            contorno,
            ancho,
            alto
        )

        profundidad = calcular_profundidad(
            indice,
            jerarquia
        )

        # --------------------------------------------------
        # Determinar tipo
        # --------------------------------------------------

        if profundidad == 0:

            tipo = "EXTERIOR"

        elif profundidad % 2 == 1:

            tipo = "HUECO"

        else:

            tipo = "DETALLE"

        resultado.append(
            {
                "indice": indice,
                "puntos": puntos,
                "profundidad": profundidad,
                "tipo": tipo
            }
        )

    return resultado


# ==========================================================
# CALCULAR ESCALA AUTOMATICA
# ==========================================================

def calcular_escala(
    coordenadas
):

    todos_los_puntos = []

    for datos in coordenadas:

        todos_los_puntos.extend(
            datos["puntos"]
        )

    if not todos_los_puntos:

        return 1

    xs = [
        punto[0]
        for punto in todos_los_puntos
    ]

    ys = [
        punto[1]
        for punto in todos_los_puntos
    ]

    minimo_x = min(xs)
    maximo_x = max(xs)

    minimo_y = min(ys)
    maximo_y = max(ys)

    ancho = maximo_x - minimo_x
    alto = maximo_y - minimo_y

    espacio_x = (
        ANCHO_VENTANA
        - MARGEN * 2
    )

    espacio_y = (
        ALTO_VENTANA
        - MARGEN * 2
    )

    if ancho <= 0 or alto <= 0:

        return 1

    escala_x = espacio_x / ancho
    escala_y = espacio_y / alto

    escala = min(
        escala_x,
        escala_y
    )

    return escala


# ==========================================================
# GENERAR CODIGO DE RECONSTRUCCION
# ==========================================================

def generar_codigo_turtle(
    coordenadas,
    nombre
):

    codigo = []

    codigo.append(
        "import tkinter as tk"
    )

    codigo.append("")

    codigo.append(
        "# =================================================="
    )

    codigo.append(
        "# SILUETA RECONSTRUIDA AUTOMATICAMENTE"
    )

    codigo.append(
        "# Imagen: " + nombre
    )

    codigo.append(
        "# =================================================="
    )

    codigo.append("")

    codigo.append(
        "ANCHO = 1000"
    )

    codigo.append(
        "ALTO = 800"
    )

    codigo.append("")

    codigo.append(
        "ventana = tk.Tk()"
    )

    codigo.append(
        'ventana.title("Silueta reconstruida")'
    )

    codigo.append(
        "ventana.geometry('1000x800')"
    )

    codigo.append(
        "ventana.configure(bg='white')"
    )

    codigo.append("")

    codigo.append(
        "canvas = tk.Canvas("
    )

    codigo.append(
        "    ventana,"
    )

    codigo.append(
        "    width=ANCHO,"
    )

    codigo.append(
        "    height=ALTO,"
    )

    codigo.append(
        "    bg='white',"
    )

    codigo.append(
        "    highlightthickness=0"
    )

    codigo.append(
        ")"
    )

    codigo.append(
        "canvas.pack()"
    )

    codigo.append("")

    # ------------------------------------------------------
    # ESCALA
    # ------------------------------------------------------

    escala = calcular_escala(
        coordenadas
    )

    codigo.append(
        "# Escala automatica: {}".format(
            round(escala, 6)
        )
    )

    codigo.append("")

    # ------------------------------------------------------
    # DIBUJAR CONTORNOS EN ORDEN
    # ------------------------------------------------------

    for numero, datos in enumerate(
        coordenadas
    ):

        puntos = datos["puntos"]

        tipo = datos["tipo"]

        profundidad = datos[
            "profundidad"
        ]

        if len(puntos) < 3:

            continue

        codigo.append(
            "# --------------------------------------------------"
        )

        codigo.append(
            "# Contorno {}".format(
                numero + 1
            )
        )

        codigo.append(
            "# Tipo: {}".format(
                tipo
            )
        )

        codigo.append(
            "# Profundidad: {}".format(
                profundidad
            )
        )

        codigo.append(
            "# Puntos: {}".format(
                len(puntos)
            )
        )

        codigo.append(
            "# --------------------------------------------------"
        )

        codigo.append(
            "puntos = ["
        )

        for x, y in puntos:

            canvas_x = (
                x * escala
                + ANCHO_VENTANA / 2
            )

            canvas_y = (
                ALTO_VENTANA / 2
                - y * escala
            )

            codigo.append(
                "    ({}, {}),".format(
                    round(canvas_x, 2),
                    round(canvas_y, 2)
                )
            )

        codigo.append(
            "]"
        )

        codigo.append("")

        # --------------------------------------------------
        # COLOR SEGUN PROFUNDIDAD
        # --------------------------------------------------

        if profundidad % 2 == 0:

            relleno = "black"

        else:

            relleno = "white"

        codigo.append(
            "canvas.create_polygon("
        )

        codigo.append(
            "    puntos,"
        )

        codigo.append(
            "    fill='{}',".format(
                relleno
            )
        )

        codigo.append(
            "    outline='{}',".format(
                relleno
            )
        )

        codigo.append(
            "    smooth=False"
        )

        codigo.append(
            ")"
        )

        codigo.append("")

    # ------------------------------------------------------
    # INFORMACION
    # ------------------------------------------------------

    codigo.append(
        "ventana.mainloop()"
    )

    return "\n".join(codigo)


# ==========================================================
# GUARDAR RESULTADOS
# ==========================================================

def guardar_resultados(
    ruta_imagen,
    coordenadas,
    codigo
):

    carpeta = os.path.dirname(
        ruta_imagen
    )

    nombre = os.path.splitext(
        os.path.basename(
            ruta_imagen
        )
    )[0]

    archivo_python = os.path.join(
        carpeta,
        nombre + "_silueta.py"
    )

    archivo_coordenadas = os.path.join(
        carpeta,
        nombre + "_coordenadas.txt"
    )

    # ------------------------------------------------------
    # GUARDAR PYTHON
    # ------------------------------------------------------

    with open(
        archivo_python,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(
            codigo
        )

    # ------------------------------------------------------
    # GUARDAR COORDENADAS
    # ------------------------------------------------------

    with open(
        archivo_coordenadas,
        "w",
        encoding="utf-8"
    ) as archivo:

        for numero, datos in enumerate(
            coordenadas
        ):

            archivo.write(
                "CONTORNO {}\n".format(
                    numero + 1
                )
            )

            archivo.write(
                "TIPO: {}\n".format(
                    datos["tipo"]
                )
            )

            archivo.write(
                "PROFUNDIDAD: {}\n".format(
                    datos["profundidad"]
                )
            )

            archivo.write(
                "PUNTOS: {}\n".format(
                    len(datos["puntos"])
                )
            )

            archivo.write(
                "\n"
            )

            for x, y in datos["puntos"]:

                archivo.write(
                    "{}, {}\n".format(
                        x,
                        y
                    )
                )

            archivo.write(
                "\n"
            )

    return (
        archivo_python,
        archivo_coordenadas
    )


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================

def main():

    print()
    print("=" * 65)
    print(
        "          EXTRACTOR DE SILUETAS"
    )
    print(
        "        CON DETALLE Y HUECOS"
    )
    print("=" * 65)
    print()

    print(
        "Selecciona una o varias fotos de la misma hoja..."
    )

    rutas = seleccionar_imagenes()

    if not rutas:

        print()
        print(
            "No seleccionaste ninguna imagen."
        )

        return

    print()

    ruta = rutas[0]

    print("Fotos seleccionadas:", len(rutas))
    for ruta_actual in rutas:
        print(" -", ruta_actual)

    print()

    print(
        "Analizando imagen..."
    )

    # ------------------------------------------------------
    # CARGAR
    # ------------------------------------------------------

    imagenes = cargar_imagenes(rutas)
    imagenes = alinear_vistas(imagenes)
    imagen = imagenes[0]

    alto, ancho = imagen.shape

    print()

    print(
        "Resolucion:",
        ancho,
        "x",
        alto
    )

    # ------------------------------------------------------
    # MASCARA
    # ------------------------------------------------------

    mascara = crear_mascara(
        imagen
    )

    mascara = limpiar_mascara(
        mascara
    )

    profundidad_sombreado = estimar_profundidad_sombreado(
        imagenes,
        mascara
    )

    profundidad_fotogrametrica = estimar_profundidad_fotogrametrica(
        imagenes,
        mascara
    )

    if profundidad_fotogrametrica is not None:
        profundidad = (
            0.65 * profundidad_fotogrametrica
            + 0.35 * profundidad_sombreado
        )
        metodo_3d = "fotogrametria relativa + sombreado"
    else:
        profundidad = profundidad_sombreado
        metodo_3d = "shape from shading relativo"

    # ------------------------------------------------------
    # CONTORNOS
    # ------------------------------------------------------

    contornos, jerarquia = encontrar_contornos(
        mascara
    )

    print(
        "Contornos encontrados:",
        len(contornos)
    )

    if jerarquia is None:

        print()

        print(
            "No se encontro jerarquia."
        )

        return

    # ------------------------------------------------------
    # CONTORNO PRINCIPAL
    # ------------------------------------------------------

    indice_principal = encontrar_contorno_principal(
        contornos,
        jerarquia
    )

    if indice_principal is None:

        print()

        print(
            "No se encontro la silueta principal."
        )

        print()

        print(
            "Recomendacion:"
        )

        print(
            "- Fondo claro"
        )

        print(
            "- Hoja oscura"
        )

        print(
            "- Hoja claramente separada del fondo"
        )

        return

    print(
        "Contorno principal:",
        indice_principal
    )

    # ------------------------------------------------------
    # TODA LA JERARQUIA
    # ------------------------------------------------------

    indices = obtener_descendientes(
        indice_principal,
        contornos,
        jerarquia
    )

    print(
        "Contornos de la hoja:",
        len(indices)
    )

    # ------------------------------------------------------
    # COORDENADAS
    # ------------------------------------------------------

    coordenadas = extraer_coordenadas(
        contornos,
        indices,
        jerarquia,
        ancho,
        alto
    )

    # ------------------------------------------------------
    # ESTADISTICAS
    # ------------------------------------------------------

    total_puntos = sum(
        len(datos["puntos"])
        for datos in coordenadas
    )

    exteriores = sum(
        1
        for datos in coordenadas
        if datos["tipo"] == "EXTERIOR"
    )

    huecos = sum(
        1
        for datos in coordenadas
        if datos["tipo"] == "HUECO"
    )

    detalles = sum(
        1
        for datos in coordenadas
        if datos["tipo"] == "DETALLE"
    )

    print()

    print(
        "============================================"
    )

    print(
        "RESULTADOS"
    )

    print(
        "============================================"
    )

    print(
        "Puntos generados:",
        total_puntos
    )

    print(
        "Contornos exteriores:",
        exteriores
    )

    print(
        "Huecos interiores:",
        huecos
    )

    print(
        "Detalles internos:",
        detalles
    )

    print()

    # ------------------------------------------------------
    # GENERAR CODIGO
    # ------------------------------------------------------

    nombre = os.path.basename(
        ruta
    )

    print(
        "Generando codigo..."
    )

    codigo = generar_codigo_turtle(
        coordenadas,
        nombre
    )

    # ------------------------------------------------------
    # GUARDAR
    # ------------------------------------------------------

    archivo_python, archivo_coordenadas = guardar_resultados(
        ruta,
        coordenadas,
        codigo
    )

    vertices, caras = construir_malla_3d(
        profundidad,
        mascara
    )

    archivo_obj, archivo_json_3d = guardar_reconstruccion_3d(
        ruta,
        vertices,
        caras,
        profundidad
    )

    # ------------------------------------------------------
    # FINAL
    # ------------------------------------------------------

    print()

    print(
        "============================================"
    )

    print(
        "PROCESO TERMINADO"
    )

    print(
        "============================================"
    )

    print()

    print(
        "Archivo Python:"
    )

    print(
        archivo_python
    )

    print()

    print(
        "Archivo de coordenadas:"
    )

    print(
        archivo_coordenadas
    )

    print()

    print(
        "Metodo 3D:"
    )

    print(
        metodo_3d
    )

    print()

    print(
        "Malla OBJ:"
    )

    print(
        archivo_obj
    )

    print()

    print(
        "Datos 3D JSON:"
    )

    print(
        archivo_json_3d
    )

    print()

    print(
        "Puntos:",
        total_puntos
    )

    print(
        "Huecos:",
        huecos
    )

    print(
        "Detalles:",
        detalles
    )

    print()

    print(
        "Abre el archivo *_silueta.py"
    )

    print(
        "para ver la reconstruccion."
    )

    print()


# ==========================================================
# EJECUTAR
# ==========================================================

if __name__ == "__main__":

    main()
