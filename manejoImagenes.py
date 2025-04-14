import cv2
import numpy as np
import os

def divide_image_into_sectors(image, sector_size=100):
    height, width = image.shape

    if height != 400 or width != 400:
        print(f"Advertencia: Redimensionando la imagen de {height}x{width} a 400x400.")
        image = cv2.resize(image, (400, 400))
        height, width = image.shape

    # Diccionario para almacenar las matrices de cada sector
    sector_matrices = {}

    # Recorrer los sectores de la imagen (4x4 sectores en una imagen de 400x400)
    sector_num = 1
    for i in range(4):  # 4 filas de sectores
        for j in range(4):  # 4 columnas de sectores
            # oordenadas 
            y_start, y_end = i * sector_size, (i + 1) * sector_size
            x_start, x_end = j * sector_size, (j + 1) * sector_size

            # Extraer el sector
            sector = image[y_start:y_end, x_start:x_end]

            if sector.shape != (sector_size, sector_size):
                print(f"Error: El sector {sector_num} tiene dimensiones incorrectas {sector.shape}.")
                return None

            # Guardar la matriz del sector en el diccionario
            sector_matrices[sector_num] = sector
        
            sector_num += 1

    return sector_matrices

def save_sectors_to_file(sector_matrices, filename, separacion, num_sectores):
    with open(filename, 'w') as file:
        contador = 0
        for sector_num, sector in sector_matrices.items():
        
        
        
            #COMPROBAR SI ESTA LINEA ES NECESARIA
            #file.write(f"Sector {sector_num}:\n")  # Escribir el número del sector
            
            
            if (contador == num_sectores):
                return 0
            for row in sector:
                # Convertir los valores de cada píxel a hexadecimal y unirlos en una cadena
                row_hex = f'{separacion}'.join(f'{val:02X}' for val in row)
                # Escribir la fila en el archivo
                file.write(row_hex + '\n')
            contador += 1
            file.write('\n')  # Separador entre sectores
    print(f"Sectores guardados en {filename}")


# CODIGO PRUEBA CORRER DIRECTO ESTE ARCHIVO
if __name__ == "__main__":
    repo_base_path = os.path.dirname(__file__)

    path_imagen = os.path.join(repo_base_path, 'cat.png')
    output_sector_greyscale = os.path.join(repo_base_path, 'sectores_100x100_greyscale.txt')
    output_completo_greyscale = os.path.join(repo_base_path, 'imagen_completa_greyscale.txt')

    greyscale = cv2.imread(path_imagen, cv2.IMREAD_GRAYSCALE)

    if greyscale is None:
        print("Error al cargar la imagen.")
    else:
        sector_matrices_greyscale = divide_image_into_sectors(greyscale, sector_size=100)

        if sector_matrices_greyscale:
            save_sectors_to_file(sector_matrices_greyscale, output_sector_greyscale, ' ', 16)
            save_combined_sectors_to_file(sector_matrices_greyscale, output_completo_greyscale)
