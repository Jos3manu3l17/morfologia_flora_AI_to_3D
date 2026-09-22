"""
==============================================================
ESTIMADOR DE RELIEVE 3D (SHAPE-FROM-SHADING)
==============================================================

MVP para estimar mapa de altura h(x,y) desde una imagen cenital
usando shape-from-shading simple de una sola vista.

Limitaciones conocidas:
- Shape-from-shading de una sola vista asume albedo uniforme
- Confundirá variación de textura/color (venas, manchas) con relieve real
- Resultado es relativo, no métrico (necesita calibración para medidas reales)

==============================================================
"""

import cv2
import numpy as np
import json
import os
from scipy import interpolate


# ==============================================================
# CONFIGURACIÓN
# ==============================================================

ALTURA_RELIEVE_DEFAULT = 20.0  # Escala máxima para el relieve (unidades arbitrarias)
METODO_DEFAULT = "gradiente_intensidad_normalizado"


# ==============================================================
# SHAPE-FROM-SHADING SIMPLE
# ==============================================================

def estimar_relieve_sfs(imagen, mascara, metodo="gradiente_intensidad_normalizado"):
    """
    Estima mapa de altura usando shape-from-shading simple de una sola vista.
    
    Métodos implementados:
    - "gradiente_intensidad_normalizado": Usa gradiente de intensidad normalizado por silueta
    - "intensidad_invertida": Inversión simple de intensidad (zonas oscuras = relieve alto)
    
    Args:
        imagen: Array numpy (H, W) en escala de grises
        mascara: Array numpy (H, W) binaria (255 dentro de la hoja, 0 fuera)
        metodo: Método de estimación a usar
    
    Returns:
        mapa_altura: Array numpy (H, W) normalizado 0-1 dentro de la silueta
    """
    if metodo == "gradiente_intensidad_normalizado":
        return _sfs_gradiente_normalizado(imagen, mascara)
    elif metodo == "intensidad_invertida":
        return _sfs_intensidad_invertida(imagen, mascara)
    else:
        raise ValueError(f"Método desconocido: {metodo}")


def _sfs_gradiente_normalizado(imagen, mascara):
    """
    Shape-from-shading basado en gradiente de intensidad normalizado.
    
    Asumimos que las zonas relativamente oscuras corresponden a relieve alto
    (como en hojas donde las venas crean sombras). Normalizamos por la
    silueta para que el fondo no afecte la estimación.
    
    LIMITACIÓN: Confundirá venas oscuras con relieve alto, y manchas
    claras con depresiones, debido a la asunción de albedo uniforme.
    """
    # Convertir a float y normalizar 0-1
    imagen_float = imagen.astype(np.float32) / 255.0
    
    # Aplicar suavizado para reducir ruido de textura
    imagen_suave = cv2.GaussianBlur(imagen_float, (0, 0), 2.0)
    
    # Máscara binaria normalizada
    mascara_bin = (mascara > 0).astype(np.float32)
    
    # Extraer solo los píxeles dentro de la silueta
    dentro = mascara_bin > 0
    if not np.any(dentro):
        return np.zeros_like(imagen_float)
    
    valores_dentro = imagen_suave[dentro]
    minimo, maximo = float(valores_dentro.min()), float(valores_dentro.max())
    
    if maximo - minimo < 1e-6:
        # Imagen uniforme dentro de la silueta
        return np.zeros_like(imagen_float)
    
    # Normalizar dentro de la silueta: zonas oscuras -> relieve alto (1.0)
    # Zonas claras -> relieve bajo (0.0)
    normalizado = 1.0 - (imagen_suave - minimo) / (maximo - minimo)
    
    # Aplicar máscara (fuera de la silueta = 0)
    mapa_altura = normalizado * mascara_bin
    
    # Suavizado adicional para reducir artefactos de textura
    mapa_altura = cv2.GaussianBlur(mapa_altura, (0, 0), 1.5)
    
    return mapa_altura


def _sfs_intensidad_invertida(imagen, mascara):
    """
    Shape-from-shading ultra-simple: inversión de intensidad.
    
    Asumimos directamente: píxel oscuro = relieve alto.
    Método más simple pero más susceptible a ruido y variación de albedo.
    """
    imagen_float = imagen.astype(np.float32) / 255.0
    mascara_bin = (mascara > 0).astype(np.float32)
    
    # Invertir intensidad
    mapa_altura = (1.0 - imagen_float) * mascara_bin
    
    return mapa_altura


# ==============================================================
# TRANSFORMACIÓN DE COORDENADAS (CRÍTICO)
# ==============================================================

def landmarks_a_espacio_imagen(landmarks_2d, forma_imagen):
    """
    Transforma landmarks del sistema de coordenadas del proyecto al espacio de imagen.
    
    SISTEMA DE COORDENADAS DEL PROYECTO (landmarks):
    - Origen: centro de la imagen
    - Eje Y: hacia arriba (positivo = arriba)
    - Unidades: píxeles desde el centro
    
    SISTEMA DE COORDENADAS DE IMAGEN (OpenCV):
    - Origen: esquina superior izquierda
    - Eje Y: hacia abajo (positivo = abajo)
    - Unidades: píxeles desde la esquina
    
    TRANSFORMACIÓN:
    - x_imagen = x_landmark + ancho/2
    - y_imagen = alto/2 - y_landmark  # NOTA: inversión de Y
    
    Esta es la transformación MÁS CRÍTICA y fácil de romper sin notarlo.
    Un error aquí causará que el relieve se mapee en posiciones incorrectas.
    
    Args:
        landmarks_2d: Array numpy (N, 2) con landmarks en sistema del proyecto
        forma_imagen: Tuple (alto, ancho) de la imagen
    
    Returns:
        landmarks_imagen: Array numpy (N, 2) en espacio de imagen
    """
    alto, ancho = forma_imagen
    centro_x = ancho / 2
    centro_y = alto / 2
    
    landmarks_imagen = np.zeros_like(landmarks_2d)
    
    # Transformación explícita con comentarios
    landmarks_imagen[:, 0] = landmarks_2d[:, 0] + centro_x  # x: mismo sistema, solo traslación
    landmarks_imagen[:, 1] = centro_y - landmarks_2d[:, 1]  # y: inversión + traslación
    
    return landmarks_imagen


def landmarks_a_espacio_proyecto(landmarks_imagen, forma_imagen):
    """
    Transforma landmarks del espacio de imagen al sistema de coordenadas del proyecto.
    
    TRANSFORMACIÓN INVERSA:
    - x_landmark = x_imagen - ancho/2
    - y_landmark = alto/2 - y_imagen  # NOTA: inversión de Y
    
    Args:
        landmarks_imagen: Array numpy (N, 2) en espacio de imagen
        forma_imagen: Tuple (alto, ancho) de la imagen
    
    Returns:
        landmarks_2d: Array numpy (N, 2) en sistema del proyecto
    """
    alto, ancho = forma_imagen
    centro_x = ancho / 2
    centro_y = alto / 2
    
    landmarks_2d = np.zeros_like(landmarks_imagen)
    
    # Transformación inversa explícita
    landmarks_2d[:, 0] = landmarks_imagen[:, 0] - centro_x  # x: traslación inversa
    landmarks_2d[:, 1] = centro_y - landmarks_imagen[:, 1]  # y: inversión + traslación inversa
    
    return landmarks_2d


# ==============================================================
# MAPEO DE RELIEVE A LANDMARKS
# ==============================================================

def mapear_relieve_a_landmarks(mapa_altura, landmarks_2d, altura_max=ALTURA_RELIEVE_DEFAULT):
    """
    Convierte landmarks 2D en 3D añadiendo coordenada Z del relieve.
    
    Proceso:
    1. Transformar landmarks al espacio de imagen (CRÍTICO)
    2. Interpolar valor Z del mapa de altura para cada landmark
    3. Escalar Z por altura_max
    4. Devolver landmarks 3D en sistema de coordenadas del proyecto
    
    Args:
        mapa_altura: Array numpy (H, W) normalizado 0-1 de altura
        landmarks_2d: Array numpy (N, 2) de landmarks en sistema del proyecto
        altura_max: Escala para Z (default 20.0)
    
    Returns:
        landmarks_3d: Array numpy (N, 3) con coordenadas [x, y, z]
    """
    forma_imagen = mapa_altura.shape  # (alto, ancho)
    
    # PASO 1: Transformar landmarks al espacio de imagen (CRÍTICO)
    landmarks_imagen = landmarks_a_espacio_imagen(landmarks_2d, forma_imagen)
    
    # PASO 2: Interpolar valor Z para cada landmark
    # Usamos interpolación bilineal para valores suaves
    alto, ancho = forma_imagen
    
    # Crear función de interpolación
    # grid_x, grid_y son las coordenadas de los píxeles (DEBEN estar en orden creciente)
    grid_x = np.arange(ancho)  # [0, 1, 2, ..., ancho-1]
    grid_y = np.arange(alto)    # [0, 1, 2, ..., alto-1]
    
    # Interpolador bilineal
    interp_func = interpolate.RectBivariateSpline(grid_y, grid_x, mapa_altura)
    
    # Evaluar en las posiciones de los landmarks
    # Nota: RectBivariateSpline espera (y, x) en ese orden
    valores_z = interp_func.ev(landmarks_imagen[:, 1], landmarks_imagen[:, 0])
    
    # Re-normalizar para usar el rango completo disponible [0, 1]
    # Esto corrige el bug donde el mapa de altura no usa el rango completo
    z_min, z_max = valores_z.min(), valores_z.max()
    if z_max - z_min > 1e-6:
        valores_z = (valores_z - z_min) / (z_max - z_min)
    else:
        valores_z = np.zeros_like(valores_z)
    
    # PASO 3: Escalar por altura_max
    valores_z_escalados = valores_z * altura_max
    
    # PASO 4: Construir landmarks 3D en sistema del proyecto
    landmarks_3d = np.column_stack([
        landmarks_2d[:, 0],  # x (sin cambios)
        landmarks_2d[:, 1],  # y (sin cambios)  
        valores_z_escalados  # z (del relieve)
    ])
    
    return landmarks_3d


# ==============================================================
# GUARDAR/CARGAR DATOS DE RELIEVE
# ==============================================================

def guardar_relieve_json(mapa_altura, landmarks_3d, ruta_salida, altura_max=ALTURA_RELIEVE_DEFAULT, 
                         metodo=METODO_DEFAULT):
    """
    Guarda datos de relieve en formato JSON.
    
    Args:
        mapa_altura: Array numpy (H, W) normalizado 0-1
        landmarks_3d: Array numpy (N, 3) con coordenadas [x, y, z]
        ruta_salida: Ruta del archivo JSON de salida
        altura_max: Escala máxima usada para Z
        metodo: Método de estimación utilizado
    """
    datos = {
        "tipo": "mapa_relieve_sfs",
        "resolucion": list(mapa_altura.shape),  # [alto, ancho]
        "altura_max": altura_max,
        "metodo": metodo,
        "mapa_altura": mapa_altura.tolist(),  # Array 2D como lista de listas
        "landmarks_relieve": landmarks_3d.tolist(),  # Landmarks 3D
        "metadatos": {
            "metodo": metodo,
            "limitaciones": [
                "Shape-from-shading de una sola vista asume albedo uniforme",
                "Confundirá variación de textura/color con relieve real",
                "Resultado es relativo, no métrico"
            ]
        }
    }
    
    directorio = os.path.dirname(ruta_salida)
    if directorio:  # Solo crear directorio si no está vacío
        os.makedirs(directorio, exist_ok=True)
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    return ruta_salida


def cargar_relieve_json(ruta_entrada):
    """
    Carga datos de relieve desde archivo JSON.
    
    Args:
        ruta_entrada: Ruta del archivo JSON
    
    Returns:
        datos: Diccionario con datos de relieve
    """
    with open(ruta_entrada, encoding="utf-8") as f:
        datos = json.load(f)
    
    # Convertir listas a arrays numpy
    datos["mapa_altura"] = np.array(datos["mapa_altura"])
    datos["landmarks_relieve"] = np.array(datos["landmarks_relieve"])
    
    return datos


# ==============================================================
# FUNCIÓN PRINCIPAL DE PROCESAMIENTO
# ==============================================================

def procesar_imagen_con_relieve(ruta_imagen, ruta_silueta, ruta_salida, 
                                metodo=METODO_DEFAULT, altura_max=ALTURA_RELIEVE_DEFAULT):
    """
    Procesa una imagen para estimar su relieve y mapearlo a landmarks existentes.
    
    Flujo completo:
    1. Cargar imagen y landmarks existentes
    2. Estimar mapa de altura con shape-from-shading
    3. Mapear relieve a landmarks 2D -> 3D
    4. Guardar resultados en JSON
    
    Args:
        ruta_imagen: Ruta de la imagen original
        ruta_silueta: Ruta del archivo *_silueta.py con landmarks 2D
        ruta_salida: Ruta del archivo JSON de salida
        metodo: Método de shape-from-shading a usar
        altura_max: Escala máxima para el relieve
    
    Returns:
        datos_relieve: Diccionario con resultados completos
    """
    # Cargar imagen
    imagen = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise ValueError(f"No se pudo cargar la imagen: {ruta_imagen}")
    
    # Crear máscara simple (umbral) - podría mejorarse usando la silueta existente
    _, mascara = cv2.threshold(imagen, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Estimar mapa de altura
    mapa_altura = estimar_relieve_sfs(imagen, mascara, metodo=metodo)
    
    # Cargar landmarks 2D existentes
    from modelo_forma_especie import extraer_puntos
    landmarks_2d = extraer_puntos(ruta_silueta)
    
    # Mapear relieve a landmarks
    landmarks_3d = mapear_relieve_a_landmarks(mapa_altura, landmarks_2d, altura_max=altura_max)
    
    # Guardar resultados
    guardar_relieve_json(mapa_altura, landmarks_3d, ruta_salida, altura_max=altura_max, metodo=metodo)
    
    return {
        "mapa_altura": mapa_altura,
        "landmarks_2d": landmarks_2d,
        "landmarks_3d": landmarks_3d,
        "ruta_salida": ruta_salida
    }


# ==============================================================
# MAIN (para uso desde línea de comandos)
# ==============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Estimar relieve 3D desde imagen cenital usando shape-from-shading"
    )
    parser.add_argument("imagen", help="Ruta de la imagen cenital")
    parser.add_argument("silueta", help="Ruta del archivo *_silueta.py con landmarks 2D")
    parser.add_argument("salida", help="Ruta del archivo JSON de salida")
    parser.add_argument("--metodo", default=METODO_DEFAULT, 
                       help="Método de shape-from-shading (default: gradiente_intensidad_normalizado)")
    parser.add_argument("--altura-max", type=float, default=ALTURA_RELIEVE_DEFAULT,
                       help="Altura máxima del relieve (default: 20.0)")
    
    args = parser.parse_args()
    
    resultado = procesar_imagen_con_relieve(
        args.imagen, 
        args.silueta, 
        args.salida,
        metodo=args.metodo,
        altura_max=args.altura_max
    )
    
    print(f"Relieve estimado y guardado en: {args.salida}")
    print(f"Landmarks 2D: {len(resultado['landmarks_2d'])} puntos")
    print(f"Landmarks 3D: {len(resultado['landmarks_3d'])} puntos")
    print(f"Rango de relieve: [{resultado['landmarks_3d'][:, 2].min():.2f}, {resultado['landmarks_3d'][:, 2].max():.2f}]")