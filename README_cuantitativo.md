# Investigación Cuantitativa: Morfología de Plantas AI to 3D

## Formulación del Problema

### Problema de Investigación
¿Es posible cuantificar y modelar matemáticamente la variabilidad morfológica de las hojas de diferentes especies vegetales para generar nuevas siluetas realistas mediante técnicas de morfometría geométrica y análisis estadístico?

### Hipótesis
- **H1**: Las siluetas de hojas de una misma especie pueden ser modeladas estadísticamente mediante análisis de componentes principales (PCA) después de la normalización mediante análisis de Procrustes.
- **H2**: La variabilidad morfológica intra-específica puede ser cuantificada mediante métricas de distancia RMS (Root Mean Square) entre formas alineadas.
- **H3**: La generación de nuevas hojas sintéticas basadas en el modelo estadístico mantendrá las características morfológicas esenciales de la especie dentro de rangos de variación aceptables.

### Variables de Estudio

**Variables Independientes:**
- Especie vegetal (cualitativa nominal)
- Número de muestras por especie (cuantitativa discreta)
- Parámetros de configuración del algoritmo (número de landmarks, componentes PCA)

**Variables Dependientes:**
- Distancia RMS entre formas alineadas (cuantitativa continua)
- Varianza explicada por componentes principales (cuantitativa continua)
- Precisión de reconstrucción de siluetas (cuantitativa continua)
- Tiempo de procesamiento computacional (cuantitativa continua)

**Variables de Control:**
- Calidad de las imágenes de entrada
- Resolución de las fotografías
- Condiciones de iluminación
- Orientación de las hojas en las fotos

## Elementos de Recolección de Datos

### Instrumentos de Medición

**1. Sistema de Extracción de Siluetas**
- **Software**: extractor_siluetas.py
- **Tecnología**: OpenCV con procesamiento de contornos jerárquicos
- **Parámetros de medición**:
  - Coordenadas (x,y) de puntos del contorno
  - Número total de puntos generados
  - Cantidad de contornos exteriores
  - Cantidad de huecos interiores
  - Cantidad de detalles internos

**2. Sistema de Análisis Morfométrico**
- **Software**: modelo_forma_especie.py
- **Técnicas**: 
  - Análisis de Procrustes generalizado
  - Análisis de Componentes Principales (PCA)
  - Detección de valores atípicos
- **Métricas calculadas**:
  - Distancia RMS entre formas
  - Varianza por componente principal
  - Porcentaje de varianza explicada acumulada

**3. Sistema de Generación y Validación**
- **Software**: generador_hojas_parametrico.py, generar.py
- **Parámetros**: intensidad de variación, semilla aleatoria
- **Métricas de salida**: número de puntos, fidelidad al modelo

### Procedimiento de Recolección

**Fase 1: Adquisición de Imágenes**
1. Seleccionar especies vegetales de interés
2. Fotografiar hojas individuales extendidas y planas
3. Mantener condiciones consistentes (fondo liso, iluminación uniforme)
4. Mínimo 8-10 muestras por especie para análisis estadístico robusto

**Fase 2: Extracción de Coordenadas**
1. Procesar cada imagen con extractor_siluetas.py
2. Extraer contorno exterior principal
3. Registrar métricas de calidad (número de puntos, detección de artefactos)
4. Validar visualmente la extracción

**Fase 3: Normalización y Alineación**
1. Aplicar análisis de Procrustes para alinear formas
2. Detectar y marcar valores atípicos (factor_std = 2.0)
3. Calcular forma promedio por especie
4. Registrar distancias RMS al promedio

**Fase 4: Modelado Estadístico**
1. Construir modelo PCA con 6 componentes principales
2. Calcular varianza explicada por cada componente
3. Documentar porcentaje de varianza acumulada
4. Guardar modelo en formato JSON

### Tamaño de Muestra

**Criterios de determinación:**
- Mínimo 5 muestras por especie (umbral técnico del algoritmo PCA)
- Recomendado 8-10 muestras para estabilidad estadística
- Ideal 15+ muestras para análisis de variabilidad intra-específica robusto

**Especies en dataset actual:**
- Euphorbia lactea: 5 muestras
- Mango: 6 muestras

## Solución Esperada

### Objetivos Cuantitativos

**1. Modelado Estadístico de Formas**
- Construir modelos PCA que expliquen ≥80% de varianza con ≤6 componentes
- Alcanzar distancias RMS promedio entre formas alineadas < 10% del tamaño de la hoja
- Identificar valores atípicos con sensibilidad > 90% y especificidad > 85%

**2. Generación de Variantes Sintéticas**
- Generar siluetas nuevas con intensidad de variación controlada (factor 0.5-2.0)
- Mantener fidelidad morfológica dentro de ±2 desviaciones estándar del promedio
- Procesamiento computacional < 5 segundos por hoja generada

**3. Validación Cuantitativa**
- Comparar métricas morfométricas entre hojas reales y generadas
- Calcular índices de similitud (distancia RMS, superposición de áreas)
- Establecer umbrales de aceptación para clasificación automática

### Métricas de Éxito

**Métricas de Precisión:**
- Porcentaje de varianza explicada acumulada por modelo PCA
- Error medio cuadrático (MSE) entre formas generadas y promedio
- Coeficiente de correlación entre landmarks correspondientes

**Métricas de Eficiencia:**
- Tiempo de extracción de siluetas por imagen
- Tiempo de entrenamiento de modelo por especie
- Tiempo de generación de variantes sintéticas

**Métricas de Calidad:**
- Tasa de detección de valores atípicos
- Porcentaje de hojas generadas dentro de rangos morfológicos aceptables
- Índice de similitud con especies reales correspondientes

### Resultados Esperados

**Análisis Estadístico:**
- Tablas de varianza explicada por componente principal
- Gráficos de dispersión de formas en espacio PCA
- Histogramas de distancias RMS intra-específicas
- Métricas de separabilidad entre especies

**Validación del Modelo:**
- Cross-validation con leave-one-out
- Análisis de estabilidad del modelo con diferentes tamaños de muestra
- Comparación con métodos generativos alternativos

## Informe de Investigación

### Estructura del Informe Final

**1. Introducción y Marco Teórico**
- Fundamentos de morfometría geométrica
- Análisis de Procrustes en biología comparada
- Aplicaciones de PCA en morfología vegetal

**2. Metodología**
- Descripción detallada del pipeline de procesamiento
- Justificación de parámetros técnicos
- Protocolo de recolección de datos

**3. Resultados**
- Análisis descriptivo de muestras por especie
- Resultados de alineación de Procrustes
- Análisis de componentes principales
- Detección y análisis de valores atípicos
- Evaluación de generación de variantes

**4. Discusión**
- Interpretación de componentes principales morfológicos
- Comparación de variabilidad entre especies
- Limitaciones del enfoque cuantitativo
- Implicaciones para botánica sistemática

**5. Conclusiones**
- Validación de hipótesis planteadas
- Contribuciones metodológicas
- Recomendaciones para investigaciones futuras

### Análisis Estadístico a Realizar

**Análisis Descriptivo:**
- Estadísticos de tendencia central (media, mediana) para métricas morfológicas
- Medidas de dispersión (desviación estándar, rango intercuartílico)
- Visualizaciones: boxplots, scatter plots, heatmaps

**Análisis Inferencial:**
- Pruebas de normalidad (Shapiro-Wilk) para distribuciones de distancias
- ANOVA para comparar variabilidad entre especies
- Análisis de correlación entre componentes principales

**Análisis Multivariado:**
- Análisis discriminante para clasificación de especies
- Clustering jerárquico de formas
- Análisis de componentes principales con visualización

### Validación y Reproducibilidad

**Control de Calidad:**
- Documentación de versiones de software
- Registro de semillas aleatorias para reproducibilidad
- Validación cruzada de resultados
- Comparación con datasets de referencia (si disponibles)

**Disponibilidad de Datos:**
- Dataset de siluetas en formato estructurado
- Modelos estadísticos en formato JSON
- Scripts de análisis reproducibles
- Documentación de procedimientos

## Aplicaciones Prácticas

**Botánica y Taxonomía:**
- Cuantificación de caracteres morfológicos para identificación de especies
- Análisis de variabilidad intra-específica
- Apoyo a revisiones taxonómicas

**Diseño y Arquitectura:**
- Generación de formas vegetales para diseño biomimético
- Creación de elementos arquitectónicos inspirados en naturaleza
- Prototipado rápido de formas orgánicas

**Educación:**
- Herramienta didáctica para enseñanza de morfología vegetal
- Visualización de variabilidad morfológica
- Laboratorios virtuales de botánica

## Referencias Metodológicas

- Bookstein, F. L. (1997). "Morphometric Tools for Landmark Data"
- Dryden, I. L., & Mardia, K. V. (2016). "Statistical Shape Analysis"
- Zelditch, M. L., et al. (2012). "Geometric Morphometrics for Biologists"
- Adams, D. C., et al. (2013). "A Method for Assessing Phylogenetic Least Squares Models"