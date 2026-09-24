# CryptoMatrix

Cada caractere de uma mensagem é convertido nas coordenadas `(camada, linha, coluna)` de uma célula em uma matriz 3D de símbolos. A matriz é **permutada de novo a cada posição** a partir de um *keystream* derivado da *passphrase*, então o mesmo símbolo cai em coordenadas diferentes ao longo do texto.

> [!WARNING]
> CryptoMatrix é um **projeto de estudo** e uma **construção própria, sem revisão externa/formal**. Para proteger dados sensíveis de verdade, prefira uma AEAD padrão (ChaCha20-Poly1305 ou AES-GCM) de uma biblioteca consagrada como a [`cryptography`](https://cryptography.io).

---

## Sumário

- [Visão geral](#visão-geral)
- [Como funciona](#como-funciona)
- [Propriedades de segurança](#propriedades-de-segurança)
- [Conjunto de símbolos](#conjunto-de-símbolos)
- [Requisitos e instalação](#requisitos-e-instalação)
- [Uso](#uso)
- [Testes](#testes)
- [Limitações](#limitações)
- [Licença](#licença)

---

## Visão geral

A ideia central é representar cada símbolo por **coordenadas** em uma matriz 3D em vez de por um valor fixo. Um símbolo pode ocupar mais de uma célula (**homofonia**), e a matriz não é fixa: a cada caractere da mensagem uma permutação nova das células é derivada de um *keystream*. Isso torna o esquema equivalente a uma cifra de fluxo — não existe um mapa fixo símbolo→coordenada que um atacante possa recuperar por análise de frequência.

O ciphertext é autenticado, o comprimento da mensagem é ocultado por *padding*, e há proteção contra repetição (*replay*).

## Como funciona

```
passphrase
   │  scrypt(salt)                     derivação lenta e com salt
   ▼
master key ── HKDF ──► k_stream (cifra)   +   k_mac (autenticação)
   │
   │  para cada posição i da mensagem:
   │     keystream(k_stream, nonce, i) gera uma PERMUTAÇÃO nova das células
   │     o símbolo é escrito na coordenada correspondente nessa matriz
   ▼
token = base64url( cabeçalho | ciphertext | HMAC-SHA256 )
        cabeçalho = MAGIC | versão | params do scrypt | salt | nonce | seq
```

## Propriedades de segurança

| Propriedade | Mecanismo |
|---|---|
| Confidencialidade | matriz permutada por posição via *keystream* `HMAC-SHA256` (modo contador) |
| Derivação de chave | `scrypt` com *salt* (memória-dura); parâmetros de custo gravados no token |
| Separação de chaves | `HKDF-SHA256` deriva chaves distintas para cifra e MAC |
| Integridade | `HMAC-SHA256` *encrypt-then-MAC* sobre cabeçalho + ciphertext + AAD |
| Independência entre mensagens | *nonce* aleatório por mensagem |
| Sigilo de tamanho | *padding* PADMÉ (esconde o comprimento exato) |
| Anti-replay | contador `seq` autenticado + `ReplayGuard` (janela deslizante) no receptor |

## Conjunto de símbolos

97 símbolos: `A–Z` + `Ç`, espaço, `0–9`, `a–z` + `ç`, e a pontuação ASCII. Letras acentuadas além de `ç`/`Ç` (como `á`, `é`) **não** fazem parte do conjunto; mensagens com caracteres fora dele são rejeitadas com `ValueError`.

## Requisitos e instalação

> [!NOTE]
> Somente biblioteca padrão do Python. Nenhuma dependência externa.

Requer **Python 3.8+** (usa `hashlib.scrypt`).

```bash
git clone https://github.com/LuizWT/CryptoMatrix.git
cd CryptoMatrix
```

## Uso

### Linha de comando

```bash
# demonstração: cifra, decifra e mostra a matriz da 1ª posição
python3 cryptomatrix.py demo

# calibra o custo do scrypt para ~0,1 s nesta máquina
python3 cryptomatrix.py calibrate

# cifrar / decifrar (a senha é pedida sem exibir)
python3 cryptomatrix.py enc -m "reuniao as quinze horas" --seq 1
python3 cryptomatrix.py dec -t "<token>"
```

### Como biblioteca

```python
import cryptomatrix as cm

# remetente — persista o contador entre execuções
snd = cm.SenderState(start=0)
token = cm.encrypt("senha-forte", "transferir 500 para a conta 42", seq=snd.next())

# receptor — persista a ReplayGuard por sessão/remetente
guard = cm.ReplayGuard(window=64)
msg = cm.decrypt("senha-forte", token, guard=guard)
# levanta ValueError em senha errada, token adulterado ou replay
```

## Testes

```bash
python3 test_cryptomatrix.py
```

Cobre correção (`decrypt(encrypt(m)) == m`), integridade, sigilo de tamanho, anti-replay e uma bateria de ataques (análise de frequência, texto conhecido, reuso de chave), demonstrando que não recuperam o plaintext.

## Limitações

- Construção própria, **sem revisão externa/formal**.
- O *padding* esconde o tamanho exato, mas não o **tamanho aproximado** (quantizado).
- `SenderState` e `ReplayGuard` precisam ser **persistidos** pelo chamador; sem isso, não há garantia anti-replay.
- Implementação didática em Python puro — não é *hardened* contra ataques de canal lateral (*timing*, etc.).

## Licença

GNU Affero General Public License v3.0 (Modificada). Veja [`LICENSE`](LICENSE).

## Contribuição

Issues e Pull Requests são bem-vindos.
