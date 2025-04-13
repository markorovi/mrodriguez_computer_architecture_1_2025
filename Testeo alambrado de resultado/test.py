import cv2
import numpy as np
import os

def save_image_as_hex_txt(image, output_filename="imagen_hex.txt"):
    """
    Guarda una imagen (200x200) en un archivo .txt con valores hexadecimales.
    - Si la imagen no es 200x200, se redimensiona.
    - Soporta imágenes en escala de grises y RGB.
    """
    # Verificar dimensiones y redimensionar si es necesario
    if len(image.shape) == 2:  # Escala de grises (200x200)
        if image.shape != (200, 200):
            print(f"Redimensionando imagen a 200x200 (escala de grises)")
            image = cv2.resize(image, (200, 200))
    elif len(image.shape) == 3:  # RGB (200x200x3)
        if image.shape[:2] != (200, 200):
            print(f"Redimensionando imagen a 200x200 (RGB)")
            image = cv2.resize(image, (200, 200))
    else:
        raise ValueError("Formato de imagen no soportado (debe ser 200x200 o 200x200x3)")

    # Guardar los valores hexadecimales en un archivo .txt
    with open(output_filename, 'w') as file:
        if len(image.shape) == 2:  # Escala de grises (1 canal)
            for row in image:
                hex_row = ' '.join(f'{pixel:02X}' for pixel in row)
                file.write(hex_row + '\n')
        else:  # RGB (3 canales)
            for row in image:
                hex_row = ' '.join(f'{r:02X}{g:02X}{b:02X}' for r, g, b in row)
                file.write(hex_row + '\n')

    print(f"¡Archivo guardado como {output_filename}!")

# --- Ejemplo de uso ---
if __name__ == "__main__":
    # Cargar imagen (200x200 o se redimensiona)
    imagen_path = "imagen_procesada.png"  # Cambia por tu ruta
    imagen = cv2.imread(imagen_path, cv2.IMREAD_GRAYSCALE)  # Para escala de grises
    # imagen = cv2.imread(imagen_path, cv2.IMREAD_COLOR)  # Para RGB

    if imagen is None:
        print("Error: No se pudo cargar la imagen.")
    else:
        save_image_as_hex_txt(imagen, "matriz_hexadecimal.txt")
