import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import manejoImagenes
import os
import cv2
import numpy as np

class ImageQuadrantSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Selector de Cuadrantes (4x4)")

        self.canvas = tk.Canvas(root, width=1000, height=400) 
        self.canvas.pack()

        self.image = None
        self.selected_quadrant_image = None
        self.original_pil_image = None
        self.current_sector = None
        self.greyscale_image = None

        btn_cargar = tk.Button(root, text="Cargar Imagen", command=self.cargar_imagen)
        btn_cargar.pack()

        btn_guardar = tk.Button(root, text="Guardar Sector", command=self.guardar_sector)
        btn_guardar.pack()

        self.canvas.bind("<Button-1>", self.detectar_cuadrante)

    def cargar_imagen(self):
        path = filedialog.askopenfilename(filetypes=[
            ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp"),
            ("Todos los archivos", "*.*")
        ])
        if path:
            # Cargar la imagen original
            img = Image.open(path).convert("RGB")
            img = img.resize((400, 400))
            self.original_pil_image = img
            self.image = ImageTk.PhotoImage(img)

            # Cargar también la imagen en escala de grises para manejoImagenes
            self.greyscale_image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if self.greyscale_image is not None:
                self.greyscale_image = cv2.resize(self.greyscale_image, (400, 400))
            else:
                print("Error al cargar la imagen en escala de grises")
                return

            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

            for i in range(1, 4):
                self.canvas.create_line(i * 100, 0, i * 100, 400, fill="red")
                self.canvas.create_line(0, i * 100, 400, i * 100, fill="red")

            self.canvas.create_text(420, 50, text="Cuadrante seleccionado:", anchor=tk.NW)
            self.canvas.create_rectangle(420, 80, 620, 280, outline="blue", width=2)

            self.canvas.create_text(640, 50, text="Área de interpolación:", anchor=tk.NW)
            self.canvas.create_rectangle(640, 80, 840, 280, outline="green", width=2)

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

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

        for i in range(1, 4):
            self.canvas.create_line(i * 100, 0, i * 100, 400, fill="red")
            self.canvas.create_line(0, i * 100, 400, i * 100, fill="red")

        self.canvas.create_text(420, 50, text="Cuadrante seleccionado:", anchor=tk.NW)
        self.canvas.create_rectangle(420, 80, 620, 280, outline="blue", width=2)

        quadrant_x = 420 + (200 - 100) // 2  
        quadrant_y = 80 + (200 - 100) // 2   

        self.canvas.create_image(quadrant_x, quadrant_y, anchor=tk.NW, image=self.selected_quadrant_image)

        self.canvas.create_text(640, 50, text="Área de interpolación:", anchor=tk.NW)
        self.canvas.create_rectangle(640, 80, 840, 280, outline="green", width=2)

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
        
        
        output_path = os.path.join(os.path.dirname(__file__), f'sector.txt') #ACA SE GUARDA EL SECTOR
        manejoImagenes.save_sectors_to_file(selected_sector, output_path, ' ', 1)
        
        print(f"Sector {self.current_sector} guardado en {output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageQuadrantSelector(root)
    root.mainloop()
