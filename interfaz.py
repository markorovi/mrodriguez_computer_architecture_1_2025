import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import manejoImagenes
import os
import cv2
import numpy as np
import subprocess

class ImageQuadrantSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Selector de Cuadrantes (4x4)")

        self.canvas = tk.Canvas(root, width=900, height=400) 
        self.canvas.pack()

        self.image = None
        self.selected_quadrant_image = None
        self.original_pil_image = None
        self.current_sector = None
        self.greyscale_image = None
        self.interpolated_image = None

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        btn_cargar = tk.Button(btn_frame, text="Cargar Imagen", command=self.cargar_imagen)
        btn_cargar.pack(side=tk.LEFT, padx=5)

        btn_guardar = tk.Button(btn_frame, text="Guardar Sector", command=self.guardar_sector)
        btn_guardar.pack(side=tk.LEFT, padx=5)

        btn_interpolar = tk.Button(btn_frame, text="Ejecutar Interpolación", command=self.ejecutar_interpolacion)
        btn_interpolar.pack(side=tk.LEFT, padx=5)

        self.canvas.bind("<Button-1>", self.detectar_cuadrante)

    def cargar_imagen(self):
        path = filedialog.askopenfilename(filetypes=[
            ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp"),
            ("Todos los archivos", "*.*")
        ])
        if path:
            # Cargar imagen 
            img = Image.open(path).convert("RGB")
            img = img.resize((400, 400))
            self.original_pil_image = img
            self.image = ImageTk.PhotoImage(img)

            # Cargar en escala de grises para manejoImagenes
            self.greyscale_image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if self.greyscale_image is not None:
                self.greyscale_image = cv2.resize(self.greyscale_image, (400, 400))
            else:
                print("Error al cargar la imagen en escala de grises")
                return

            self.actualizar_canvas()

    def actualizar_canvas(self):
        self.canvas.delete("all")
        
        # cuadrícula
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        
        # Dibujar cuadrícula
        for i in range(1, 4):
            self.canvas.create_line(i * 100, 0, i * 100, 400, fill="red")
            self.canvas.create_line(0, i * 100, 400, i * 100, fill="red")

        # cuadrante seleccionado
        self.canvas.create_text(420, 50, text="Cuadrante seleccionado:", anchor=tk.NW)
        self.canvas.create_rectangle(420, 80, 620, 280, outline="blue", width=2)

        # Mostrar cuadrante 
        if self.selected_quadrant_image:
            quadrant_x = 420 + (200 - 100) // 2  
            quadrant_y = 80 + (200 - 100) // 2   
            self.canvas.create_image(quadrant_x, quadrant_y, anchor=tk.NW, image=self.selected_quadrant_image)

        # Área de interpolación
        self.canvas.create_text(640, 50, text="Área de interpolación:", anchor=tk.NW)
        self.canvas.create_rectangle(640, 80, 840, 280, outline="green", width=2)

        # Mostrar imagen interpolad
        if self.interpolated_image:
            interp_x = 640 + (200 - 200) // 2  # Centrar la imagen de 200x200
            interp_y = 80 + (200 - 200) // 2
            self.canvas.create_image(interp_x, interp_y, anchor=tk.NW, image=self.interpolated_image)

    def detectar_cuadrante(self, event):
        if self.original_pil_image is None:
            return

        col = event.x // 100
        row = event.y // 100
        self.current_sector = int(row * 4 + col + 1)

        if col > 3 or row > 3:
            return

        print(f"Cuadrante seleccionado: {self.current_sector} (fila {row+1}, columna {col+1})")

        x_start, x_end = col * 100, (col + 1) * 100
        y_start, y_end = row * 100, (row + 1) * 100

        quadrant = self.original_pil_image.crop((x_start, y_start, x_end, y_end))
        self.selected_quadrant_image = ImageTk.PhotoImage(quadrant)

        self.actualizar_canvas()

    def guardar_sector(self):
        if self.current_sector is None or self.greyscale_image is None:
            print("Error: No se ha seleccionado ningún sector o no se ha cargado imagen")
            return

        # Dividir la imagen en sectores
        sector_matrices = manejoImagenes.divide_image_into_sectors(self.greyscale_image)
        
        if sector_matrices is None:
            print("Error al dividir la imagen en sectores")
            return

        # Obtener solo el sector seleccionado
        selected_sector = {self.current_sector: sector_matrices[self.current_sector]}
        
        output_path = os.path.join(os.path.dirname(__file__), 'sector.txt')
        manejoImagenes.save_sectors_to_file(selected_sector, output_path, ' ', 1)
        
        print(f"Sector {self.current_sector} guardado en {output_path}")

    def ejecutar_interpolacion(self):
        if not os.path.exists('sector.txt'):
            print("Error: Primero debes guardar un sector")
            return

        try:
            # Ejecutar el programa de ensamblador
            result = subprocess.run(['./interpolacion'], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error al ejecutar interpolacion: {result.stderr}")
                return
            
            print("Interpolación ejecutada correctamente")
            
            # Leer y mostrar el resultado
            self.mostrar_resultado_interpolacion()
            
        except Exception as e:
            print(f"Error al ejecutar interpolación: {str(e)}")

    def mostrar_resultado_interpolacion(self):
        try:
            # Leer el archivo img generado por la interpolación
            with open('test.img', 'rb') as f:
                datos = np.frombuffer(f.read(), dtype=np.uint8)
            
            # Reformar a matriz 200x200
            imagen = datos.reshape((200, 200))
            
            # Convertir a imagen PIL
            img_pil = Image.fromarray(imagen, mode='L')
            
            # Convertir para mostrar en Tkinter
            self.interpolated_image = ImageTk.PhotoImage(img_pil)
            
            # Actualizar el canvas
            self.actualizar_canvas()
            
            # Guardar copia
            img_pil.save('imagen_procesada.png')
            print("Imagen interpolada guardada como 'imagen_procesada.png'")
            
        except Exception as e:
            print(f"Error al mostrar resultado: {str(e)}")
            print("Asegúrate de que:")
            print("1. El archivo 'test.bin' existe")
            print("2. Tiene exactamente 40,000 bytes (200x200)")
            print("3. Tienes permisos de lectura")

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    app = ImageQuadrantSelector(root)
    root.mainloop()
