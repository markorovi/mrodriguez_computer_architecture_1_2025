import numpy as np
from PIL import Image  # Biblioteca más ligera que suele estar preinstalada

def leer_y_mostrar_imagen():
    try:
        # Leer el archivo binario
        with open('test.bin', 'rb') as f:
            datos = np.frombuffer(f.read(), dtype=np.uint8)
        
        # Reformar a matriz 200x200
        imagen = datos.reshape((200, 200))
        
        # Convertir a imagen PIL y mostrar
        img = Image.fromarray(imagen, mode='L')  # 'L' para escala de grises
        img.show()
        
        # Guardar copia
        img.save('imagen_procesada.png')
        print("Imagen guardada como 'imagen_procesada.png'")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Asegúrate de que:")
        print("1. El archivo 'test.bin' existe")
        print("2. Tiene exactamente 40,000 bytes (200x200)")
        print("3. Tienes permisos de lectura")

if __name__ == "__main__":
    leer_y_mostrar_imagen()
