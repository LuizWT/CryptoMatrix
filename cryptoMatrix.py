from __future__ import annotations
import os, hmac, hashlib, base64, string, struct, secrets, time

_UP  = list(string.ascii_uppercase) + ['Ç']
_LO  = list(string.ascii_lowercase) + ['ç']
SYMBOLS = _UP + [' '] + list(string.digits) + _LO + list(string.punctuation)
NSYM = len(SYMBOLS)
SYM2IDX = {s: i for i, s in enumerate(SYMBOLS)}

# Há mais células que símbolos: as sobras viram homófonos (várias células por símbolo).
DEPTH, ROWS, COLS = 4, 5, 6
NCELLS = DEPTH * ROWS * COLS

# Os homófonos extras vão para os símbolos mais frequentes do português.
_FREQ = {' ':0.17,'e':0.12,'a':0.115,'o':0.10,'s':0.078,'r':0.065,'i':0.062,'n':0.05,
         'd':0.05,'m':0.047,'u':0.046,'t':0.043,'c':0.039,'l':0.028,'p':0.025}

def _build_slots() -> list[int]:
    slots = list(range(NSYM))
    ranked = sorted(range(NSYM), key=lambda i: _FREQ.get(SYMBOLS[i], 0.0), reverse=True)
    for k in range(NCELLS - NSYM):
        slots.append(ranked[k % len(ranked)])
    return slots

SLOTS = _build_slots()
SYM_SLOTS: dict[int, list[int]] = {}
for _j, _x in enumerate(SLOTS):
    SYM_SLOTS.setdefault(_x, []).append(_j)

# Token (base64url): MAGIC | versão | logN r p | salt | nonce | seq | ct | tag
# tag = HMAC-SHA256(k_mac, tudo antes do tag + AAD)
MAGIC = b'CMX3'
VERSION = 3
SALT_LEN, NONCE_LEN, SEQ_LEN, TAG_LEN = 16, 12, 8, 32
HEADER_LEN = len(MAGIC) + 1 + 3 + SALT_LEN + NONCE_LEN + SEQ_LEN
DEFAULT_LOGN, DEFAULT_R, DEFAULT_P = 15, 8, 1
MAXLEN = NSYM**3 - 1     # maior tamanho representável no prefixo de 3 símbolos
MIN_FRAME = 16           # frame mínimo, para que mensagens curtas tenham o mesmo tamanho cifrado

def _scrypt(passphrase: str, salt: bytes, logN: int, r: int, p: int) -> bytes:
    N = 1 << logN
    maxmem = 128 * r * N * 2 + (1 << 20)   # scrypt precisa de ~128·r·N bytes; o restante é folga
    return hashlib.scrypt(passphrase.encode('utf-8'), salt=salt, n=N, r=r, p=p,
                          dklen=32, maxmem=maxmem)

def calibrate_scrypt(target_seconds: float = 0.1, r: int = DEFAULT_R, p: int = DEFAULT_P,
                     lo: int = 12, hi: int = 20) -> int:
    """Maior logN cuja derivação leva até target_seconds nesta máquina."""
    salt = os.urandom(SALT_LEN); chosen = lo
    for logN in range(lo, hi + 1):
        t0 = time.perf_counter(); _scrypt("calibracao", salt, logN, r, p); dt = time.perf_counter() - t0
        if dt <= target_seconds:
            chosen = logN
        else:
            break
    return chosen

def _hkdf(master: bytes, salt: bytes, info: bytes, length: int) -> bytes:
    """HKDF-SHA256 (RFC 5869)."""
    prk = hmac.new(salt, master, hashlib.sha256).digest()
    out, t, ctr = b'', b'', 1
    while len(out) < length:
        t = hmac.new(prk, t + info + bytes([ctr]), hashlib.sha256).digest()
        out += t; ctr += 1
    return out[:length]

class _Keystream:
    """Bytes pseudoaleatórios determinísticos para (chave, nonce, posição)."""
    __slots__ = ('k', 'prefix', 'ctr', 'buf')
    def __init__(self, k: bytes, nonce: bytes, pos: int):
        self.k = k; self.prefix = nonce + struct.pack('>Q', pos); self.ctr = 0; self.buf = b''
    def _fill(self):
        self.buf += hmac.new(self.k, self.prefix + struct.pack('>I', self.ctr),
                             hashlib.sha256).digest()
        self.ctr += 1
    def byte(self) -> int:
        if not self.buf: self._fill()
        b, self.buf = self.buf[0], self.buf[1:]; return b
    def below(self, m: int) -> int:
        # amostragem por rejeição: evita o viés de v % m
        if m <= 1: return 0
        if m <= 256:
            limit = (256 // m) * m
            while True:
                v = self.byte()
                if v < limit: return v % m
        limit = (65536 // m) * m
        while True:
            v = self.byte() << 8 | self.byte()
            if v < limit: return v % m

def _perm_from(ks: '_Keystream') -> list[int]:
    """Fisher-Yates sobre o keystream. p[slot] = célula ocupada pelo slot nesta posição."""
    p = list(range(NCELLS))
    for j in range(NCELLS - 1, 0, -1):
        r = ks.below(j + 1); p[j], p[r] = p[r], p[j]
    return p

def _invert(p: list[int]) -> list[int]:
    inv = [0] * len(p)
    for slot, cell in enumerate(p): inv[cell] = slot
    return inv

def cell_to_coord(cell: int) -> tuple[int, int, int]:
    return (cell // (ROWS * COLS), (cell % (ROWS * COLS)) // COLS, cell % COLS)

def _padme(n: int) -> int:
    """PADMÉ (PURBs, PETS 2019): overhead ≤ ~12%, expõe só O(log log n) bits do tamanho."""
    if n <= 1: return n
    E = n.bit_length() - 1
    S = E.bit_length()
    mask = (1 << (E - S)) - 1
    return (n + mask) & ~mask

def _pad_target(base: int, pad) -> int:
    base = max(base, MIN_FRAME)
    if pad is None:            return base
    if pad == 'padme':         return _padme(base)
    if isinstance(pad, int):   return ((base + pad - 1) // pad) * pad
    raise ValueError("pad inválido: None | 'padme' | inteiro (bloco)")

def _frame(message: str, pad) -> list[int]:
    """[tamanho em 3 símbolos, base 97] + mensagem + padding aleatório."""
    try:
        idx = [SYM2IDX[c] for c in message]
    except KeyError as e:
        raise ValueError(f"caractere fora do charset: {e.args[0]!r}") from None
    L = len(idx)
    if L > MAXLEN: raise ValueError("mensagem longa demais para o prefixo de tamanho")
    core = [(L // (NSYM * NSYM)) % NSYM, (L // NSYM) % NSYM, L % NSYM] + idx
    total = _pad_target(len(core), pad)
    return core + [secrets.randbelow(NSYM) for _ in range(total - len(core))]

def _unframe(sym_idx: list[int]) -> str:
    if len(sym_idx) < 3: raise ValueError("frame curto demais")
    L = sym_idx[0] * NSYM * NSYM + sym_idx[1] * NSYM + sym_idx[2]
    if 3 + L > len(sym_idx): raise ValueError("tamanho declarado inconsistente")
    return ''.join(SYMBOLS[x] for x in sym_idx[3:3 + L])

def encrypt(passphrase: str, message: str, *, seq: int = 0, aad: bytes = b'',
            pad='padme', logN: int = DEFAULT_LOGN, r: int = DEFAULT_R, p: int = DEFAULT_P) -> str:
    if not (0 <= seq < (1 << 64)): raise ValueError("seq fora de 0..2^64-1")
    salt, nonce = os.urandom(SALT_LEN), os.urandom(NONCE_LEN)
    kk = _hkdf(_scrypt(passphrase, salt, logN, r, p), salt, b'cryptomatrix-v2', 64)
    k_stream, k_mac = kk[:32], kk[32:]

    frame = _frame(message, pad)
    ct = bytearray()
    for i, x in enumerate(frame):
        # permutação nova por posição; o homófono de x é escolhido pelo mesmo keystream
        ks = _Keystream(k_stream, nonce, i)
        p_ = _perm_from(ks)
        js = SYM_SLOTS[x]
        ct.append(p_[js[ks.below(len(js))]])

    header = MAGIC + bytes([VERSION, logN, r, p]) + salt + nonce + struct.pack('>Q', seq)
    tag = hmac.new(k_mac, header + bytes(ct) + aad, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(header + bytes(ct) + tag).decode('ascii')

def _parse(token: str):
    raw = base64.urlsafe_b64decode(token.encode('ascii'))
    if len(raw) < HEADER_LEN + TAG_LEN or raw[:4] != MAGIC or raw[4] != VERSION:
        raise ValueError("formato inválido ou versão incompatível")
    logN, r, p = raw[5], raw[6], raw[7]
    o = 8
    salt = raw[o:o+SALT_LEN]; o += SALT_LEN
    nonce = raw[o:o+NONCE_LEN]; o += NONCE_LEN
    seq = struct.unpack('>Q', raw[o:o+SEQ_LEN])[0]; o += SEQ_LEN
    header, ct, tag = raw[:HEADER_LEN], raw[HEADER_LEN:-TAG_LEN], raw[-TAG_LEN:]
    return dict(logN=logN, r=r, p=p, salt=salt, nonce=nonce, seq=seq,
                header=header, ct=ct, tag=tag)

def decrypt(passphrase: str, token: str, *, aad: bytes = b'', guard: 'ReplayGuard | None' = None) -> str:
    f = _parse(token)
    kk = _hkdf(_scrypt(passphrase, f['salt'], f['logN'], f['r'], f['p']), f['salt'],
               b'cryptomatrix-v2', 64)
    k_stream, k_mac = kk[:32], kk[32:]
    expected = hmac.new(k_mac, f['header'] + f['ct'] + aad, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, f['tag']):
        raise ValueError("MAC inválido: ciphertext alterado, AAD errado ou senha incorreta.")
    # seq está no header autenticado, então o replay só é checado depois do MAC
    if guard is not None and not guard.check_and_update(f['seq']):
        raise ValueError(f"replay detectado ou fora da janela (seq={f['seq']}).")
    frame = []
    for i, cell in enumerate(f['ct']):
        # mesma permutação do encrypt; a escolha do homófono não precisa ser refeita
        inv = _invert(_perm_from(_Keystream(k_stream, f['nonce'], i)))
        frame.append(SLOTS[inv[cell]])
    return _unframe(frame)

def read_seq(token: str) -> int:
    return _parse(token)['seq']

class SenderState:
    """Contador de seq do remetente. Precisa ser persistido entre execuções."""
    def __init__(self, start: int = 0): self._next = start
    def next(self) -> int:
        s = self._next; self._next += 1; return s

class ReplayGuard:
    """Janela deslizante anti-replay (como em IPsec/DTLS); o receptor deve persisti-la.

    O bit i de `bits` indica que a seq (top - i) já foi aceita.
    """
    def __init__(self, window: int = 64):
        self.W = window; self.top = -1; self.bits = 0
    def check_and_update(self, seq: int) -> bool:
        if seq < 0: return False
        if self.top < 0:
            self.top, self.bits = seq, 1; return True
        if seq > self.top:
            shift = seq - self.top
            self.bits = ((self.bits << shift) | 1) & ((1 << self.W) - 1) if shift < self.W else 1
            self.top = seq; return True
        offset = self.top - seq
        if offset >= self.W: return False
        if (self.bits >> offset) & 1: return False
        self.bits |= (1 << offset); return True

def render_matrix(passphrase: str, token: str, position: int) -> str:
    """Matriz 3D usada em uma posição do token."""
    f = _parse(token)
    kk = _hkdf(_scrypt(passphrase, f['salt'], f['logN'], f['r'], f['p']), f['salt'],
               b'cryptomatrix-v2', 64)
    p = _perm_from(_Keystream(kk[:32], f['nonce'], position))
    grid = [SYMBOLS[SLOTS[iv]] for iv in _invert(p)]
    lines = [f"— matriz da posição {position} ({DEPTH}x{ROWS}x{COLS}) —"]
    for d in range(DEPTH):
        lines.append(f"camada {d}:")
        for rr in range(ROWS):
            base = d * ROWS * COLS + rr * COLS
            lines.append("  " + " ".join(f"{grid[base+c]:>2}" for c in range(COLS)))
    return "\n".join(lines)

if __name__ == '__main__':
    import argparse, getpass, sys
    ap = argparse.ArgumentParser(description="CryptoMatrix v2.1")
    ap.add_argument('mode', choices=['enc', 'dec', 'demo', 'calibrate'])
    ap.add_argument('-m', '--message'); ap.add_argument('-t', '--token'); ap.add_argument('--seq', type=int, default=0)
    args = ap.parse_args()
    if args.mode == 'calibrate':
        print("logN recomendado (~0.1s):", calibrate_scrypt(0.1)); sys.exit(0)
    if args.mode == 'demo':
        pw = "senha-de-demonstracao"; msg = args.message or "reuniao confidencial as quinze horas."
        tok = encrypt(pw, msg, seq=1)
        print("mensagem :", msg); print("token    :", tok)
        print("seq      :", read_seq(tok)); print("decifrado:", decrypt(pw, tok))
        print(); print(render_matrix(pw, tok, 0)); sys.exit(0)
    pw = getpass.getpass("passphrase: ")
    if args.mode == 'enc':
        print(encrypt(pw, args.message if args.message is not None else sys.stdin.read().rstrip('\n'), seq=args.seq))
    else:
        print(decrypt(pw, args.token if args.token else sys.stdin.read().strip()))
