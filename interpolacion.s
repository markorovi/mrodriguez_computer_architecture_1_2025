section .data
    input_file  db "sector.txt", 0
    output_file db "test.bin", 0
    create_flags equ 0x42        ; O_CREAT|O_WRONLY|O_TRUNC
    create_mode  equ 0644o       ; rw-r--r--
    
    SYS_OPEN    equ 2
    SYS_READ    equ 0
    SYS_WRITE   equ 1
    SYS_CLOSE   equ 3
    SYS_EXIT    equ 60
    
    MATRIX_SIZE     equ 100
    OUTPUT_SIZE     equ 200      ; Tamaño matriz interpolada (2x)

section .bss
    input_matrix    resb MATRIX_SIZE * MATRIX_SIZE
    output_matrix   resb OUTPUT_SIZE * OUTPUT_SIZE
    input_fd        resq 1
    output_fd       resq 1
    buffer          resb 30000   ; Buffer para lectura

section .text
    global _start

_start:
    ; Abrir archivo de entrada
    mov rax, SYS_OPEN
    lea rdi, [rel input_file]
    mov rsi, 0              ; O_RDONLY
    syscall
    cmp rax, 0
    jl exit_error
    mov [rel input_fd], rax

    ; Leer todo el archivo
    mov rax, SYS_READ
    mov rdi, [rel input_fd]
    lea rsi, [rel buffer]
    mov rdx, 30000          ; Tamaño suficiente
    syscall
    cmp rax, 0
    jle exit_error

    ; Cerrar archivo de entrada
    mov rax, SYS_CLOSE
    mov rdi, [rel input_fd]
    syscall

    ; Procesar datos y llenar matriz de entrada
    lea rsi, [rel buffer]     ; Puntero a datos
    lea rdi, [rel input_matrix] ; Puntero a matriz
    mov rcx, MATRIX_SIZE * MATRIX_SIZE
    xor rbx, rbx             ; Contador de valores

process_hex:
    ; Buscar siguiente dígito hexadecimal
    mov al, [rsi]
    inc rsi
    
    ; Ignorar caracteres no válidos
    cmp al, ' '
    je process_hex
    cmp al, 9               ; Tab
    je process_hex
    cmp al, 10              ; LF
    je process_hex
    cmp al, 13              ; CR
    je process_hex
    
    ; Primer nibble
    call ascii_to_nibble
    shl al, 4
    mov dl, al
    
    ; Segundo nibble
    mov al, [rsi]
    inc rsi
    call ascii_to_nibble
    or al, dl
    
    ; Guardar en matriz de entrada
    mov [rdi], al
    inc rdi
    
    ; Verificar si completamos la matriz
    inc rbx
    cmp rbx, MATRIX_SIZE * MATRIX_SIZE
    jl process_hex

    ; Aplicar interpolación
    call interpolate_matrix

    ; Crear archivo binario de salida
    mov rax, SYS_OPEN
    lea rdi, [rel output_file]
    mov rsi, create_flags
    mov rdx, create_mode
    syscall
    cmp rax, 0
    jl exit_error
    mov [rel output_fd], rax

    ; Escribir matriz interpolada completa
    mov rax, SYS_WRITE
    mov rdi, [rel output_fd]
    lea rsi, [rel output_matrix]
    mov rdx, OUTPUT_SIZE * OUTPUT_SIZE
    syscall

    ; Cerrar archivo de salida
    mov rax, SYS_CLOSE
    mov rdi, [rel output_fd]
    syscall

exit:
    mov rax, SYS_EXIT
    xor rdi, rdi
    syscall

exit_error:
    mov rax, SYS_EXIT
    mov rdi, 1
    syscall

ascii_to_nibble:
    cmp al, '9'
    jbe .digit
    and al, 0xDF    ; Convertir a mayúscula
    sub al, 'A' - 10
    ret
.digit:
    sub al, '0'
    ret

; ---- Rutina de interpolación ----
interpolate_matrix:
    ; Utilizamos:
    ; r8, r9 - Para coordenadas y cálculos de índices
    ; r10, r11 - Para los valores originales
    ; r12, r13, r14, r15 - Para cálculos temporales
    ; rax, rbx, rcx, rdx - Para valores interpolados y contadores

    xor r8, r8      ; r8 = fila_actual
    mov r9, 3       ; r9 = divisor para las operaciones (3)

process_rows:
    cmp r8, MATRIX_SIZE-1  ; Procesar hasta penúltima fila
    jge interpolation_done
    
    xor r10, r10    ; r10 = columna_actual

process_cols:
    cmp r10, MATRIX_SIZE-1 ; Procesar hasta penúltima columna
    jge next_row

    ; Calcular los índices para las esquinas originales de 2x2
    mov r11, r8
    imul r11, MATRIX_SIZE
    add r11, r10
    lea rsi, [rel input_matrix]
    add rsi, r11      ; rsi = puntero a esquina superior izquierda (A)

    ; Cargar los 4 valores de esquina
    movzx rax, byte [rsi]                    ; A = esquina superior izquierda
    movzx rbx, byte [rsi+1]                  ; B = esquina superior derecha
    movzx rcx, byte [rsi+MATRIX_SIZE]        ; C = esquina inferior izquierda
    movzx rdx, byte [rsi+MATRIX_SIZE+1]      ; D = esquina inferior derecha

    ; Calcular posición en la matriz de salida (primera fila, primera columna de este bloque 4x4)
    mov r12, r8
    shl r12, 1      ; r12 = fila_original * 2
    mov r13, r10
    shl r13, 1      ; r13 = columna_original * 2
    mov r14, r12
    imul r14, OUTPUT_SIZE
    add r14, r13    ; r14 = índice en matriz de salida

    lea rdi, [rel output_matrix]
    add rdi, r14    ; rdi = puntero a inicio de este bloque 4x4 en salida

    ; --- Primera fila de la matriz interpolada 4x4 ---
    ; (0,0) = A
    mov byte [rdi], al
    
    ; (0,1) = (2/3 * A) + (1/3 * B)
    mov r14, rax            ; r14 = A
    shl r14, 1              ; r14 = 2*A
    add r14, rbx            ; r14 = 2*A + B
    xor rdx, rdx
    mov rax, r14
    div r9                  ; rax = (2*A + B) / 3
    mov byte [rdi+1], al
    
    ; (0,2) = (1/3 * A) + (2/3 * B)
    mov r14, rbx            ; r14 = B
    shl r14, 1              ; r14 = 2*B
    add r14, rax            ; r14 = 2*B + A
    xor rdx, rdx
    mov rax, r14
    div r9                  ; rax = (2*B + A) / 3
    mov byte [rdi+2], al
    
    ; (0,3) = B
    mov byte [rdi+3], bl

    ; --- Segunda fila de la matriz interpolada 4x4 ---
    ; (1,0) = (2/3 * A) + (1/3 * C)
    movzx rax, byte [rsi]   ; A
    movzx rcx, byte [rsi+MATRIX_SIZE] ; C
    mov r14, rax            ; r14 = A
    shl r14, 1              ; r14 = 2*A
    add r14, rcx            ; r14 = 2*A + C
    xor rdx, rdx
    mov rax, r14
    div r9                  ; rax = (2*A + C) / 3
    mov byte [rdi+OUTPUT_SIZE], al
    
    ; (1,1) = Interpolación de 4 esquinas mixta
    movzx rax, byte [rdi]              ; A
    movzx rbx, byte [rdi+3]            ; B
    movzx rcx, byte [rdi+OUTPUT_SIZE*3] ; C
    movzx rdx, byte [rdi+OUTPUT_SIZE*3+3] ; D
    
    ; (1,1) = (4/9 * A) + (2/9 * B) + (2/9 * C) + (1/9 * D)
    ; Aproximado como (2/3 * A) + (1/3 * B+C+D)/3
    mov r14, rax            ; r14 = A
    shl r14, 1              ; r14 = 2*A
    
    mov r15, rbx            ; r15 = B
    add r15, rcx            ; r15 = B + C
    add r15, rdx            ; r15 = B + C + D
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r15
    div r9                  ; rax = (B + C + D) / 3
    
    add r14, rax            ; r14 = 2*A + (B + C + D)/3
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r14
    div r9                  ; rax = (2*A + (B+C+D)/3) / 3
    
    mov byte [rdi+OUTPUT_SIZE+1], al
    
    ; (1,2) = Interpolar similar a (1,1) pero con énfasis en B
    movzx rax, byte [rdi]              ; A
    movzx rbx, byte [rdi+3]            ; B
    movzx rcx, byte [rdi+OUTPUT_SIZE*3] ; C
    movzx rdx, byte [rdi+OUTPUT_SIZE*3+3] ; D
    
    ; (1,2) = (2/9 * A) + (4/9 * B) + (1/9 * C) + (2/9 * D)
    ; Aproximado como (2/3 * B) + (1/3 * A+C+D)/3
    mov r14, rbx            ; r14 = B
    shl r14, 1              ; r14 = 2*B
    
    mov r15, rax            ; r15 = A
    add r15, rcx            ; r15 = A + C
    add r15, rdx            ; r15 = A + C + D
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r15
    div r9                  ; rax = (A + C + D) / 3
    
    add r14, rax            ; r14 = 2*B + (A + C + D)/3
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r14
    div r9                  ; rax = (2*B + (A+C+D)/3) / 3
    
    mov byte [rdi+OUTPUT_SIZE+2], al
    
    ; (1,3) = (2/3 * B) + (1/3 * D)
    movzx rbx, byte [rsi+1]         ; B
    movzx rdx, byte [rsi+MATRIX_SIZE+1] ; D
    mov r14, rbx            ; r14 = B
    shl r14, 1              ; r14 = 2*B
    add r14, rdx            ; r14 = 2*B + D
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r14
    div r9                  ; rax = (2*B + D) / 3
    mov byte [rdi+OUTPUT_SIZE+3], al

    ; --- Tercera fila de la matriz interpolada 4x4 ---
    ; (2,0) = (1/3 * A) + (2/3 * C)
    movzx rax, byte [rsi]           ; A
    movzx rcx, byte [rsi+MATRIX_SIZE] ; C
    mov r14, rcx            ; r14 = C
    shl r14, 1              ; r14 = 2*C
    add r14, rax            ; r14 = 2*C + A
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r14
    div r9                  ; rax = (2*C + A) / 3
    mov byte [rdi+OUTPUT_SIZE*2], al
    
    ; (2,1) = Interpolar similar a (1,1) pero con énfasis en C
    movzx rax, byte [rdi]              ; A
    movzx rbx, byte [rdi+3]            ; B
    movzx rcx, byte [rdi+OUTPUT_SIZE*3] ; C
    movzx rdx, byte [rdi+OUTPUT_SIZE*3+3] ; D
    
    ; (2,1) = (2/9 * A) + (1/9 * B) + (4/9 * C) + (2/9 * D)
    ; Aproximado como (2/3 * C) + (1/3 * A+B+D)/3
    mov r14, rcx            ; r14 = C
    shl r14, 1              ; r14 = 2*C
    
    mov r15, rax            ; r15 = A
    add r15, rbx            ; r15 = A + B
    add r15, rdx            ; r15 = A + B + D
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r15
    div r9                  ; rax = (A + B + D) / 3
    
    add r14, rax            ; r14 = 2*C + (A + B + D)/3
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r14
    div r9                  ; rax = (2*C + (A+B+D)/3) / 3
    
    mov byte [rdi+OUTPUT_SIZE*2+1], al
    
    ; (2,2) = Interpolar similar a (1,2) pero con énfasis en D
    movzx rax, byte [rdi]              ; A
    movzx rbx, byte [rdi+3]            ; B
    movzx rcx, byte [rdi+OUTPUT_SIZE*3] ; C
    movzx rdx, byte [rdi+OUTPUT_SIZE*3+3] ; D
    
    ; (2,2) = (1/9 * A) + (2/9 * B) + (2/9 * C) + (4/9 * D)
    ; Aproximado como (2/3 * D) + (1/3 * A+B+C)/3
    mov r14, rdx            ; r14 = D
    shl r14, 1              ; r14 = 2*D
    
    mov r15, rax            ; r15 = A
    add r15, rbx            ; r15 = A + B
    add r15, rcx            ; r15 = A + B + C
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r15
    div r9                  ; rax = (A + B + C) / 3
    
    add r14, rax            ; r14 = 2*D + (A + B + C)/3
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r14
    div r9                  ; rax = (2*D + (A+B+C)/3) / 3
    
    mov byte [rdi+OUTPUT_SIZE*2+2], al
    
    ; (2,3) = (1/3 * B) + (2/3 * D)
    movzx rbx, byte [rsi+1]           ; B
    movzx rdx, byte [rsi+MATRIX_SIZE+1] ; D
    mov r14, rdx            ; r14 = D
    shl r14, 1              ; r14 = 2*D
    add r14, rbx            ; r14 = 2*D + B
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r14
    div r9                  ; rax = (2*D + B) / 3
    mov byte [rdi+OUTPUT_SIZE*2+3], al

    ; --- Cuarta fila de la matriz interpolada 4x4 ---
    ; (3,0) = C
    movzx rcx, byte [rsi+MATRIX_SIZE]
    mov byte [rdi+OUTPUT_SIZE*3], cl
    
    ; (3,1) = (2/3 * C) + (1/3 * D)
    movzx rcx, byte [rsi+MATRIX_SIZE]    ; C
    movzx rdx, byte [rsi+MATRIX_SIZE+1]  ; D
    mov r14, rcx            ; r14 = C
    shl r14, 1              ; r14 = 2*C
    add r14, rdx            ; r14 = 2*C + D
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r14
    div r9                  ; rax = (2*C + D) / 3
    mov byte [rdi+OUTPUT_SIZE*3+1], al
    
    ; (3,2) = (1/3 * C) + (2/3 * D)
    movzx rcx, byte [rsi+MATRIX_SIZE]    ; C
    movzx rdx, byte [rsi+MATRIX_SIZE+1]  ; D
    mov r14, rdx            ; r14 = D
    shl r14, 1              ; r14 = 2*D
    add r14, rcx            ; r14 = 2*D + C
    xor rdx, rdx            ; Limpiar rdx antes de dividir
    mov rax, r14
    div r9                  ; rax = (2*D + C) / 3
    mov byte [rdi+OUTPUT_SIZE*3+2], al
    
    ; (3,3) = D
    movzx rdx, byte [rsi+MATRIX_SIZE+1]
    mov byte [rdi+OUTPUT_SIZE*3+3], dl

    ; Avanzar a la siguiente columna
    inc r10
    jmp process_cols

next_row:
    inc r8
    jmp process_rows

interpolation_done:
    ret
