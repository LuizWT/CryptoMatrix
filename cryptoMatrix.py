import secrets
import random
import string
import os
import hmac
import hashlib
from hashlib import pbkdf2_hmac
import math

# Cores (ANSI) para terminal
YELLOW = "\033[33m"
BLUE   = "\033[34m"
PURPLE = "\033[35m"
RED    = "\033[31m"
RESET  = "\033[0m"

# CSPRNG para escolhas aleatórias e que são seguras
e_rng = secrets.SystemRandom()

# Parâmetros PBKDF2 para key stretching
PBKDF2_HASH       = 'sha256'
PBKDF2_ITERATIONS = 100_000
KEY_LEN           = 64 # Bytes para posteriormente se dividir em duas chaves de 32
SALT_LEN          = 16 # Bytes para MAC

# Caracteres
t_BASE_UPPER = list(string.ascii_uppercase) + ['Ç'] # A-Z + Ç
DIGITS       = list(string.digits) # 0-9
BASE_LOWER   = list(string.ascii_lowercase) + ['ç'] # a-z + ç
PUNCTUATION  = list(string.punctuation) # Caracteres especiais (ASCII)
SYMBOLS      = t_BASE_UPPER + [' '] + DIGITS + BASE_LOWER + PUNCTUATION # Junta os caracteres citados acima (mais o caractere de espaço)

# Número mínimo e máximo de células na matriz 3D
MIN_CELLS = len(set(SYMBOLS)) # 97 símbolos (únicos)
MAX_CELLS = 1000              # Evita consumo demais

# Armazena ciphertext raw
default_raw_ct = None

# Deriva seed fixo para matriz a partir da passphrase
def derive_matrix_seed(passphrase: str) -> bytes:
    return hashlib.sha256(passphrase.encode('utf-8')).digest()

# Deriva apenas o mac_key usando PBKDF2 (passphrase e salt)
def derive_mac_key(passphrase: str, salt: bytes) -> bytes:
    full = pbkdf2_hmac(
        PBKDF2_HASH,
        passphrase.encode('utf-8'),
        salt,
        PBKDF2_ITERATIONS,
        dklen=KEY_LEN
    )
    return full[KEY_LEN//2:]

# Valida se cada caractere está no conjunto SYMBOLS
def validate_message(msg: str) -> bool:
    return all(ch in SYMBOLS for ch in msg)

# Limpa o terminal
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Calcula dimensões (depth, rows, cols) balanceadas e determinísticas
def decide_dimensions(seed_int: int) -> tuple[int, int, int]:
    random.seed(seed_int)
    candidates = []
    # Limite para cada dimensão (baseado no teto estipulado)
    max_dim = int(math.ceil(MAX_CELLS ** (1/3)))
    for d in range(1, max_dim + 1):
        for r in range(1, max_dim + 1):
            c = math.ceil(MIN_CELLS / (d * r))
            if c < 1:
                continue
            total = d * r * c
            if total >= MIN_CELLS and total <= MAX_CELLS:
                candidates.append((d, r, c))
    if not candidates:
        # fallback simples
        return 1, 1, MIN_CELLS
    random.shuffle(candidates)
    return candidates[0]

# Gera matriz 3D com shuffle determinístico (matrix_seed)
def generate_matrix(matrix_seed: bytes, depth: int, rows: int, cols: int) -> list[list[list[str]]]:
    total = depth * rows * cols
    if total < MIN_CELLS:
        raise ValueError(f"Matriz deve ter ao menos {MIN_CELLS} células, mas tem {total}.")

    # Lista inicial de símbolos únicos
    ml = SYMBOLS.copy()
    # Preenche extras (mas só se for necessário)
    while len(ml) < total:
        ml += SYMBOLS.copy()
    ml = ml[:total]

    # Embaralha (rng.suffle) com seed determinístico
    seed_int = int.from_bytes(matrix_seed, 'big')
    rng = random.Random(seed_int)
    rng.shuffle(ml)

    # garante que todos os símbolos apareçam
    from collections import Counter
    counts = Counter(ml)
    missing = [s for s in SYMBOLS if counts[s] == 0]
    if missing:
        dup_positions = [i for i, s in enumerate(ml) if counts[s] > 1]
        rng.shuffle(dup_positions)
        for sym, pos in zip(missing, dup_positions):
            counts[ml[pos]] -= 1
            ml[pos] = sym
            counts[sym] += 1

    # constrói a matriz 3D
    matrix = []
    it = iter(ml)
    for _ in range(depth):
        layer = []
        for _ in range(rows):
            row = [next(it) for _ in range(cols)]
            layer.append(row)
        matrix.append(layer)
    return matrix

# Imprime a matriz 3D por camadas
def print_matrix(matrix: list[list[list[str]]]):
    for d, layer in enumerate(matrix):
        print(f"{BLUE}{'=' * 10} Camada {d} {'=' * 10}{RESET}\n")
        col_header = "     " + " ".join(f"{i:>2}" for i in range(len(layer[0])))
        print(f"{YELLOW}{col_header}{RESET}\n")
        for r_idx, row in enumerate(layer):
            row_str = " ".join(f"{ch:>2}" for ch in row)
            print(f"{YELLOW}{r_idx:>2}:{RESET}  {row_str}")
        print()


# Gera raw_ct (string de coordenadas 6 dígitos por símbolo) e usa mac_key para HMAC
def encrypt(msg: str, matrix: list[list[list[str]]], mac_key: bytes) -> tuple[str, str]:
    global default_raw_ct
    pos_map = {}
    # mapeia cada símbolo às suas posições (d,r,c)
    for d, layer in enumerate(matrix, start=0):
        for r, row in enumerate(layer, start=0):
            for c, ch in enumerate(row, start=0):
                pos_map.setdefault(ch, []).append((d, r, c))

    pool = {ch: pos_map[ch].copy() for ch in pos_map}
    raw = ''
    for ch in msg:
        if ch not in pool:
            raise ValueError(f"Caractere inválido: '{ch}' não encontrado na matriz.")
        if not pool[ch]:
            pool[ch] = pos_map[ch].copy()
        d, r, c = e_rng.choice(pool[ch])
        raw += f"{d:02}{r:02}{c:02}"
        pool[ch].remove((d, r, c))

    default_raw_ct = raw
    display = raw.replace('0', '')  # Corta os zeros para exibição
    tag = hmac.new(mac_key, raw.encode('utf-8'), hashlib.sha256).hexdigest()
    return display, tag

# Usa default_raw_ct para descriptografar (aqui inclui os zeros)
def decrypt(ct: str, tag: str, matrix: list[list[list[str]]], mac_key: bytes) -> str:
    raw = default_raw_ct
    expected = hmac.new(mac_key, raw.encode('utf-8'), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, tag):
        raise ValueError("MAC inválido: dados alterados ou senha incorreta.")

    pt = ''
    # cada símbolo usa 6 dígitos: 2 (d) + 2 (r) + 2 (c)
    for i in range(0, len(raw), 6):
        d = int(raw[i:i+2])
        r = int(raw[i+2:i+4])
        c = int(raw[i+4:i+6])
        pt += matrix[d][r][c]
    return pt

def main():
    clear_terminal()
    user_passphrase = input(f"{YELLOW}Digite a chave para gerar a matriz: {RESET}")

    matrix_seed = derive_matrix_seed(user_passphrase)
    seed_int = int.from_bytes(matrix_seed, 'big')
    depth, rows, cols = decide_dimensions(seed_int)

    salt = secrets.token_bytes(SALT_LEN)
    mac_key = derive_mac_key(user_passphrase, salt)

    matrix = generate_matrix(matrix_seed, depth, rows, cols)

    while True:
        clear_terminal()
        print(f"{YELLOW}{'='*10} ATENÇÃO {'='*9}")
        print(f"{RED} Não permitido: caracteres fora do padrão ASCII e acentos{RESET}")
        print(f"{YELLOW}{'='*28}\n")
        print(f"Dimensões definidas: {depth}x{rows}x{cols} ( >= {MIN_CELLS} células)\n")
        print_matrix(matrix)
        msg = input(f"\n{YELLOW}Mensagem: {RESET}").strip()
        if validate_message(msg):
            break
        clear_terminal()

    display_ct, tag = encrypt(msg, matrix, mac_key)
    print(f"{PURPLE}Cifrado:{RESET}", display_ct)
    print(f"{PURPLE}Tag (MAC):{RESET}", tag)
    print(f"{PURPLE}Salt (hex):{RESET}", salt.hex())

    try:
        pt = decrypt(None, tag, matrix, mac_key)
        print(f"\n{BLUE}Decifrado:{RESET}", pt)
        print(f"\n{YELLOW}Chave (Passphrase):{RESET}", user_passphrase)
    except ValueError as e:
        print(f"{RED}Erro:{RESET}", e)

if __name__ == '__main__':
    main()