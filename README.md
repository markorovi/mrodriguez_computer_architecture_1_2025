# Proyecto: Interfaz y Ejecución de Interpolación en Ensamblador x86-64

Este proyecto combina una interfaz gráfica escrita en Python con `Tkinter` y una rutina de interpolación escrita en lenguaje ensamblador para arquitectura x86-64.

---

## Requisitos

Antes de ejecutar o compilar, asegúrate de tener instalado en tu sistema:

- Python 3.x
- OpenCV (`cv2`)
- Pillow (`PIL`)
- Tkinter
- NASM (Netwide Assembler) para x86-64

---

##  Instalación en Linux

### Instalación de Python 3 y PIP

Primero, instala Python y su administrador de paquetes `pip`:

```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

---

### Instalación de OpenCV (`cv2`)

Para instalar OpenCV en Python:

```bash
pip3 install opencv-python
```

---

###  Instalación de Pillow (`PIL`)

Pillow es la librería recomendada para manipulación de imágenes:

```bash
pip3 install Pillow
```

---

### Instalación de Tkinter

Tkinter usualmente viene preinstalado con Python, pero si no lo tienes:

```bash
sudo apt install python3-tk -y
```

---

### Instalación de NASM

NASM es el ensamblador que se utiliza para compilar el código en lenguaje ensamblador x86-64:

```bash
sudo apt update
sudo apt install nasm -y
```

Puedes verificar la instalación con:

```bash
nasm -v
```

---

## Compilación del Código en Ensamblador

Para compilar y enlazar tu archivo `interpolacion.s` sigue los siguientes pasos desde la terminal:

```bash
nasm -f elf64 -F dwarf -g interpolacion.s -o interpolacion.o
ld interpolacion.o -o interpolacion
```

Una vez compilado, ejecuta el programa:

```bash
./interpolacion
```

---

## Ejecución de la Interfaz Python

Después de compilar el código ensamblador, ejecuta la interfaz gráfica que controlará el flujo del programa:

```bash
python3 interfaz.py
```

---

## Flujo de Uso

1. Compilar el código ensamblador usando `nasm` y `ld`.
2. Ejecutar el binario ensamblador (`./interpolacion`) si se requiere procesamiento previo.
3. Ejecutar la interfaz con:

```bash
python3 interfaz.py
```

---

## Nota

Asegúrate de tener los permisos adecuados para ejecutar archivos binarios en tu carpeta de trabajo:

```bash
chmod +x interpolacion
```

---

## Dependencias

- Python 3.x
- OpenCV
- Pillow
- Tkinter
- NASM (Netwide Assembler)

---




