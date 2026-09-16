# Investigación Personal: Captura de Relieve 3D en Morfología Vegetal

## Diagnóstico del Problema Actual

### Limitación Identificada
El sistema actual logra un modelado efectivo de siluetas de hojas en 2D, pero presenta una limitación fundamental: las formas generadas terminan siendo estructuras planas y rectas. Aunque se puede aplicar extrusión en 3ds Max, el resultado carece del relieve característico de las especies vegetales reales.

### Manifestación del Problema
- **Extrusión Plana**: Las hojas generadas son superficies planas sin variaciones de profundidad
- **Pérdida de Características**: Ondulaciones, venas prominentes, texturas superficiales y curvaturas naturales no se capturan
- **Representación Incompleta**: Vista cenital puede ser aceptable, pero vista lateral muestra falta de fidelidad morfológica
- **Simplificación Excesiva**: La complejidad tridimensional de las hojas se reduce a siluetas bidimensionales

## Nueva Dirección de Investigación

### Objetivo Principal
Desarrollar un sistema capaz de capturar y modelar el relieve tridimensional de las hojas, generando representaciones que sean fieles tanto en vista cenital como lateral, incorporando las ondulaciones y características volumétricas propias de cada especie.

### Pregunta de Investigación Personal
¿Cómo se puede capturar, modelar y generar el relieve tridimensional de hojas vegetales a partir de múltiples muestras de cada especie, para lograr representaciones que mantengan fidelidad morfológica en todas las dimensiones espaciales?

## Hipótesis de Trabajo

### H1: Hipótesis de Muestreo Multi-angular
La captura de imágenes desde múltiples ángulos (cenital, lateral, oblicuo) de las mismas hojas permitirá reconstruir la geometría 3D mediante técnicas de fotogrametría o visión estéreo.

### H2: Hipótesis de Variabilidad Superficial
Las ondulaciones y relieve de las hojas siguen patrones consistentes dentro de una especie que pueden ser modelados estadísticamente de manera similar a como se modelan las siluetas 2D actuales.

### H3: Hipótesis de Integración 2D-3D
Es posible integrar el sistema actual de modelado de siluetas 2D con un nuevo sistema de modelado de relieve 3D, manteniendo la coherencia entre contorno y volumen.

## Propuesta de Solución Técnica

### Fase 1: Captura de Datos 3D

**1.1 Protocolo de Adquisición Multi-angular**
- **Vistas Requeridas**:
  - Vista cenital (top-down): Para contorno y patrones superficiales
  - Vista lateral (side-view): Para curvatura y perfil vertical
  - Vista oblicua (45°): Para capturar transiciones y relieve intermedio
  - Vista invertida (bottom-up): Para venas prominentes en el envés

- **Equipamiento Sugerido**:
  - Sistema de giro controlado (turntable) para rotación precisa
  - Iluminación difusa para minimizar sombras que confundan el relieve
  - Cámara calibrada con parámetros intrínsecos conocidos
  - Escala de referencia para reconstrucción métrica

**1.2 Extracción de Información de Profundidad**
- **Técnicas a Explorar**:
  - **Fotogrametría**: Reconstrucción 3D desde múltiples imágenes
  - **Shape from Shading**: Estimación de profundidad desde variaciones de iluminación
  - **Estereovisión**: Pares estéreo para cálculo de disparidad
  - **Luz Estructurada**: Proyección de patrones para captura de relieve

### Fase 2: Modelado de Relieve

**2.1 Representación de Superficie**
- **Malla 3D Paramétrica**: 
  - Malla base derivada de silueta 2D existente
  - Desplazamiento vertical (Z) en cada punto del contorno
  - Función de altura h(x,y) que modula la superficie

- **Mapas de Desplazamiento**:
  - Displacement maps derivados de datos de profundidad
  - Texturas de altura para venas y ondulaciones
  - Normal maps para iluminación realista

**2.2 Modelado Estadístico de Relieve**
- **Análisis de Componentes Principales 3D**:
  - Extensión del PCA actual a vectores 3D (x,y,z)
  - Modelado de variabilidad en la dimensión de profundidad
  - Componentes principales que capturen patrones de ondulación

- **Correspondencia de Superficie**:
  - Alineación de mallas 3D mediante Procrustes 3D
  - Landmarks superficiales además de contornos
  - Modelado de venas como características estructurales

### Fase 3: Integración con Sistema Actual

**3.1 Pipeline Extendido**
```
Imágenes Multi-angulares → Reconstrucción 3D → Malla + Silueta
                                                      ↓
                                        Alineación 2D + 3D
                                                      ↓
                                  Modelo Estadístico Híbrido
                                                      ↓
                                Generación de Variantes 3D
```

**3.2 Compatibilidad con Código Existente**
- Mantener funcionalidad de extractor_siluetas.py para casos 2D
- Extender modelo_forma_especie.py para manejar coordenadas 3D
- Adaptar convertir_a_maxscript.py para exportar mallas 3D completas
- Generar nuevos scripts para procesamiento específico 3D

## Elementos de Recolección de Datos

### Dataset Multi-angular Requerido

**Por Especie:**
- Mínimo 5-8 hojas diferentes
- Cada hoja fotografiada desde 4-6 ángulos distintos
- Total de 20-48 imágenes por especie para análisis robusto

**Metadatos a Capturar:**
- Ángulo de la cámara respecto a la hoja
- Distancia y parámetros de la cámara
- Condiciones de iluminación
- Información de escala (objeto de referencia)
- Estado de la hoja (fresca, seca, etc.)

### Instrumentos de Medición 3D

**1. Sistema de Reconstrucción**
- Software: COLMAP, MeshLab, o desarrollo propio
- Salida: Nubes de puntos, mallas 3D, texturas
- Métricas: Densidad de puntos, calidad de malla, error de reconstrucción

**2. Análisis de Superficie**
- Curvatura media y gaussiana
- Área superficial vs área proyectada
- Profundidad máxima y distribución
- Detección de venas y crestas

**3. Validación Geométrica**
- Comparación con mediciones físicas (calibradores)
- Consistencia entre vistas diferentes
- Detección de artefactos de reconstrucción

## Solución Esperada

### Objetivos Técnicos

**1. Reconstrucción 3D Fiable**
- Error de reconstrucción < 2% del tamaño de la hoja
- Densidad de malla suficiente para capturar detalles de venas
- Tiempo de procesamiento < 5 minutos por hoja

**2. Modelado Estadístico de Relieve**
- PCA 3D que explique ≥85% de varianza superficial
- Componentes principales interpretables (ej: curvatura general, patrones de venas)
- Generación de variantes con relieve realista

**3. Fidelidad Multi-angular**
- Similitud > 90% con fotos reales en vista cenital
- Similitud > 85% con fotos reales en vista lateral
- Consistencia morfológica en todas las proyecciones

### Métricas de Éxito

**Métricas Geométricas:**
- Error RMSE entre malla reconstruida y realidad
- Preservación de características estructurales (venas, nervaduras)
- Suavidad de superficie (ausencia de artefactos)

**Métricas Perceptuales:**
- Evaluación por expertos de fidelidad en relieve
- Clasificación correcta de especie desde múltiples ángulos
- Preferencia sobre modelos puramente 2D

**Métricas de Rendimiento:**
- Tiempo de captura y procesamiento
- Tamaño de archivos de mallas 3D
- Escalabilidad a múltiples especies

## Informe de Investigación Personal

### Estructura del Documento

**1. Contexto y Motivación**
- Evolución del proyecto desde siluetas 2D a modelos 3D
- Limitaciones observadas en el sistema actual
- Importancia del relieve en morfología vegetal

**2. Estado del Arte en Reconstrucción 3D Vegetal**
- Técnicas existentes en fotogrametría de plantas
- Sistemas comerciales de escaneo botánico
- Investigación académica en modelado de hojas 3D

**3. Metodología Propuesta**
- Protocolo detallado de captura multi-angular
- Algoritmos de reconstrucción y alineación
- Extensión del sistema de modelado estadístico

**4. Implementación Técnica**
- Arquitectura del sistema extendido
- Scripts y herramientas desarrolladas
- Integración con código existente

**5. Resultados Experimentales**
- Pruebas con especies piloto
- Comparación entre métodos de reconstrucción
- Validación de fidelidad 3D

**6. Discusión y Lecciones Aprendidas**
- Desafíos técnicos encontrados
- Soluciones desarrolladas
- Limitaciones del enfoque

**7. Conclusiones y Trabajo Futuro**
- Logros alcanzados
- Recomendaciones para implementación
- Direcciones para investigaciones adicionales

## Plan de Implementación

### Etapa 1: Prototipo de Captura (2-3 semanas)
- Configurar sistema básico de fotografía multi-angular
- Desarrollar protocolo de calibración
- Realizar pruebas con 2-3 especies simples

### Etapa 2: Reconstrucción 3D (3-4 semanas)
- Implementar pipeline de fotogrametría
- Desarrollar scripts de procesamiento de mallas
- Validar calidad de reconstrucciones

### Etapa 3: Modelado Estadístico (4-5 semanas)
- Extender PCA a coordenadas 3D
- Desarrollar alineación Procrustes 3D
- Implementar generación de variantes con relieve

### Etapa 4: Integración y Validación (3-4 semanas)
- Integrar con sistema existente
- Validar fidelidad multi-angular
- Optimizar rendimiento

## Aplicaciones Potenciales

**Botánica Científica:**
- Documentación precisa de morfología 3D
- Análisis de adaptaciones estructurales
- Apoyo a taxonomía basada en forma

**Diseño Biomimético:**
- Inspiración para estructuras arquitectónicas
- Diseño de superficies funcionales
- Prototipado de elementos orgánicos

**Educación Virtual:**
- Modelos 3D interactivos para enseñanza
- Laboratorios virtuales de botánica
- Visualización de biodiversidad

**Industria:**
- Diseño de productos inspirados en naturaleza
- Texturas y patrones biomiméticos
- Simulación de comportamiento de superficies vegetales

## Referencias Técnicas

**Fotogrametría y Visión 3D:**
- Hartley, R., & Zisserman, A. (2003). "Multiple View Geometry in Computer Vision"
- Szeliski, R. (2010). "Computer Vision: Algorithms and Applications"
- Furukawa, Y., & Ponce, J. (2010). "Accurate, Dense, and Robust Multi-View Stereopsis"

**Morfología Vegetal 3D:**
- Price, C. A., et al. (2011). "The Leaf Morphology Database (LMD)"
- Runions, A., et al. (2017). "Modeling leaf development"
- Boudon, F., et al. (2019). "3D plant modeling and visualization"

**Procesamiento de Mallas:**
- Botsch, M., et al. (2010). "Polygon Mesh Processing"
- Crane, K., et al. (2017). "Discrete Differential Geometry"

Este enfoque personal representa una evolución natural del proyecto actual, manteniendo la base sólida de modelado estadístico de siluetas mientras se añade la dimensión de relieve necesaria para representaciones 3D fieles y completas de las especies vegetales.