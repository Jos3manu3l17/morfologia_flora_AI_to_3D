"""
Generar imagen de prueba sintética para validar estimar_relieve.py
"""

import numpy as np
import cv2
import json

# Crear una imagen sintética que simule una hoja con variaciones de intensidad
alto, ancho = 400, 600
imagen = np.ones((alto, ancho), dtype=np.uint8) * 200  # Fondo claro

# Crear forma de hoja simple (elíptica)
centro_y, centro_x = alto // 2, ancho // 2
y, x = np.ogrid[:alto, :ancho]
mascara_hoja = ((x - centro_x)**2 / (ancho//3)**2 + (y - centro_y)**2 / (alto//2.5)**2) <= 1

# Añadir variaciones de intensidad para simular relieve
# Simulamos una "veta" central más oscura
veta_central = np.exp(-((x - centro_x)**2) / (ancho//10)**2)
imagen = imagen - (veta_central * 80).astype(np.uint8)

# Añadir algunas "manchas" para simular textura
np.random.seed(42)
ruido = np.random.randn(alto, ancho) * 15
imagen = imagen + ruido.astype(np.uint8)

# Aplicar máscara
imagen[~mascara_hoja] = 200

# Guardar imagen
cv2.imwrite('hoja_prueba.png', imagen)

# Crear un archivo silueta.py correspondiente simple
# Usamos landmarks elípticos simples
theta = np.linspace(0, 2*np.pi, 100)
x_landmarks = (ancho//3) * np.cos(theta)
y_landmarks = (alto//2.5) * np.sin(theta)

# Convertir al sistema de coordenadas del proyecto (origen centro, Y hacia arriba)
landmarks_proyecto = []
for x, y in zip(x_landmarks, y_landmarks):
    x_proj = x  # Ya está centrado
    y_proj = -y  # Invertir Y para sistema del proyecto
    landmarks_proyecto.append((float(x_proj), float(y_proj)))

# Generar código silueta.py
codigo_silueta = f"""
import tkinter as tk

ventana = tk.Tk()
ventana.title("Hoja prueba")
ventana.geometry('600x400')
ventana.configure(bg='white')

canvas = tk.Canvas(ventana, width=600, height=400, bg='white', highlightthickness=0)
canvas.pack()

puntos = [
"""
for x, y in landmarks_proyecto:
    # Transformar al sistema de visualización (coordenadas pantalla)
    cx = x + 300  # centro_x
    cy = 200 - y  # centro_y - y (inversión)
    codigo_silueta += f"    ({cx:.1f}, {cy:.1f}),\n"

codigo_silueta += """]

canvas.create_polygon(puntos, fill='black', outline='black')
ventana.mainloop()
"""

with open('hoja_prueba_silueta.py', 'w') as f:
    f.write(codigo_silueta)

print("Imagen de prueba creada: hoja_prueba.png")
print("Silueta correspondiente: hoja_prueba_silueta.py")
print(f"Landmarks generados: {len(landmarks_proyecto)} puntos")