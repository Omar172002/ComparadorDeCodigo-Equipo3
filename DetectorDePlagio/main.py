import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import sys
from io import StringIO
import datetime
from hash import subtree_hashes
from Ast import get_ast_root
from Jaccard import jaccard
from normalize import normalize_variables

class PlagiarismDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Detector de Plagio - Análisis Avanzado")
        self.root.geometry("1300x850")
        self.root.configure(bg='#1e3a5f')
        
        # Estilo con botones negros
        self.colors = {
            'primary': '#1e3a5f',
            'secondary': '#2d5aa0', 
            'accent': '#4a90e2',
            'accent_light': '#6ba8ff',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50',
            'text_light': '#ffffff',
            'text_dark': '#2c3e50',
            'file_area': '#34495e',
            'button_normal': '#000000',      # Negro
            'button_hover': '#333333',       # Negro más claro para hover
            'button_press': '#555555',       # Negro más claro aún para presionar
            'button_text': '#ffffff'         # Texto blanco
        }
        
        # Configurar estilo
        self.setup_styles()
        
        # Variables para almacenar archivos y configuración
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.similarity_threshold_high = tk.DoubleVar(value=0.9)
        self.similarity_threshold_medium = tk.DoubleVar(value=0.7)
        self.similarity_threshold_low = tk.DoubleVar(value=0.5)
        self.auto_save = tk.BooleanVar(value=True)
        self.current_similarity = 0.0
        
        self.setup_ui()
    
    def setup_styles(self):
        style = ttk.Style()
        style.configure('Blue.TFrame', background=self.colors['primary'])
        style.configure('Blue.TLabelframe', background=self.colors['secondary'], foreground=self.colors['text_light'])
        style.configure('Blue.TLabelframe.Label', background=self.colors['secondary'], foreground=self.colors['text_light'])
        style.configure('Blue.TButton', background=self.colors['button_normal'], foreground=self.colors['button_text'])
    
    def setup_ui(self):
        # Frame principal con 3 paneles
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo: Configuración y archivos
        left_frame = ttk.Frame(main_paned, style='Blue.TFrame')
        main_paned.add(left_frame, weight=1)
        
        # Panel central: Resultados detallados
        center_frame = ttk.Frame(main_paned, style='Blue.TFrame')
        main_paned.add(center_frame, weight=2)
        
        # Panel derecho: Resultado final
        right_frame = ttk.Frame(main_paned, style='Blue.TFrame')
        main_paned.add(right_frame, weight=1)
        
        self.setup_left_panel(left_frame)
        self.setup_center_panel(center_frame)
        self.setup_right_panel(right_frame)
    
    def setup_left_panel(self, parent):
        # Título
        title_label = tk.Label(parent, text="⚙️ CONFIGURACIÓN", 
                              font=("Arial", 16, "bold"),
                              bg=self.colors['secondary'],
                              fg=self.colors['text_light'],
                              pady=10)
        title_label.pack(fill=tk.X, pady=(0, 15))
        
        # Frame para selección de archivos con diseño mejorado
        files_container = self.create_styled_frame(parent, "📁 ARCHIVOS A ANALIZAR")
        files_container.pack(fill=tk.X, pady=10, padx=5)
        
        # Archivo 1 con diseño mejorado
        file1_frame = tk.Frame(files_container, bg=self.colors['light'])
        file1_frame.pack(fill=tk.X, pady=8, padx=10)
        
        tk.Label(file1_frame, text="📄 Archivo 1:", font=("Arial", 11, "bold"),
                bg=self.colors['light'], fg=self.colors['text_dark']).grid(row=0, column=0, sticky="w", padx=5, pady=8)
        
        file1_entry = tk.Entry(file1_frame, textvariable=self.file1_path, width=30,
                              bg='white', fg=self.colors['text_dark'],
                              font=("Arial", 10),
                              relief=tk.SUNKEN, bd=2)
        file1_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        file1_btn = self.create_styled_button(file1_frame, "🔍 Examinar", 
                                            lambda: self.browse_file(self.file1_path))
        file1_btn.grid(row=0, column=2, padx=5, pady=8)
        
        file1_frame.grid_columnconfigure(1, weight=1)
        
        # Archivo 2 con diseño mejorado
        file2_frame = tk.Frame(files_container, bg=self.colors['light'])
        file2_frame.pack(fill=tk.X, pady=8, padx=10)
        
        tk.Label(file2_frame, text="📄 Archivo 2:", font=("Arial", 11, "bold"),
                bg=self.colors['light'], fg=self.colors['text_dark']).grid(row=0, column=0, sticky="w", padx=5, pady=8)
        
        file2_entry = tk.Entry(file2_frame, textvariable=self.file2_path, width=30,
                              bg='white', fg=self.colors['text_dark'],
                              font=("Arial", 10),
                              relief=tk.SUNKEN, bd=2)
        file2_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        file2_btn = self.create_styled_button(file2_frame, "🔍 Examinar", 
                                            lambda: self.browse_file(self.file2_path))
        file2_btn.grid(row=0, column=2, padx=5, pady=8)
        
        file2_frame.grid_columnconfigure(1, weight=1)
        
        # Barra de progreso
        progress_frame = tk.Frame(parent, bg=self.colors['primary'])
        progress_frame.pack(fill=tk.X, pady=15)
        
        progress_label = tk.Label(progress_frame, text="📊 PROGRESO DEL ANÁLISIS", 
                                 font=("Arial", 12, "bold"),
                                 bg=self.colors['primary'],
                                 fg=self.colors['accent_light'])
        progress_label.pack()
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate', 
                                       style='Blue.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, pady=10, padx=20)
        
        # Botones de acción con diseño mejorado
        buttons_container = self.create_styled_frame(parent, "🎮 ACCIONES PRINCIPALES")
        buttons_container.pack(fill=tk.X, pady=15, padx=5)
        
        # Botones principales más grandes y visibles
        self.create_main_button(buttons_container, "🔍 ANALIZAR SIMILITUD", 
                              self.analyze_similarity).pack(fill=tk.X, padx=20, pady=8)
        
        self.create_main_button(buttons_container, "🔄 LIMPIAR TODO", 
                              self.clear_all).pack(fill=tk.X, padx=20, pady=8)
        
        self.create_main_button(buttons_container, "💾 GUARDAR RESULTADOS", 
                              self.save_results).pack(fill=tk.X, padx=20, pady=8)
        
        # Configuración de umbrales
        config_frame = self.create_styled_frame(parent, "🎯 UMBRALES DE SIMILITUD")
        config_frame.pack(fill=tk.X, pady=15, padx=5)
        
        self.create_threshold_slider(config_frame, "🔴 Alta similitud (>=):", 
                                   self.similarity_threshold_high, 0)
        self.create_threshold_slider(config_frame, "🟡 Media similitud (>=):", 
                                   self.similarity_threshold_medium, 1)
        self.create_threshold_slider(config_frame, "🟢 Baja similitud (>=):", 
                                   self.similarity_threshold_low, 2)
        
        # Opciones
        options_frame = tk.Frame(config_frame, bg=self.colors['light'])
        options_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=15)
        
        tk.Checkbutton(options_frame, text="💾 Guardar resultados automáticamente", 
                      variable=self.auto_save, font=("Arial", 10, "bold"),
                      bg=self.colors['light'], fg=self.colors['text_dark'],
                      selectcolor=self.colors['accent'],
                      activebackground=self.colors['light']).pack(anchor="w", padx=10, pady=8)
    
    def create_main_button(self, parent, text, command):
        """Crea botones principales grandes y visibles en negro"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=self.colors['button_normal'], 
                       fg=self.colors['button_text'],
                       font=("Arial", 12, "bold"),
                       relief=tk.RAISED, bd=3,
                       padx=20, pady=15,
                       cursor="hand2",
                       activebackground=self.colors['button_press'],
                       activeforeground=self.colors['button_text'])
        
        # Efecto hover
        def on_enter(e):
            btn['bg'] = self.colors['button_hover']
        def on_leave(e):
            btn['bg'] = self.colors['button_normal']
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def create_styled_button(self, parent, text, command):
        """Crea botones estilo negro"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=self.colors['button_normal'], 
                       fg=self.colors['button_text'],
                       font=("Arial", 10, "bold"),
                       relief=tk.RAISED, bd=2,
                       padx=12, pady=6,
                       cursor="hand2",
                       activebackground=self.colors['button_press'],
                       activeforeground=self.colors['button_text'])
        
        # Efecto hover para botones pequeños
        def on_enter(e):
            btn['bg'] = self.colors['button_hover']
        def on_leave(e):
            btn['bg'] = self.colors['button_normal']
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def create_styled_frame(self, parent, title):
        frame = tk.LabelFrame(parent, text=title, font=("Arial", 12, "bold"),
                             bg=self.colors['light'], fg=self.colors['text_dark'],
                             relief=tk.RAISED, bd=3, padx=15, pady=15)
        return frame
    
    def create_threshold_slider(self, parent, label_text, variable, row):
        label = tk.Label(parent, text=label_text, font=("Arial", 10, "bold"),
                        bg=self.colors['light'], fg=self.colors['text_dark'])
        label.grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        value_label = tk.Label(parent, textvariable=variable, 
                              font=("Arial", 10, "bold"),
                              bg=self.colors['light'], fg=self.colors['accent'])
        value_label.grid(row=row, column=1, padx=10, pady=8)
        
        scale = tk.Scale(parent, from_=0.1, to=1.0, resolution=0.05, 
                        orient=tk.HORIZONTAL, variable=variable,
                        length=180, showvalue=False,
                        bg=self.colors['light'], fg=self.colors['text_dark'],
                        highlightbackground=self.colors['accent'],
                        troughcolor=self.colors['accent_light'],
                        sliderrelief=tk.RAISED,
                        command=lambda v: None)
        scale.grid(row=row, column=2, padx=10, pady=8, sticky="ew")
        
        parent.grid_columnconfigure(2, weight=1)
        return scale
    
    def browse_file(self, text_variable):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Archivos de texto", "*.txt"), ("Archivos C++", "*.cpp"), 
                      ("Archivos C", "*.c"), ("Todos los archivos", "*.*")]
        )
        if filename:
            text_variable.set(filename)
    
    def setup_center_panel(self, parent):
        # Título
        title_label = tk.Label(parent, text="📊 RESULTADOS DETALLADOS", 
                              font=("Arial", 16, "bold"),
                              bg=self.colors['secondary'],
                              fg=self.colors['text_light'],
                              pady=10)
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Área de resultados detallados
        results_frame = tk.Frame(parent, bg=self.colors['primary'])
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD,
                                                     bg='#2c3e50', fg='#ecf0f1',
                                                     insertbackground='white',
                                                     selectbackground=self.colors['accent'],
                                                     font=("Consolas", 10),
                                                     padx=15, pady=15)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_right_panel(self, parent):
        # Título
        title_label = tk.Label(parent, text="🎯 RESULTADO FINAL", 
                              font=("Arial", 16, "bold"),
                              bg=self.colors['secondary'],
                              fg=self.colors['text_light'],
                              pady=10)
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para resultado final
        result_frame = tk.Frame(parent, bg=self.colors['primary'])
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Contenedor para el círculo de similitud
        canvas_frame = tk.Frame(result_frame, bg=self.colors['primary'])
        canvas_frame.pack(pady=20)
        
        self.similarity_canvas = tk.Canvas(canvas_frame, width=280, height=280, 
                                         bg=self.colors['primary'], highlightthickness=0)
        self.similarity_canvas.pack()
        
        # Etiqueta de porcentaje
        self.similarity_label = tk.Label(canvas_frame, text="0.0%", 
                                       font=("Arial", 28, "bold"),
                                       bg=self.colors['primary'],
                                       fg=self.colors['text_light'])
        self.similarity_label.place(in_=self.similarity_canvas, relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Etiqueta de estado
        self.result_label = tk.Label(result_frame, text="Esperando análisis...", 
                                   font=("Arial", 14, "bold"),
                                   bg=self.colors['primary'],
                                   fg=self.colors['text_light'])
        self.result_label.pack(pady=10)
        
        # Frame para estadísticas
        stats_frame = self.create_styled_frame(result_frame, "📈 ESTADÍSTICAS")
        stats_frame.pack(fill=tk.X, pady=10, padx=10)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, wrap=tk.WORD, height=8,
                                                   bg='#2c3e50', fg='#ecf0f1',
                                                   font=("Arial", 10),
                                                   padx=10, pady=10)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para recomendación
        self.recommendation_frame = self.create_styled_frame(result_frame, "💡 RECOMENDACIÓN")
        self.recommendation_frame.pack(fill=tk.X, pady=10, padx=10)
        
        self.recommendation_text = scrolledtext.ScrolledText(self.recommendation_frame, wrap=tk.WORD, height=6,
                                                           bg='#2c3e50', fg='#ecf0f1',
                                                           font=("Arial", 10),
                                                           padx=10, pady=10)
        self.recommendation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def clear_all(self):
        self.file1_path.set("")
        self.file2_path.set("")
        self.results_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        self.recommendation_text.delete(1.0, tk.END)
        self.update_similarity_display(0.0, "Esperando análisis...")
    
    def save_results(self):
        if not self.results_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Advertencia", "No hay resultados para guardar")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Guardar resultados como",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Éxito", f"✅ Resultados guardados en:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ No se pudieron guardar los resultados:\n{str(e)}")
    
    def update_similarity_display(self, similarity, status):
        self.current_similarity = similarity
        self.similarity_label.config(text=f"{similarity:.1%}")
        self.result_label.config(text=status)
        
        # Actualizar círculo de similitud
        self.similarity_canvas.delete("all")
        
        # Determinar color basado en similitud
        if similarity >= self.similarity_threshold_high.get():
            color = self.colors['danger']  # Rojo para alta similitud
        elif similarity >= self.similarity_threshold_medium.get():
            color = self.colors['warning']  # Amarillo para media similitud
        else:
            color = self.colors['success']  # Verde para baja similitud
        
        # Dibujar círculo de progreso
        x, y, r = 140, 140, 120
        start_angle = 90
        extent = -360 * similarity
        
        # Círculo de fondo
        self.similarity_canvas.create_arc(x-r, y-r, x+r, y+r, 
                                        start=0, extent=360,
                                        outline=self.colors['dark'], 
                                        width=20, style=tk.ARC)
        
        # Círculo de progreso
        self.similarity_canvas.create_arc(x-r, y-r, x+r, y+r, 
                                        start=start_angle, extent=extent,
                                        outline=color, width=20, style=tk.ARC)
        
        # Actualizar estadísticas
        self.update_stats_display(similarity)
        
        # Actualizar recomendación
        self.update_recommendation(similarity)
    
    def update_stats_display(self, similarity):
        self.stats_text.delete(1.0, tk.END)
        
        high_thresh = self.similarity_threshold_high.get()
        med_thresh = self.similarity_threshold_medium.get()
        low_thresh = self.similarity_threshold_low.get()
        
        stats_info = f"""📊 ESTADÍSTICAS DEL ANÁLISIS

🎯 Similitud calculada: {similarity:.4f}
📈 Porcentaje: {similarity:.1%}

⚙️ UMBRALES CONFIGURADOS:
  🔴 Alta similitud: ≥ {high_thresh:.0%}
  🟡 Media similitud: ≥ {med_thresh:.0%}
  🟢 Baja similitud: ≥ {low_thresh:.0%}

📋 INTERPRETACIÓN:
"""
        
        if similarity >= high_thresh:
            stats_info += "  • 🚩 NIVEL: ALTO - Probable plagio"
        elif similarity >= med_thresh:
            stats_info += "  • ⚠️ NIVEL: MEDIO - Revisar manualmente"
        elif similarity >= low_thresh:
            stats_info += "  • 📝 NIVEL: BAJO - Posible coincidencia"
        else:
            stats_info += "  • ✅ NIVEL: MUY BAJO - Códigos diferentes"
        
        self.stats_text.insert(1.0, stats_info)
    
    def update_recommendation(self, similarity):
        self.recommendation_text.delete(1.0, tk.END)
        
        high_thresh = self.similarity_threshold_high.get()
        med_thresh = self.similarity_threshold_medium.get()
        
        if similarity >= high_thresh:
            recommendation = """🚨 ACCIONES RECOMENDADAS:

• 🔍 Revisar detenidamente ambos códigos
• 📝 Documentar todas las evidencias encontradas
• ⚖️ Considerar como caso de plagio potencial
• 👥 Consultar con supervisores o comité académico
• 📋 Realizar análisis manual complementario"""
        
        elif similarity >= med_thresh:
            recommendation = """⚠️ ACCIONES RECOMENDADAS:

• 🔎 Realizar análisis manual detallado
• 📊 Verificar similitudes específicas encontradas
• 🧮 Considerar el contexto del desarrollo
• 📝 Documentar hallazgos específicos
• 💬 Entrevistar a los desarrolladores"""
        
        else:
            recommendation = """✅ SITUACIÓN ACTUAL:

• 🎉 Similitud dentro de rangos normales
• 📚 Probablemente códigos desarrollados independientemente
• 🔒 No se detectan indicios de plagio
• 📈 Continuar con revisiones rutinarias"""
        
        self.recommendation_text.insert(1.0, recommendation)
    
    def log_message(self, message):
        """Agrega mensaje al área de resultados"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update()
    
    def capture_ast_output(self, root, code_bytes):
        """Captura la salida del AST como string - Versión mejorada"""
        try:
            # Redirigir stdout para capturar la salida del AST
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            # Importar aquí para evitar problemas de importación circular
            from Ast import print_tree_with_lexemes
            print_tree_with_lexemes(root, code_bytes)
            
            sys.stdout = old_stdout
            return captured_output.getvalue()
        except Exception as e:
            return f"Error al generar AST: {str(e)}\n"
    
    def analyze_similarity(self):
        file1 = self.file1_path.get()
        file2 = self.file2_path.get()
        
        # Validaciones
        if not file1 or not file2:
            messagebox.showerror("Error", "❌ Por favor selecciona ambos archivos")
            return
        
        if not os.path.exists(file1):
            messagebox.showerror("Error", f"❌ El archivo no existe:\n{file1}")
            return
        
        if not os.path.exists(file2):
            messagebox.showerror("Error", f"❌ El archivo no existe:\n{file2}")
            return
        
        try:
            # Iniciar progreso
            self.progress.start()
            self.update_similarity_display(0.0, "🔄 Iniciando análisis...")
            
            # Limpiar resultados anteriores
            self.results_text.delete(1.0, tk.END)
            
            # Ejecutar análisis
            sim = self.run_analysis(file1, file2)
            
            # Actualizar display final
            if sim >= self.similarity_threshold_high.get():
                status = "🚩 ALTA SIMILITUD - Posible plagio"
            elif sim >= self.similarity_threshold_medium.get():
                status = "⚠️ SIMILITUD MEDIA - Revisar manual"
            else:
                status = "✅ BAJA SIMILITUD - Códigos diferentes"
            
            self.update_similarity_display(sim, status)
            
            # Guardar automáticamente si está configurado
            if self.auto_save.get():
                self.auto_save_results()
            
        except Exception as e:
            error_msg = f"Error durante el análisis: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", f"❌ Error en el análisis:\n{str(e)}")
            self.update_similarity_display(0.0, "❌ Error en el análisis")
        finally:
            self.progress.stop()
    
    def auto_save_results(self):
        """Guarda resultados automáticamente"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resultado_analisis_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.results_text.get(1.0, tk.END))
            
            self.log_message(f"💾 Resultados guardados automáticamente en: {filename}")
        except Exception as e:
            self.log_message(f"⚠️ No se pudieron guardar los resultados automáticamente: {str(e)}")
    
    def run_analysis(self, file1, file2):
        """Ejecuta el análisis de similitud y muestra resultados en la GUI"""
        
        # Encabezado del análisis
        self.log_message("=" * 70)
        self.log_message("🔍 ANÁLISIS DE SIMILITUD DE CÓDIGO")
        self.log_message(f"📅 Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_message(f"📄 Archivo 1: {file1}")
        self.log_message(f"📄 Archivo 2: {file2}")
        self.log_message("=" * 70)
        
        # === 1️⃣ Normalización ===
        self.update_similarity_display(0.1, "🔄 Normalizando código...")
        self.log_message("\n🧩 ETAPA 1: NORMALIZACIÓN DE CÓDIGO")
        self.log_message("-" * 50)
        
        try:
            with open(file1, "r", encoding="utf-8") as f1:
                code1 = f1.read()
            with open(file2, "r", encoding="utf-8") as f2:
                code2 = f2.read()

            code1_norm = normalize_variables(code1)
            code2_norm = normalize_variables(code2)

            self.log_message(f"\n✅ Normalización completada:")
            self.log_message(f"• {os.path.basename(file1)}: {len(code1.split())} palabras → {len(code1_norm.split())} después de normalizar")
            self.log_message(f"• {os.path.basename(file2)}: {len(code2.split())} palabras → {len(code2_norm.split())} después de normalizar")

        except Exception as e:
            self.log_message(f"❌ Error en normalización: {str(e)}")
            return 0.0

        # Guardar temporalmente el código normalizado
        self.update_similarity_display(0.3, "⚙️ Preparando análisis...")
        tmp1 = "tmp_norm1.cpp"
        tmp2 = "tmp_norm2.cpp"
        try:
            with open(tmp1, "w", encoding="utf-8") as f:
                f.write(code1_norm)
            with open(tmp2, "w", encoding="utf-8") as f:
                f.write(code2_norm)
        except Exception as e:
            self.log_message(f"❌ Error creando archivos temporales: {str(e)}")
            return 0.0

        # === 2️⃣ Generación de AST ===
        self.update_similarity_display(0.5, "🌳 Generando árboles sintácticos...")
        self.log_message("\n🌳 ETAPA 2: ÁRBOLES SINTÁCTICOS (AST)")
        self.log_message("-" * 50)
        
        try:
            root1, code_bytes1 = get_ast_root(tmp1)
            root2, code_bytes2 = get_ast_root(tmp2)

            self.log_message(f"\n✅ Árboles sintácticos generados:")
            self.log_message(f"• {os.path.basename(file1)}: AST construido correctamente")
            self.log_message(f"• {os.path.basename(file2)}: AST construido correctamente")

        except Exception as e:
            self.log_message(f"❌ Error generando AST: {str(e)}")
            # Limpiar archivos temporales
            try:
                os.remove(tmp1)
                os.remove(tmp2)
            except:
                pass
            return 0.0

        # === 3️⃣ Hashes de subárboles ===
        self.update_similarity_display(0.7, "🔑 Calculando hashes...")
        self.log_message("\n🔑 ETAPA 3: HASHES DE SUBÁRBOLES")
        self.log_message("-" * 50)
        
        try:
            hashes1 = subtree_hashes(root1)
            hashes2 = subtree_hashes(root2)

            self.log_message(f"\n📊 Estadísticas de hashes:")
            self.log_message(f"• {os.path.basename(file1)}: {len(hashes1)} subárboles únicos")
            self.log_message(f"• {os.path.basename(file2)}: {len(hashes2)} subárboles únicos")
            self.log_message(f"• Subárboles en común: {len(hashes1 & hashes2)}")

        except Exception as e:
            self.log_message(f"❌ Error calculando hashes: {str(e)}")
            # Limpiar archivos temporales
            try:
                os.remove(tmp1)
                os.remove(tmp2)
            except:
                pass
            return 0.0

        # === 4️⃣ Cálculo de similitud ===
        self.update_similarity_display(0.9, "📊 Calculando similitud final...")
        try:
            sim = jaccard(hashes1, hashes2)

            self.log_message("\n📊 ETAPA 4: COMPARACIÓN DE SIMILITUD")
            self.log_message("-" * 50)
            self.log_message(f"🎯 Similitud estructural (Jaccard): {sim:.4f}")

        except Exception as e:
            self.log_message(f"❌ Error calculando similitud: {str(e)}")
            sim = 0.0

        # Limpiar archivos temporales
        try:
            os.remove(tmp1)
            os.remove(tmp2)
        except:
            pass

        return sim

def main():
    try:
        root = tk.Tk()
        app = PlagiarismDetectorGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error iniciando la aplicación: {e}")

if __name__ == "__main__":
    main()