import secrets
import random
import string
import re
import os
import hmac
import hashlib
from hashlib import pbkdf2_hmac

YELLOW = "\033[33m"
BLUE = "\033[34m"
PURPLE = "\033[35m"
RED = "\033[31m"
RESET = "\033[0m"

# CSPRNG ( não determinístico)
csprng = secrets.SystemRandom()

VALID_PATTERN = r"[A-ZÇ ]+"

BASE_ALPHABET = list(string.ascii_uppercase + "Ç ")

# Parâmetros PBKDF2 para key stretching
PBKDF2_HASH = 'sha256'
PBKDF2_ITERATIONS = 100_000
KEY_LEN = 64  # bytes para permitir divisão em duas chaves
SALT_LEN = 16  # bytes

# Usa duas chaves separadas (32 bytes cada) para matrix_seed e para mac_key
def derive_keys(passphrase: str, salt_bytes: bytes) -> tuple[bytes, bytes]:
    full_key = pbkdf2_hmac(PBKDF2_HASH, passphrase.encode(), salt_bytes, PBKDF2_ITERATIONS, dklen=KEY_LEN)
    return full_key[:32], full_key[32:]


def validate_message(msg: str) -> bool:
    return bool(re.fullmatch(VALID_PATTERN, msg))


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Usa PRNG com seed derivada
def generate_matrix(matrix_seed: bytes, size=7):
    seed_int = int.from_bytes(matrix_seed, 'big')
    local_rng = random.Random(seed_int)

    matrix_list = BASE_ALPHABET.copy()
    while len(matrix_list) < size * size:
        matrix_list += BASE_ALPHABET.copy()
    matrix_list = matrix_list[: size * size]

    local_rng.shuffle(matrix_list)

    counts = {c: matrix_list.count(c) for c in set(BASE_ALPHABET)}
    missing = [c for c, ct in counts.items() if ct == 0]
    if missing:
        from collections import Counter
        dup_pos = [i for i, c in enumerate(matrix_list) if Counter(matrix_list)[c] > 1]
        local_rng.shuffle(dup_pos)
        for sym, pos in zip(missing, dup_pos):
            matrix_list[pos] = sym

    return [matrix_list[i*size:(i+1)*size] for i in range(size)]


def print_matrix(matrix):
    for i, row in enumerate(matrix):
        print(f"{BLUE}{i+1}:{RESET}", " ".join(row))


def encrypt(message: str, matrix: list, mac_key: bytes) -> tuple[str, str]:
    pos_full = {}
    for i, row in enumerate(matrix):
        for j, sym in enumerate(row):
            pos_full.setdefault(sym, []).append((i+1, j+1))
    pool = {s: lst.copy() for s, lst in pos_full.items()}

    ct = ""
    for ch in message:
        if not pool[ch]:
            pool[ch] = pos_full[ch].copy()
        r, c = csprng.choice(pool[ch])
        ct += f"{r}{c}"
        pool[ch].remove((r, c))

    tag = hmac.new(mac_key, ct.encode(), hashlib.sha256).hexdigest()
    return ct, tag # ciphertext e tag_hex


def decrypt(ciphertext: str, tag: str, matrix: list, mac_key: bytes) -> str:
    expected = hmac.new(mac_key, ciphertext.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, tag):
        raise ValueError("MAC inválido: dados alterados ou senha incorreta.")

    pt = ""
    i = 0
    while i < len(ciphertext):
        token = ciphertext[i:i+2]
        r, c = int(token[0]) - 1, int(token[1]) - 1
        pt += matrix[r][c]
        i += 2
    return pt


def main():
    clear_terminal()
    user_passphrase = input(f"{YELLOW}Digite a chave para gerar a matriz: {RESET}")
    salt_bytes = secrets.token_bytes(SALT_LEN)
    matrix_seed, mac_key = derive_keys(user_passphrase, salt_bytes)

    matrix = generate_matrix(matrix_seed)
    while True:
        clear_terminal()
        print(f"{YELLOW}{'='*10} ATENÇÃO {'='*9}")
        print(f"{BLUE}Permitido: A–Z | Ç | espaço")
        print(f"{YELLOW}{'='*28}")
        print_matrix(matrix)
        msg = input(f"\n{YELLOW}Mensagem: {RESET}").strip().upper()
        if validate_message(msg): break

    ct, tag = encrypt(msg, matrix, mac_key)
    print(f"{PURPLE}Cifrado:{RESET}", ct)
    print(f"{PURPLE}Tag (MAC):{RESET}", tag)
    print(f"{PURPLE}Salt (HEX):{RESET}", salt_bytes.hex())

    try:
        pt = decrypt(ct, tag, matrix, mac_key)
        print(f"\n{BLUE}Decifrado:{RESET}", pt)
    except ValueError as e:
        print(f"{RED}Erro:{RESET}", e)
    print(f"{BLUE}Chave (passphrase):{YELLOW}", user_passphrase)


if __name__ == "__main__":
    main()
