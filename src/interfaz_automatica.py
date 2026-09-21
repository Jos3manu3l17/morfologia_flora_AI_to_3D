import json
import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import convertir_a_maxscript
import convertir_a_maxscript_mejorado
import extractor_siluetas
import generar
import entrenar_todo
import modelo_forma_especie
import generador_hojas_parametrico


RAIZ = Path(__file__).resolve().parent.parent


class InterfazAutomatica(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Morfologia Flora | Pipeline Automático 2D a 3D")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(bg="#eef2f3")

        self.variables = {}
        self.vistas = {}
        self.fotos_seleccionadas = []
        self._crear_estilos()
        self._crear_cabecera()
        self._crear_contenido()
        self._crear_estado()

    def _crear_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background="#eef2f3")
        estilo.configure("Card.TFrame", background="#ffffff")
        estilo.configure("TLabel", background="#eef2f3", foreground="#243238")
        estilo.configure("Card.TLabel", background="#ffffff", foreground="#243238")
        estilo.configure("Title.TLabel", background="#eef2f3", foreground="#173f43", font=("Segoe UI", 22, "bold"))
        estilo.configure("Subtitle.TLabel", background="#eef2f3", foreground="#5b6b70", font=("Segoe UI", 10))
        estilo.configure("CardTitle.TLabel", background="#ffffff", foreground="#173f43", font=("Segoe UI", 13, "bold"))
        estilo.configure("TButton", padding=(10, 7))
        estilo.configure("Accent.TButton", background="#147d74", foreground="#ffffff", padding=(12, 8))
        estilo.map("Accent.TButton", background=[("active", "#0f655e")])
        estilo.configure("TNotebook", background="#eef2f3", borderwidth=0)
        estilo.configure("TNotebook.Tab", padding=(16, 9), background="#dce5e5")
        estilo.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", "#147d74")])

    def _crear_cabecera(self):
        cabecera = ttk.Frame(self, padding=(28, 22, 28, 10))
        cabecera.pack(fill="x")
        ttk.Label(cabecera, text="Morfologia Flora", style="Title.TLabel").pack(anchor="w")
        ttk.Label(cabecera, text="Pipeline automatico: selecciona las fotos y el sistema genera el modelo 3D completo.", style="Subtitle.TLabel").pack(anchor="w", pady=(3, 0))

    def _crear_contenido(self):
        contenido = ttk.Frame(self, padding=28)
        contenido.pack(fill="both", expand=True)
        
        # Panel izquierdo: formulario con scroll
        panel_izquierdo = ttk.Frame(contenido)
        panel_izquierdo.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Canvas con scrollbar para el formulario
        canvas = tk.Canvas(panel_izquierdo, bg="#eef2f3", highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel_izquierdo, orient="vertical", command=canvas.yview)
        formulario = ttk.Frame(canvas, style="Card.TFrame", padding=18)
        
        formulario.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=formulario, anchor="nw", width=450)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Label(formulario, text="Configuracion del Proceso", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
        
        # Seleccion de fotos
        self._campo(formulario, "Fotos de hojas", "fotos", "", explorador=self._elegir_fotos)
        ttk.Label(formulario, text="Selecciona una o varias fotos de la misma especie (Ctrl+click para multiples).", style="Card.TLabel", wraplength=380).pack(anchor="w", pady=(0, 5))
        
        # Boton adicional para importar imagenes
        importar_frame = ttk.Frame(formulario, style="Card.TFrame")
        importar_frame.pack(fill="x", pady=8)
        
        ttk.Button(
            importar_frame, 
            text="📁 IMPORTAR IMÁGENES", 
            command=self._elegir_fotos,
            width=30
        ).pack(anchor="center", pady=4)
        
        # Especie
        self._campo(formulario, "Nombre de especie", "especie", "mango")
        
        # Carpeta de trabajo
        self._campo(formulario, "Carpeta de trabajo", "carpeta_trabajo", str(RAIZ / "fotos_procesadas"), explorador=self._elegir_carpeta_trabajo)
        
        # Parametros opcionales
        ttk.Separator(formulario, orient="horizontal").pack(fill="x", pady=15)
        ttk.Label(formulario, text="Parametros Avanzados (opcional)", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
        
        self._campo(formulario, "Cantidad a generar", "cantidad_hojas", "3", ancho=12)
        self._campo(formulario, "Intensidad variacion", "intensidad", "1.0", ancho=12)
        self._campo(formulario, "Extrusion 3D", "extrusion", "15", ancho=12)
        self._campo(formulario, "Tolerancia MAXScript", "tolerancia", "0.8", ancho=12)
        
        # Opciones de realismo 3D
        ttk.Separator(formulario, orient="horizontal").pack(fill="x", pady=15)
        ttk.Label(formulario, text="Realismo 3D", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
        
        self.con_venacion = tk.BooleanVar(value=True)
        self.grosor_variable = tk.BooleanVar(value=True)
        self.detalle_superficie = tk.BooleanVar(value=True)
        
        fila_venacion = ttk.Frame(formulario, style="Card.TFrame")
        fila_venacion.pack(fill="x", pady=5)
        ttk.Checkbutton(fila_venacion, text="Generar venación procedimental", variable=self.con_venacion, style="Card.TLabel").pack(side="left")
        
        fila_grosor = ttk.Frame(formulario, style="Card.TFrame")
        fila_grosor.pack(fill="x", pady=5)
        ttk.Checkbutton(fila_grosor, text="Grosor variable (más grueso en centro)", variable=self.grosor_variable, style="Card.TLabel").pack(side="left")
        
        fila_detalle = ttk.Frame(formulario, style="Card.TFrame")
        fila_detalle.pack(fill="x", pady=5)
        ttk.Checkbutton(fila_detalle, text="Detalle de superficie", variable=self.detalle_superficie, style="Card.TLabel").pack(side="left")
        
        self._campo(formulario, "Curvatura natural (°)", "curvatura", "5.0", ancho=12)
        
        # Boton principal
        ttk.Separator(formulario, orient="horizontal").pack(fill="x", pady=15)
        
        boton_frame = ttk.Frame(formulario, style="Card.TFrame")
        boton_frame.pack(fill="x", pady=12)
        
        ttk.Button(
            boton_frame, 
            text="🚀 EJECUTAR PIPELINE COMPLETO", 
            style="Accent.TButton", 
            command=self._ejecutar_pipeline,
            width=40
        ).pack(anchor="center", pady=8)
        
        ttk.Label(
            boton_frame, 
            text="Procesará: Extracción → Entrenamiento → Generación → MAXScript 3D", 
            style="Card.TLabel",
            wraplength=380
        ).pack(anchor="center", pady=(4, 0))
        
        # Boton de limpiar/reiniciar
        ttk.Separator(formulario, orient="horizontal").pack(fill="x", pady=15)
        
        limpiar_frame = ttk.Frame(formulario, style="Card.TFrame")
        limpiar_frame.pack(fill="x", pady=8)
        
        ttk.Button(
            limpiar_frame, 
            text="🧹 LIMPIAR / REINICIAR SESIÓN", 
            command=self._limpiar_sesion,
            width=30
        ).pack(anchor="center", pady=4)
        
        ttk.Label(
            limpiar_frame, 
            text="Limpia fotos seleccionadas para iniciar con nuevas muestras. Los modelos anteriores se conservan.", 
            style="Card.TLabel",
            wraplength=380
        ).pack(anchor="center", pady=(4, 0))
        
        # Panel derecho: vista previa y log
        panel_derecho = ttk.Frame(contenido)
        panel_derecho.pack(side="left", fill="both", expand=True)
        
        # Vista previa
        vista_previa = ttk.Frame(panel_derecho, style="Card.TFrame", padding=12)
        vista_previa.pack(fill="both", expand=True, pady=(0, 10))
        self.figura = Figure(figsize=(5, 4), dpi=100, facecolor="white")
        self.eje = self.figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figura, master=vista_previa)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self._limpiar_vista(self.eje, self.canvas, "Vista previa de resultados")
        
        # Log de proceso
        log_frame = ttk.Frame(panel_derecho, style="Card.TFrame", padding=12)
        log_frame.pack(fill="both", expand=True)
        ttk.Label(log_frame, text="Log del Proceso", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 5))
        
        self.log_text = tk.Text(log_frame, height=8, width=50, font=("Consolas", 9), bg="#f8f9fa", fg="#243238", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _crear_estado(self):
        pie = ttk.Frame(self, padding=(28, 0, 28, 18))
        pie.pack(fill="x")
        self.estado = tk.StringVar(value="Listo. Selecciona las fotos de las hojas.")
        ttk.Label(pie, textvariable=self.estado, style="Subtitle.TLabel").pack(side="left")
        self.progreso = ttk.Progressbar(pie, mode="indeterminate", length=170)
        self.progreso.pack(side="right")

    def _campo(self, parent, etiqueta, clave, valor="", ancho=52, explorador=None):
        fila = ttk.Frame(parent, style="Card.TFrame")
        fila.pack(fill="x", pady=5)
        ttk.Label(fila, text=etiqueta, width=21, anchor="w", style="Card.TLabel").pack(side="left")
        variable = tk.StringVar(value=valor)
        self.variables[clave] = variable
        ttk.Entry(fila, textvariable=variable, width=ancho).pack(side="left", fill="x", expand=True)
        if explorador:
            ttk.Button(fila, text="Examinar", command=explorador).pack(side="left", padx=(8, 0))
        return variable

    def _elegir_fotos(self):
        rutas = filedialog.askopenfilenames(
            title="Selecciona fotos de hojas",
            filetypes=[
                ("Imagenes", "*.png *.jpg *.jpeg *.bmp *.webp"),
                ("Todos", "*.*")
            ]
        )
        if rutas:
            self.fotos_seleccionadas = list(rutas)
            self.variables["fotos"].set(f"{len(rutas)} foto(s) seleccionada(s)")
            self._log(f"Seleccionadas {len(rutas)} foto(s)")

    def _elegir_carpeta_trabajo(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.variables["carpeta_trabajo"].set(ruta)

    def _log(self, mensaje):
        self.log_text.insert("end", f"[{self._obtener_hora()}] {mensaje}\n")
        self.log_text.see("end")
        self.update_idletasks()

    def _obtener_hora(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def _limpiar_vista(self, eje, canvas, mensaje):
        eje.clear()
        eje.text(0.5, 0.5, mensaje, ha="center", va="center", color="#7b8a8e", transform=eje.transAxes)
        eje.set_axis_off()
        canvas.draw_idle()

    def _limpiar_sesion(self):
        """Limpia la sesión actual para iniciar con nuevas muestras sin borrar modelos anteriores."""
        # Limpiar fotos seleccionadas
        self.fotos_seleccionadas = []
        self.variables["fotos"].set("")
        
        # Limpiar log
        self.log_text.delete(1.0, "end")
        self._log("Sesión reiniciada. Listo para nuevas muestras.")
        
        # Limpiar vista previa
        eje, canvas = self.vistas["generador"]
        self._limpiar_vista(eje, canvas, "Vista previa de resultados")
        
        # Reiniciar estado
        self.estado.set("Sesión limpiada. Selecciona nuevas fotos.")
        
        # Confirmación visual
        messagebox.showinfo("Sesión Reiniciada", "La sesión ha sido limpiada. Los modelos anteriores se conservan.\n\nSelecciona nuevas fotos para comenzar una nueva generación.")

    def _dibujar_puntos(self, puntos, titulo):
        self.eje.clear()
        cerrados = list(puntos) + [puntos[0]]
        self.eje.fill([p[0] for p in cerrados], [p[1] for p in cerrados], color="#68b6a9", alpha=0.55)
        self.eje.plot([p[0] for p in cerrados], [p[1] for p in cerrados], color="#147d74", linewidth=1.2)
        self.eje.set_title(titulo)
        self.eje.set_aspect("equal")
        self.eje.set_axis_off()
        self.canvas.draw_idle()

    def _ejecutar(self, descripcion, funcion):
        self.estado.set(descripcion)
        self.progreso.start(10)

        def trabajo():
            try:
                resultado = funcion()
                self.after(0, lambda: self._terminar_trabajo(descripcion, resultado))
            except Exception as error:
                self.after(0, lambda e=error: self._fallar_trabajo(str(e)))

        threading.Thread(target=trabajo, daemon=True).start()

    def _terminar_trabajo(self, descripcion, resultado):
        self.progreso.stop()
        self.estado.set(descripcion + " terminado")
        if resultado:
            self._log(resultado)

    def _fallar_trabajo(self, error):
        self.progreso.stop()
        self.estado.set("Se produjo un error")
        self._log(f"ERROR: {error}")
        messagebox.showerror("No se pudo completar", error)

    def _ejecutar_pipeline(self):
        if not self.fotos_seleccionadas:
            messagebox.showwarning("Faltan fotos", "Selecciona al menos una foto de hoja.")
            return
        
        especie = self.variables["especie"].get().strip()
        if not especie:
            messagebox.showwarning("Falta especie", "Escribe el nombre de la especie.")
            return
        
        carpeta_trabajo = self.variables["carpeta_trabajo"].get().strip()
        if not carpeta_trabajo:
            messagebox.showwarning("Falta carpeta", "Selecciona la carpeta de trabajo.")
            return
        
        try:
            cantidad_hojas = int(self.variables["cantidad_hojas"].get())
            intensidad = float(self.variables["intensidad"].get())
            extrusion = float(self.variables["extrusion"].get())
            tolerancia = float(self.variables["tolerancia"].get())
            curvatura = float(self.variables["curvatura"].get())
            
            if cantidad_hojas < 1 or intensidad < 0 or extrusion < 0 or tolerancia < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Datos invalidos", "Los parametros numericos deben ser validos.")
            return

        def pipeline_completo():
            self._log("Iniciando pipeline completo...")
            self._log(f"Especie: {especie}")
            self._log(f"Fotos: {len(self.fotos_seleccionadas)}")
            
            # Paso 1: Extraer siluetas (con soporte 3D si hay múltiples vistas)
            self._log("Paso 1/4: Extrayendo siluetas...")
            carpeta_especie = Path(carpeta_trabajo) / especie
            carpeta_especie.mkdir(parents=True, exist_ok=True)
            
            siluetas_generadas = []
            tiene_3d = len(self.fotos_seleccionadas) > 1
            
            if tiene_3d:
                self._log(f"  Detectadas {len(self.fotos_seleccionadas)} vistas - intentando reconstrucción 3D...")
            
            for i, foto in enumerate(self.fotos_seleccionadas):
                try:
                    # Si hay múltiples vistas, procesar todas juntas para 3D
                    if tiene_3d and i == 0:
                        try:
                            imagenes = extractor_siluetas.cargar_imagenes(self.fotos_seleccionadas)
                            imagenes_alineadas = extractor_siluetas.alinear_vistas(imagenes)
                            
                            # Usar primera imagen para máscara
                            gris = imagenes[0]
                            alto, ancho = gris.shape
                            mascara = extractor_siluetas.limpiar_mascara(extractor_siluetas.crear_mascara(gris))
                            
                            # Estimar profundidad
                            profundidad = extractor_siluetas.estimar_profundidad_sombreado(imagenes_alineadas, mascara)
                            
                            # Construir malla 3D
                            vertices, caras = extractor_siluetas.construir_malla_3d(profundidad, mascara)
                            
                            # Guardar malla 3D
                            nombre = Path(foto).stem
                            ruta_obj, ruta_json = extractor_siluetas.guardar_reconstruccion_3d(foto, vertices, caras, profundidad)
                            self._log(f"  - Malla 3D generada: {Path(ruta_obj).name}")
                            
                            # También generar silueta 2D para compatibilidad
                            contornos, jerarquia = extractor_siluetas.encontrar_contornos(mascara)
                            indice = extractor_siluetas.encontrar_contorno_principal(contornos, jerarquia)
                            
                            if indice is not None:
                                indices = extractor_siluetas.obtener_descendientes(indice, contornos, jerarquia)
                                coordenadas = extractor_siluetas.extraer_coordenadas(contornos, indices, jerarquia, ancho, alto)
                                
                                codigo = extractor_siluetas.generar_codigo_turtle(coordenadas, Path(foto).name)
                                archivo_py = carpeta_especie / (nombre + "_silueta.py")
                                archivo_txt = carpeta_especie / (nombre + "_coordenadas.txt")
                                
                                archivo_py.write_text(codigo, encoding="utf-8")
                                with archivo_txt.open("w", encoding="utf-8") as archivo:
                                    for numero, datos in enumerate(coordenadas, 1):
                                        archivo.write(f"CONTORNO {numero}\nTIPO: {datos['tipo']}\nPROFUNDIDAD: {datos['profundidad']}\nPUNTOS: {len(datos['puntos'])}\n\n")
                                        archivo.write("".join(f"{x}, {y}\n" for x, y in datos["puntos"]) + "\n")
                                
                                siluetas_generadas.append(archivo_py)
                                
                                # Mostrar primera silueta en vista previa
                                exteriores = [dato["puntos"] for dato in coordenadas if dato["tipo"] == "EXTERIOR"]
                                if exteriores:
                                    puntos_exterior = exteriores[0]
                                    # Verificar que los puntos sean válidos
                                    puntos_validos = [(x, y) for x, y in puntos_exterior if not (x != x or y != y)]  # Check for NaN
                                    if puntos_validos:
                                        self.after(0, lambda p=puntos_validos: self._dibujar_puntos(p, "Silueta extraida + 3D"))
                            
                            break  # Solo procesar el lote una vez
                        
                        except Exception as e3d:
                            self._log(f"  - Reconstrucción 3D falló: {str(e3d)}, usando extracción 2D...")
                            tiene_3d = False  # Fallback a 2D
                    
                    if not tiene_3d:
                        # Extracción 2D normal
                        gris = extractor_siluetas.cargar_imagen(foto)
                        alto, ancho = gris.shape
                        mascara = extractor_siluetas.limpiar_mascara(extractor_siluetas.crear_mascara(gris))
                        contornos, jerarquia = extractor_siluetas.encontrar_contornos(mascara)
                        indice = extractor_siluetas.encontrar_contorno_principal(contornos, jerarquia)
                        
                        if indice is None:
                            self._log(f"  - Foto {i+1}: No se detecto silueta principal")
                            continue
                        
                        indices = extractor_siluetas.obtener_descendientes(indice, contornos, jerarquia)
                        coordenadas = extractor_siluetas.extraer_coordenadas(contornos, indices, jerarquia, ancho, alto)
                        
                        nombre = Path(foto).stem
                        codigo = extractor_siluetas.generar_codigo_turtle(coordenadas, Path(foto).name)
                        archivo_py = carpeta_especie / (nombre + "_silueta.py")
                        archivo_txt = carpeta_especie / (nombre + "_coordenadas.txt")
                        
                        archivo_py.write_text(codigo, encoding="utf-8")
                        with archivo_txt.open("w", encoding="utf-8") as archivo:
                            for numero, datos in enumerate(coordenadas, 1):
                                archivo.write(f"CONTORNO {numero}\nTIPO: {datos['tipo']}\nPROFUNDIDAD: {datos['profundidad']}\nPUNTOS: {len(datos['puntos'])}\n\n")
                                archivo.write("".join(f"{x}, {y}\n" for x, y in datos["puntos"]) + "\n")
                        
                        siluetas_generadas.append(archivo_py)
                        self._log(f"  - Foto {i+1}: Silueta extraida correctamente")
                        
                        # Mostrar primera silueta en vista previa
                        if i == 0:
                            exteriores = [dato["puntos"] for dato in coordenadas if dato["tipo"] == "EXTERIOR"]
                            if exteriores:
                                puntos_exterior = exteriores[0]
                                # Verificar que los puntos sean válidos
                                puntos_validos = [(x, y) for x, y in puntos_exterior if not (x != x or y != y)]  # Check for NaN
                                if puntos_validos:
                                    self.after(0, lambda p=puntos_validos: self._dibujar_puntos(p, "Silueta extraida"))
                
                except Exception as e:
                    self._log(f"  - Foto {i+1}: Error - {str(e)}")
            
            if not siluetas_generadas:
                raise ValueError("No se pudo extraer ninguna silueta valida. Revisa las fotos (fondo claro, hoja oscura).")
            
            self._log(f"Siluetas extraidas: {len(siluetas_generadas)}/{len(self.fotos_seleccionadas)}")
            
            # Paso 2: Entrenar modelo con las imágenes importadas
            self._log("Paso 2/4: Entrenando modelo con las imágenes importadas...")
            self._log(f"  Creando modelo para especie: {especie}")
            self._log(f"  Muestras disponibles: {len(siluetas_generadas)}")
            
            if len(siluetas_generadas) < entrenar_todo.MINIMO_MUESTRAS:
                self._log(f"  ⚠ ADVERTENCIA: Solo {len(siluetas_generadas)} muestras (recomendado: {entrenar_todo.MINIMO_MUESTRAS}+)")
                self._log("  El modelo sera menos preciso pero se generara igualmente...")
            
            try:
                # Entrenar siempre con las imágenes importadas
                modelo_forma_especie.entrenar_especie(
                    especie, 
                    siluetas_generadas, 
                    n_por_lado=100, 
                    carpeta_modelos=str(RAIZ / "modelos")
                )
                self._log("  ✅ Modelo entrenado correctamente con las imágenes importadas")
            except Exception as e:
                self._log(f"  ❌ Error entrenando modelo: {str(e)}")
                raise ValueError(f"No se pudo entrenar el modelo con las imágenes importadas: {str(e)}")
            
            # Paso 3: Generar hojas con el modelo recién creado
            self._log("Paso 3/4: Generando hojas sinteticas con el modelo importado...")
            carpeta_modelos = str(RAIZ / "modelos")
            
            # Crear carpeta específica para esta sesión de generación
            carpeta_generadas = carpeta_especie / "generadas"
            carpeta_generadas.mkdir(parents=True, exist_ok=True)
            
            self._log(f"  Generando {cantidad_hojas} hoja(s) basadas en las imágenes importadas...")
            
            hojas_generadas = []
            for i in range(cantidad_hojas):
                try:
                    # Intentar generar con modelo estadístico
                    hoja = modelo_forma_especie.generar_hoja_de_especie(
                        especie, 
                        carpeta_modelos=carpeta_modelos, 
                        intensidad=intensidad, 
                        semilla=None
                    )
                    
                    # Validar que la hoja generada tenga puntos válidos
                    puntos_validos = [(x, y) for x, y in hoja["puntos"] if not (x != x or y != y)]
                    
                    if len(puntos_validos) < 10:
                        self._log(f"  - Hoja {i+1}: Modelo generó pocos puntos ({len(puntos_validos)}), usando siluetas extraídas...")
                        # Fallback: usar directamente las siluetas extraídas de las imágenes
                        if siluetas_generadas:
                            # Usar la primera silueta extraída como base
                            silueta_base = siluetas_generadas[0]
                            # Leer los puntos de la silueta extraída
                            with open(silueta_base, 'r') as f:
                                contenido = f.read()
                            import re
                            pares = re.findall(r"\(([-\d.]+),\s*([-\d.]+)\)", contenido)
                            if pares:
                                puntos_silueta = [(float(x), float(y)) for x, y in pares]
                                # Crear variación simple aplicando escala aleatoria
                                import random
                                escala_variacion = 0.9 + random.random() * 0.2  # 0.9-1.1
                                puntos_variados = [(x * escala_variacion, y * escala_variacion) for x, y in puntos_silueta]
                                
                                hoja = {
                                    "id": f"{especie}_extraida_{i}",
                                    "fuente": "silueta_extraida",
                                    "puntos": puntos_variados,
                                    "num_puntos": len(puntos_variados)
                                }
                                self._log(f"  - Hoja {i+1}: Generada desde silueta extraída (variación {escala_variacion:.2f}x)")
                            else:
                                raise ValueError("No se encontraron puntos en la silueta extraída")
                        else:
                            raise ValueError("No hay siluetas extraídas disponibles")
                    
                    # Guardar con nombre específico que incluya la especie
                    ruta = carpeta_generadas / f"{especie}_importada_{i + 1:03d}.json"
                    ruta.write_text(json.dumps(hoja, ensure_ascii=False, indent=2), encoding="utf-8")
                    hojas_generadas.append(ruta)
                    self._log(f"  - Hoja {i+1} generada: {ruta.name}")
                    
                    # Mostrar ultima hoja generada en vista previa
                    if i == cantidad_hojas - 1:
                        puntos_hoja = hoja["puntos"]
                        # Verificar que los puntos sean válidos
                        puntos_validos = [(x, y) for x, y in puntos_hoja if not (x != x or y != y)]  # Check for NaN
                        if puntos_validos:
                            self.after(0, lambda p=puntos_validos, s=especie: self._dibujar_puntos(p, f"{s} importada"))
                
                except Exception as e:
                    self._log(f"  - Hoja {i+1}: Error en modelo estadístico - {str(e)}, usando siluetas extraídas...")
                    try:
                        # Fallback: usar directamente las siluetas extraídas
                        if siluetas_generadas:
                            silueta_base = siluetas_generadas[0]
                            with open(silueta_base, 'r') as f:
                                contenido = f.read()
                            import re
                            pares = re.findall(r"\(([-\d.]+),\s*([-\d.]+)\)", contenido)
                            if pares:
                                puntos_silueta = [(float(x), float(y)) for x, y in pares]
                                import random
                                escala_variacion = 0.85 + random.random() * 0.3  # 0.85-1.15
                                puntos_variados = [(x * escala_variacion, y * escala_variacion) for x, y in puntos_silueta]
                                
                                hoja = {
                                    "id": f"{especie}_extraida_{i}",
                                    "fuente": "silueta_extraida_fallback",
                                    "puntos": puntos_variados,
                                    "num_puntos": len(puntos_variados)
                                }
                                
                                ruta = carpeta_generadas / f"{especie}_extraida_{i + 1:03d}.json"
                                ruta.write_text(json.dumps(hoja, ensure_ascii=False, indent=2), encoding="utf-8")
                                hojas_generadas.append(ruta)
                                self._log(f"  - Hoja {i+1} generada (silueta): {ruta.name}")
                                
                                # Mostrar ultima hoja generada en vista previa
                                if i == cantidad_hojas - 1:
                                    puntos_validos = [(x, y) for x, y in puntos_variados if not (x != x or y != y)]
                                    if puntos_validos:
                                        self.after(0, lambda p=puntos_validos, s=especie: self._dibujar_puntos(p, f"{s} extraída"))
                            else:
                                raise ValueError("No se encontraron puntos en la silueta extraída")
                        else:
                            raise ValueError("No hay siluetas extraídas disponibles")
                    
                    except Exception as e2:
                        self._log(f"  - Hoja {i+1}: Error también en siluetas extraídas - {str(e2)}")
            
            if not hojas_generadas:
                raise ValueError("No se pudo generar ninguna hoja. Verifica que el modelo existe.")
            
            self._log(f"Hojas generadas: {len(hojas_generadas)}")
            
            # Paso 4: Convertir a MAXScript con realismo mejorado
            self._log("Paso 4/4: Convirtiendo a MAXScript con realismo mejorado...")
            
            # Crear carpeta específica para MAXScripts de esta especie
            carpeta_maxscript = carpeta_especie / "maxscript"
            carpeta_maxscript.mkdir(parents=True, exist_ok=True)
            
            self._log(f"  Guardando MAXScripts en: {carpeta_maxscript}")
            
            maxscripts_generados = []
            for i, hoja_json in enumerate(hojas_generadas):
                try:
                    # Verificar si hay malla 3D disponible de las imágenes importadas
                    archivo_3d = carpeta_especie / f"{Path(hoja_json).stem.replace('_importada', '')}_3d.json"
                    entrada_malla = str(archivo_3d) if archivo_3d.exists() else str(hoja_json)
                    
                    resultado = convertir_a_maxscript_mejorado.convertir_mejorado(
                        entrada_malla,
                        str(carpeta_maxscript / f"{especie}_importada_{i + 1:03d}.ms"),
                        altura_extrusion=extrusion,
                        escala=1.0,
                        nombre_objeto=f"{especie}_importada_{i + 1}",
                        con_venacion=self.con_venacion.get(),
                        grosor_variable=self.grosor_variable.get(),
                        curvatura=curvatura,
                        detalle_superficie=self.detalle_superficie.get()
                    )
                    maxscripts_generados.append(resultado["archivo_salida"])
                    self._log(f"  - MAXScript {i+1} creado: {Path(resultado['archivo_salida']).name}")
                    self._log(f"    (venación: {resultado['venacion']}, grosor variable: {resultado['grosor_variable']})")
                
                except Exception as e:
                    self._log(f"  - MAXScript {i+1}: Error - {str(e)}")
                    # Diagnóstico: verificar el contenido del JSON
                    try:
                        with open(hoja_json, 'r') as f:
                            contenido = f.read()
                            self._log(f"  - Diagnóstico: primeros 200 caracteres del JSON: {contenido[:200]}")
                    except:
                        pass
                    
                    # Fallback al conversor simple
                    try:
                        resultado = convertir_a_maxscript.convertir(
                            str(hoja_json),
                            str(carpeta_maxscript / f"{especie}_simple_{i + 1:03d}.ms"),
                            tolerancia=tolerancia,
                            altura_extrusion=extrusion,
                            escala=1.0,
                            nombre_objeto=f"{especie}_simple_{i + 1}"
                        )
                        maxscripts_generados.append(resultado["archivo_salida"])
                        self._log(f"  - MAXScript simple {i+1} creado como fallback")
                    except Exception as e2:
                        self._log(f"  - Fallback también falló: {str(e2)}")
            
            if not maxscripts_generados:
                raise ValueError("No se pudo generar ningun MAXScript.")
            
            self._log(f"MAXScripts generados: {len(maxscripts_generados)}")
            
            # Resumen final
            self._log("=" * 50)
            self._log("PIPELINE COMPLETADO EXITOSAMENTE")
            self._log("=" * 50)
            self._log(f"📁 Estructura creada para especie: {especie}")
            self._log(f"   📂 Carpeta principal: {carpeta_especie}")
            self._log(f"   📂 Siluetas: {len(siluetas_generadas)} archivos *_silueta.py")
            self._log(f"   📂 Generadas: {len(hojas_generadas)} hojas sintéticas")
            self._log(f"   📂 MAXScript: {len(maxscripts_generados)} archivos .ms")
            self._log(f"   📂 Modelo: {especie}.json en modelos/")
            self._log("")
            self._log(f"🎯 Todas las hojas generadas están basadas EXCLUSIVAMENTE en las imágenes importadas")
            self._log(f"🎯 No se usaron modelos preexistentes de otras especies")
            
            return f"Pipeline completado para {especie}. Estructura completa creada en {carpeta_especie}"

        self._ejecutar("Ejecutando pipeline completo", pipeline_completo)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    app = InterfazAutomatica()
    app.mainloop()
