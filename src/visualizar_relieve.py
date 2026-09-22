"""
==============================================================
VISUALIZADOR DE RELIEVE 3D
==============================================================

Script para validar visualmente los resultados de estimación de relieve.

Muestra:
- Imagen original
- Mapa de altura (heatmap)
- Landmarks 2D originales
- Landmarks 3D proyectados (con código de color por altura)
- Comparación lado a lado

==============================================================
"""

import cv2
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from estimar_relieve import cargar_relieve_json, landmarks_a_espacio_imagen


def visualizar_relieve(ruta_imagen, ruta_relieve_json, salida=None):
    """
    Visualiza los resultados de estimación de relieve.
    
    Args:
        ruta_imagen: Ruta de la imagen original
        ruta_relieve_json: Ruta del archivo JSON con datos de relieve
        salida: Ruta opcional para guardar la visualización
    """
    # Cargar datos
    imagen = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise ValueError(f"No se pudo cargar la imagen: {ruta_imagen}")
    
    datos_relieve = cargar_relieve_json(ruta_relieve_json)
    mapa_altura = datos_relieve["mapa_altura"]
    landmarks_3d = datos_relieve["landmarks_relieve"]
    altura_max = datos_relieve["altura_max"]
    
    # Extraer landmarks 2D (sin Z)
    landmarks_2d = landmarks_3d[:, :2]
    valores_z = landmarks_3d[:, 2]
    
    # Crear figura con subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle(f'Validación de Relieve 3D - Método: {datos_relieve["metodo"]}', fontsize=14)
    
    # 1. Imagen original con landmarks 2D
    ax1 = axes[0, 0]
    ax1.imshow(imagen, cmap='gray', origin='upper')
    ax1.set_title('Imagen Original + Landmarks 2D')
    ax1.axis('off')
    
    # Dibujar landmarks 2D (transformados al espacio de imagen)
    landmarks_imagen = landmarks_a_espacio_imagen(landmarks_2d, imagen.shape)
    ax1.plot(landmarks_imagen[:, 0], landmarks_imagen[:, 1], 'g-', linewidth=1, alpha=0.7, label='Landmarks 2D')
    ax1.scatter(landmarks_imagen[::20, 0], landmarks_imagen[::20, 1], c='lime', s=10, alpha=0.8)
    ax1.legend(loc='upper right')
    
    # 2. Mapa de altura (heatmap)
    ax2 = axes[0, 1]
    im = ax2.imshow(mapa_altura, cmap='terrain', origin='upper', vmin=0, vmax=1)
    ax2.set_title('Mapa de Altura (Shape-from-Shading)')
    ax2.axis('off')
    plt.colorbar(im, ax=ax2, label='Altura normalizada (0-1)')
    
    # 3. Mapa de altura con landmarks 3D codificados por color
    ax3 = axes[1, 0]
    ax3.imshow(mapa_altura, cmap='terrain', origin='upper', vmin=0, vmax=1)
    ax3.set_title('Mapa de Altura + Landmarks 3D (color = altura Z)')
    ax3.axis('off')
    
    # Normalizar valores Z para colorear
    z_norm = (valores_z - valores_z.min()) / (valores_z.max() - valores_z.min() + 1e-6)
    
    # Dibujar landmarks con color según altura Z
    scatter = ax3.scatter(landmarks_imagen[:, 0], landmarks_imagen[:, 1], 
                         c=z_norm, cmap='coolwarm', s=15, alpha=0.8,
                         vmin=0, vmax=1)
    plt.colorbar(scatter, ax=ax3, label='Altura Z (normalizada)')
    
    # 4. Perfil de altura a lo largo del contorno
    ax4 = axes[1, 1]
    # Ordenar landmarks por posición angular desde el centro para un perfil continuo
    centro = landmarks_2d.mean(axis=0)
    angulos = np.arctan2(landmarks_2d[:, 1] - centro[1], landmarks_2d[:, 0] - centro[0])
    orden = np.argsort(angulos)
    
    angulos_ordenados = angulos[orden]
    z_ordenados = valores_z[orden]
    
    ax4.plot(np.degrees(angulos_ordenados), z_ordenados, 'b-', linewidth=2)
    ax4.set_xlabel('Ángulo (grados)')
    ax4.set_ylabel('Altura Z')
    ax4.set_title('Perfil de Altura del Contorno')
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=valores_z.mean(), color='r', linestyle='--', alpha=0.7, label=f'Promedio: {valores_z.mean():.2f}')
    ax4.legend()
    
    plt.tight_layout()
    
    if salida:
        plt.savefig(salida, dpi=150, bbox_inches='tight')
        print(f"Visualización guardada en: {salida}")
    else:
        plt.show()
    
    plt.close()
    
    # Imprimir estadísticas
    print("\n=== ESTADÍSTICAS DE RELIEVE ===")
    print(f"Resolución mapa: {datos_relieve['resolucion']}")
    print(f"Altura máxima: {altura_max}")
    print(f"Rango Z: [{valores_z.min():.2f}, {valores_z.max():.2f}]")
    print(f"Promedio Z: {valores_z.mean():.2f}")
    print(f"Desviación estándar Z: {valores_z.std():.2f}")
    print(f"\nLandmarks procesados: {len(landmarks_3d)}")
    print(f"Método: {datos_relieve['metodo']}")
    print(f"\nLimitaciones conocidas:")
    for limitacion in datos_relieve['metadatos']['limitaciones']:
        print(f"  - {limitacion}")


def visualizar_comparacion_3d(ruta_imagen, ruta_relieve_json, salida=None):
    """
    Visualización alternativa enfocada en comparación 2D vs 3D.
    
    Args:
        ruta_imagen: Ruta de la imagen original
        ruta_relieve_json: Ruta del archivo JSON con datos de relieve
        salida: Ruta opcional para guardar la visualización
    """
    # Cargar datos
    imagen = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
    datos_relieve = cargar_relieve_json(ruta_relieve_json)
    mapa_altura = datos_relieve["mapa_altura"]
    landmarks_3d = datos_relieve["landmarks_relieve"]
    
    landmarks_2d = landmarks_3d[:, :2]
    valores_z = landmarks_3d[:, 2]
    
    # Crear figura
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Comparación: Imagen 2D vs Mapa de Relieve 3D', fontsize=14)
    
    # 1. Imagen original
    axes[0].imshow(imagen, cmap='gray', origin='upper')
    axes[0].set_title('Imagen Original (2D)')
    axes[0].axis('off')
    
    # 2. Mapa de altura
    im = axes[1].imshow(mapa_altura, cmap='terrain', origin='upper', vmin=0, vmax=1)
    axes[1].set_title('Mapa de Altura Estimado (3D)')
    axes[1].axis('off')
    plt.colorbar(im, ax=axes[1], label='Altura normalizada')
    
    # 3. Combinación: imagen con superposición de relieve
    axes[2].imshow(imagen, cmap='gray', origin='upper', alpha=0.7)
    axes[2].imshow(mapa_altura, cmap='terrain', origin='upper', alpha=0.3, vmin=0, vmax=1)
    axes[2].set_title('Superposición (Imagen + Relieve)')
    axes[2].axis('off')
    
    # Añadir landmarks en todas las vistas
    landmarks_imagen = landmarks_a_espacio_imagen(landmarks_2d, imagen.shape)
    
    for ax in axes:
        ax.plot(landmarks_imagen[:, 0], landmarks_imagen[:, 1], 'r-', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    
    if salida:
        plt.savefig(salida, dpi=150, bbox_inches='tight')
        print(f"Visualización comparativa guardada en: {salida}")
    else:
        plt.show()
    
    plt.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Visualizar resultados de estimación de relieve 3D"
    )
    parser.add_argument("imagen", help="Ruta de la imagen original")
    parser.add_argument("relieve", help="Ruta del archivo JSON con datos de relieve")
    parser.add_argument("--salida", help="Ruta opcional para guardar la visualización")
    parser.add_argument("--modo", default="completo", choices=["completo", "comparacion"],
                       help="Modo de visualización (default: completo)")
    
    args = parser.parse_args()
    
    if args.modo == "completo":
        visualizar_relieve(args.imagen, args.relieve, args.salida)
    else:
        visualizar_comparacion_3d(args.imagen, args.relieve, args.salida)