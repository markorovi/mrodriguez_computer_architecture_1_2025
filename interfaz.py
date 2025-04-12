import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageQuadrantSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Selector de Cuadrantes (4x4)")

        self.canvas = tk.Canvas(root, width=1000, height=400) 
        self.canvas.pack()

        self.image = None
        self.selected_quadrant_image = None
        self.original_pil_image = None

        btn_cargar = tk.Button(root, text="Cargar Imagen", command=self.cargar_imagen)
        btn_cargar.pack()

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
        if not self.original_pil_image:
            return

        col = event.x // 100
        row = event.y // 100
        sector = int(row * 4 + col + 1)

        if col > 3 or row > 3:
            return

        print(f"Cuadrante seleccionado: {sector} (fila {row+1}, columna {col+1})")

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

        # Área de interpolación vacía (marco verde)
        self.canvas.create_text(640, 50, text="Área de interpolación:", anchor=tk.NW)
        self.canvas.create_rectangle(640, 80, 840, 280, outline="green", width=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageQuadrantSelector(root)
    root.mainloop()

