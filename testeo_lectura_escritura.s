section .data
    input_file  db "sector.txt", 0
    output_file db "test.bin", 0  ; Cambiado a binario
    create_flags equ 0x42        ; O_CREAT|O_WRONLY|O_TRUNC
    create_mode  equ 0644o       ; rw-r--r--
    
    SYS_OPEN    equ 2
    SYS_READ    equ 0
    SYS_WRITE   equ 1
    SYS_CLOSE   equ 3
    SYS_EXIT    equ 60
    
    MATRIX_SIZE equ 100

section .bss
    matrix      resb MATRIX_SIZE * MATRIX_SIZE
    input_fd    resq 1
    output_fd   resq 1
    buffer      resb 30000       ; Buffer amplio para lectura

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

    ; Procesar datos y llenar matriz
    lea rsi, [rel buffer]   ; Puntero a datos
    lea rdi, [rel matrix]   ; Puntero a matriz
    mov rcx, MATRIX_SIZE * MATRIX_SIZE
    xor rbx, rbx            ; Contador de valores

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
    
    ; Incrementar valor
    inc al
    jnz .no_overflow
    xor al, al              ; Manejar FF -> 00
.no_overflow:
    
    ; Guardar en matriz
    mov [rdi], al
    inc rdi
    
    ; Verificar si completamos la matriz
    inc rbx
    cmp rbx, MATRIX_SIZE * MATRIX_SIZE
    jl process_hex

    ; Crear archivo binario de salida
    mov rax, SYS_OPEN
    lea rdi, [rel output_file]
    mov rsi, create_flags
    mov rdx, create_mode
    syscall
    cmp rax, 0
    jl exit_error
    mov [rel output_fd], rax

    ; Escribir matriz binaria completa
    mov rax, SYS_WRITE
    mov rdi, [rel output_fd]
    lea rsi, [rel matrix]
    mov rdx, MATRIX_SIZE * MATRIX_SIZE
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
