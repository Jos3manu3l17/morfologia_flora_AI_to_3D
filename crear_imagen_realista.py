"""
Generar imagen de prueba más realista simulando una hoja real
"""

import numpy as np
import cv2

# Crear imagen más grande y realista
alto, ancho = 500, 700
imagen = np.ones((alto, ancho), dtype=np.uint8) * 220  # Fondo claro

# Crear forma de hoja más realista (tipo lanceolada)
centro_y, centro_x = alto // 2, ancho // 2

# Forma base lanceolada
y, x = np.ogrid[:alto, :ancho]
# Forma más alargada con base más ancha
mascara_hoja = ((x - centro_x)**2 / (ancho//2.5)**2 + ((y - centro_y + 50)**2) / (alto//2)**2) <= 1

# Añadir relieve más realista simulando venas
# Vena principal central (más oscura)
distancia_central = np.abs(x - centro_x) / (ancho//20)
vena_central = np.exp(-distancia_central * 3) * 60

# Venas secundarias diagonales
venas_secundarias = np.zeros_like(imagen, dtype=np.float32)
for angulo in [-30, 30]:  # Venas a ±30 grados
    ang_rad = np.radians(angulo)
    x_rot = (x - centro_x) * np.cos(ang_rad) + (y - centro_y) * np.sin(ang_rad)
    y_rot = -(x - centro_x) * np.sin(ang_rad) + (y - centro_y) * np.cos(ang_rad)
    # Venas que se bifurcan desde el centro
    vena = np.exp(-np.abs(x_rot) / (ancho//15)) * np.exp(-np.abs(y_rot) / (alto//3)) * 30
    venas_secundarias += vena

# Variación de relieve desde el centro hacia los bordes
# Centro más alto, bordes más bajos (simulando curvatura natural)
distancia_borde = np.sqrt(((x - centro_x)/(ancho//2.5))**2 + ((y - centro_y + 50)/(alto//2))**2)
relieve_base = (1 - distancia_borde) * 40  # Centro más alto

# Combinar todos los efectos
variacion_intensidad = relieve_base + vena_central + venas_secundarias

# Añadir textura sutil más realista
np.random.seed(123)
textura = np.random.randn(alto, ancho) * 8

# Aplicar variaciones
imagen = imagen.astype(np.float32) - variacion_intensidad - textura

# Aplicar máscara
imagen[~mascara_hoja] = 220

# Normalizar y convertir a uint8
imagen = np.clip(imagen, 0, 255).astype(np.uint8)

# Guardar imagen
cv2.imwrite('hoja_realista.png', imagen)

# Crear landmarks correspondientes a esta forma
# Usar forma elíptica modificada para que coincida con la máscara
theta = np.linspace(0, 2*np.pi, 150)
x_landmarks = (ancho//2.5) * np.cos(theta)
y_landmarks = (alto//2) * np.sin(theta) - 50  # Desplazada hacia arriba

# Convertir al sistema de coordenadas del proyecto
landmarks_proyecto = []
for x, y in zip(x_landmarks, y_landmarks):
    x_proj = x
    y_proj = -y
    landmarks_proyecto.append((float(x_proj), float(y_proj)))

# Generar código silueta.py
codigo_silueta = f"""
import tkinter as tk

ventana = tk.Tk()
ventana.title("Hoja realista prueba")
ventana.geometry('700x500')
ventana.configure(bg='white')

canvas = tk.Canvas(ventana, width=700, height=500, bg='white', highlightthickness=0)
canvas.pack()

puntos = [
"""
for x, y in landmarks_proyecto:
    cx = x + 350  # centro_x
    cy = 250 - y  # centro_y - y
    codigo_silueta += f"    ({cx:.1f}, {cy:.1f}),\n"

codigo_silueta += """]

canvas.create_polygon(puntos, fill='black', outline='black')
ventana.mainloop()
"""

with open('hoja_realista_silueta.py', 'w') as f:
    f.write(codigo_silueta)

print("Imagen realista creada: hoja_realista.png")
print("Silueta correspondiente: hoja_realista_silueta.py")
print(f"Landmarks generados: {len(landmarks_proyecto)} puntos")
print("Características: vena central, venas secundarias, relieve desde centro a bordes")