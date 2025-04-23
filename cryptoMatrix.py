import random
import string
import re
import os

YELLOW = "\033[33m"
BLUE = "\033[34m"
PURPLE = "\033[35m"
RESET = "\033[0m"

def validate_message(msg):
    return bool(re.fullmatch(r"[A-ZÇ ]+", msg)) # Retorna TRUE se msg conter apenas letras que estejam dentro do range A–Z e/ou Ç (Inclui espaços também).

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear') # Verifica o sistema operacional para a utilização correta do comando

def generate_matrix(key, size=7):
    # Alfabeto base (A-Z + Ç)
    base_alphabet = list(string.ascii_uppercase + "Ç")
    random.seed(key)  # Usa a chave para SEED fixa

    # Cria lista inicial garantindo pelo menos uma de cada letra
    matrix_list = base_alphabet.copy()
    # Preenche o restante com cópias do alfabeto até atingir size*size
    while len(matrix_list) < size * size:
        matrix_list += base_alphabet.copy()

    # Embaralha e corta para o tamanho exato
    random.shuffle(matrix_list)
    matrix_list = matrix_list[: size * size]

    # Garante que todas as letras estejam presentes
    required = set(base_alphabet)
    present = set(matrix_list)
    missing = list(required - present)
    if missing:
        # Conta ocorrências para identificar duplicatas
        from collections import Counter
        counts = Counter(matrix_list)
        # Posições de caracteres que aparecem mais de uma vez
        duplicate_positions = [i for i, c in enumerate(matrix_list) if counts[c] > 1]
        random.shuffle(duplicate_positions)
        # Substitui duplicatas por cada letra faltante
        for letter, pos in zip(missing, duplicate_positions):
            matrix_list[pos] = letter

    # Constrói a matriz 7x7
    matrix = [matrix_list[i * size : (i + 1) * size] for i in range(size)]
    return matrix

def print_matrix(matrix):
    for i, row in enumerate(matrix):
        print(f"{BLUE}{i+1}:{RESET} " + " ".join(row))

def encrypt(message, matrix):
    encrypted = ""
    # Cria um dicionário com todas as posições disponíveis para cada caractere na matriz
    positions_full = {}
    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            if cell not in positions_full:
                positions_full[cell] = []
            positions_full[cell].append((i+1, j+1))
            
    # Cria uma pool para usar durante a criptografia (cópia inicial)
    positions_pool = {char: pos_list.copy() for char, pos_list in positions_full.items()}
    
    for char in message.upper():
        if char == ' ':
            # Usa uma letra aleatória de A-Z (exceto Ç) como prefixo para o token de espaço
            prefix = random.choice(string.ascii_uppercase)
            token = prefix + str(random.randint(11, 77))
            encrypted += token
        else:
            if char in positions_pool:
                # Se a pool estiver vazia, reinicializa-a com as posições originais
                if not positions_pool[char]:
                    positions_pool[char] = positions_full[char].copy()
                r, c = random.choice(positions_pool[char])
                encrypted += f"{r}{c}"
                # Remove a posição utilizada para favorecer posições diferentes
                positions_pool[char].remove((r, c))
            else:
                # Caso o caractere não exista na matriz, insere token padrão
                encrypted += "XX"
    return encrypted

def decrypt(encrypted_text, matrix):
    decrypted = ""
    i = 0
    while i < len(encrypted_text):
        char = encrypted_text[i]
        # Verifica se é um token de espaço: começa com A-Z e os dois próximos são dígitos
        if char in string.ascii_uppercase and i + 2 < len(encrypted_text) and encrypted_text[i+1:i+3].isdigit():
            decrypted += ' '
            i += 3
        else:
            # Token de letra: 2 caracteres (ex: "21")
            token = encrypted_text[i:i+2]
            row = int(token[0]) - 1
            col = int(token[1]) - 1
            decrypted += matrix[row][col]
            i += 2
    return decrypted

def main():
    key = input("Digite a chave para gerar a matriz: ")
    matrix = generate_matrix(key)

    while True:
        clear_terminal()
        print(f"{YELLOW}{'=' * 18} ATENÇÃO {'=' * 18}")
        print(f"{BLUE}Caracteres permitidos: A–Z  |  Ç  |  Espaços")
        print(f"{YELLOW}{'=' * 45}")
        print(f"\nChave utilizada:{RESET} {key}\n{YELLOW}Matriz utilizada:{RESET} ")
        print_matrix(matrix)
        message = input(f"\n{YELLOW}Digite a mensagem:{RESET} ").strip().upper()
        if validate_message(message):
            break
    
    encrypted = encrypt(message, matrix)
    print(f"\n{PURPLE}Mensagem criptografada:{RESET} {encrypted}")
    
    decrypted = decrypt(encrypted, matrix)
    print(f"{PURPLE}Mensagem descriptografada:{RESET} {decrypted}")
    print(f"{PURPLE}Chave utilizada:{YELLOW} {key} {RESET}")

if __name__ == "__main__":
    main()
