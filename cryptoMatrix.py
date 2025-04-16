import random
import string

def generate_matrix(key, size=7):
    alphabet = list(string.ascii_uppercase + "Ç")
    random.seed(key)  # Usa a chave para definir a semente do gerador de números aleatórios
    while len(alphabet) < size * size:
        alphabet += alphabet  # Preenche as 49 posições (7x7)
    random.shuffle(alphabet)
    matrix = [alphabet[i * size:(i + 1) * size] for i in range(size)]
    return matrix

def print_matrix(matrix):
    for i, row in enumerate(matrix):
        print(f"{i+1}: " + " ".join(row))

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
    print("Matriz utilizada:")
    print_matrix(matrix)
    
    message = input("Digite a mensagem que será criptografada: ")
    encrypted = encrypt(message, matrix)
    print(f"Mensagem criptografada: {encrypted}")
    
    decrypted = decrypt(encrypted, matrix)
    print(f"Mensagem descriptografada: {decrypted}")

if __name__ == "__main__":
    main()
