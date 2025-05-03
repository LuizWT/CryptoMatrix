<h1>CryptoMatrix</h1>
<h3>Sistema de Criptografia por Matriz com Chave Compartilhada</h3>

<div class="section">
  <h3>1. Visão Geral</h3>
  <p>
    Implementa um sistema de criptografia e decriptação baseado em uma matriz 3D determinística de símbolos ASCII imprimíveis.  
    A matriz é gerada a partir de uma <em>passphrase</em> compartilhada, usando SHA‑256 para derivar a SEED e PBKDF2‑HMAC‑SHA256 para proteger a chave de autenticação (MAC).  
    Cada caractere do texto é convertido em coordenadas (camada (dd), linha (rr), coluna (cc)) na matriz.  
  </p>
</div>

<div class="section">
  <h3>2. Dependências e Considerações</h3>
</div>

> [!NOTE]
> Todas as dependências são nativas do Python.

<div lass="section">
  <img src="https://github.com/user-attachments/assets/81f5e4f1-82da-41de-a995-8471bbcaaa9e"></img>
  <br />
  <br />
  <ul>
    <li>
      <strong>Módulos Utilizados:</strong>
      <ul>
        <li><code>secrets</code>, <code>random</code>, <code>string</code>, <code>os</code>, <code>math</code> para geração de números aleatórios, manipulação de terminal e cálculo de dimensões.</li>
        <li><code>hashlib</code>, <code>hmac</code>, <code>hashlib.pbkdf2_hmac</code> — SHA‑256 e PBKDF2 para derivação de chaves e HMAC‑SHA256 para integridade.</li>
      </ul>
    </li>
    <li>
      <strong>Parâmetros Principais:</strong>
      <ul>
        <li><code>PBKDF2_ITERATIONS = 100 000</code>, <code>KEY_LEN = 64</code>, <code>SALT_LEN = 16</code> para configurações de PBKDF2 e tamanho de salt/MAC.</li>
        <li><code>MIN_CELLS = 97</code> (número de símbolos únicos) e <code>MAX_CELLS = 1000</code> — limites para dimensão da matriz.</li>
      </ul>
    </li>
    <li>
      <strong>Conjunto de Símbolos:</strong> 95 símbolos ASCII imprimíveis (incluindo o espaço), com a adição dos caracteres <code>Ç</code> e <code>ç</code>.
    </li>
    <li>
      <strong>Validação de Mensagem:</strong> somente caracteres do conjunto acima são permitidos. Considere ver <code>validate_message()</code>.
    </li>
  </ul>
</div>

<div class="section">
  <h3>3. Explicação Detalhada do Código</h3>

  <h4>3.1 Função <code>derive_matrix_seed</code></h4>
  <img src="https://github.com/user-attachments/assets/1c6de673-ee25-4deb-8a63-73186fc20bb6"></img>
  <br />
  <br />
  <p><strong>Objetivo:</strong> derivar um SEED fixo para geração da matriz a partir da passphrase.</p>
  <ul>
    <li><strong>Entrada:</strong> <code>passphrase: str</code></li>
    <li><strong>Processamento:</strong> SHA‑256 da passphrase (UTF‑8).</li>
    <li><strong>Saída:</strong> <code>matrix_seed: bytes</code> (32 bytes)</li>
  </ul>

  <h4>3.2 Função <code>derive_mac_key</code></h4>
  <img src="https://github.com/user-attachments/assets/d34886e5-fa61-4ad4-af41-6b43028e24ff"></img>
  <br />
  <br />
  <p><strong>Objetivo:</strong> derivar a chave de autenticação (MAC) segura via PBKDF2.</p>
  <ul>
    <li><strong>Entrada:</strong> <code>passphrase: str</code>, <code>salt: bytes</code> (16 bytes)</li>
    <li><strong>Processamento:</strong> PBKDF2‑HMAC‑SHA256 com <code>PBKDF2_ITERATIONS</code> e <code>dklen=KEY_LEN</code>, retorna a metade final dos bytes.</li>
    <li><strong>Saída:</strong> <code>mac_key: bytes</code> (32 bytes)</li>
  </ul>

  <h4>3.3 Função <code>decide_dimensions</code></h4>
  <img src="https://github.com/user-attachments/assets/40c374ea-683a-4794-934b-d03bc507ea9c"></img>
  <br />
  <br />
  <p><strong>Objetivo:</strong> escolher dimensões (depth, rows, cols) para a matriz 3D de modo que <code>MIN_CELLS ≤ depth×rows×cols ≤ MAX_CELLS</code>.</p>
  <ul>
    <li><strong>Entrada:</strong> <code>seed_int: int</code> (inteiro derivado de <code>matrix_seed</code>).</li>
    <li><strong>Processamento:</strong>
      <ol>
        <li>Gera todos os candidatos (d,r,c) dentro dos limites.</li>
        <li>Filtra aqueles com produto ≥ <code>MIN_CELLS</code> e ≤ <code>MAX_CELLS</code>.</li>
        <li>Escolhe aleatoriamente um candidato usando <code>random.seed(seed_int)</code>.</li>
      </ol>
    </li>
    <li><strong>Saída:</strong> tupla <code>(depth, rows, cols)</code></li>
  </ul>

  <h4>3.4 Função <code>generate_matrix</code></h4>
  <img src="https://github.com/user-attachments/assets/bc7cee86-3c88-4a02-8d25-114088cb48c6"></img>
  <br />
  <br />
  <p><strong>Objetivo:</strong> construir a matriz 3D embaralhada de símbolos.</p>
  <ul>
    <li><strong>Entrada:</strong> <code>matrix_seed: bytes</code>, <code>depth, rows, cols: int</code>.</li>
    <li><strong>Processamento:</strong>
      <ol>
        <li>Cria lista inicial <code>ml</code> com todos os <code>SYMBOLS</code>. Se necessário, repete até alcançar <code>depth×rows×cols</code> elementos.</li>
        <li>Trunca <code>ml</code> ao tamanho exato e embaralha determinísticamente usando <code>random.Random(int.from_bytes(matrix_seed))</code>.</li>
        <li>Garante presença de todos os símbolos: substitui duplicatas por símbolos faltantes.</li>
        <li>Converte <code>ml</code> em estrutura 3D: listas de camadas, linhas e colunas.</li>
      </ol>
    </li>
    <li><strong>Saída:</strong> <code>matrix: list[list[list[str]]]</code></li>
  </ul>

  <h4>3.5 Função <code>print_matrix</code></h4>
  <img src="https://github.com/user-attachments/assets/6f04b848-637a-40c3-bbf0-fe9e733940d7"></img>
  <br />
  <br />
  <p><strong>Objetivo:</strong> exibir cada camada da matriz no terminal.</p>
  <ul>
    <li><strong>Entrada:</strong> <code>matrix</code>.</li>
    <li><strong>Processamento:</strong> para cada camada, imprime cabeçalho de colunas e linhas com ANSI colors.</li>
    <li><strong>Saída:</strong> visualização formatada no console.</li>
  </ul>

  <h4>3.6 Função <code>encrypt</code></h4>
  <img src="https://github.com/user-attachments/assets/60d3bf3a-411a-4fdf-96e6-d0da2bdd08d7"></img>
  <br />
  <br />
  <p><strong>Objetivo:</strong> cifrar uma mensagem usando a matriz e gerar tag MAC.</p>
  <ul>
    <li><strong>Entrada:</strong> <code>msg: str</code>, <code>matrix</code>, <code>mac_key</code>.</li>
    <li><strong>Processamento:</strong>
      <ol>
        <li>Mapeia cada símbolo da matriz às suas coordenadas (d,r,c).</li>
        <li>Para cada caractere da mensagem:
          <ul>
            <li>Escolhe coordenada aleatória não usada (pool) e concatena como 6 dígitos (“ddrrcc”).</li>
            <li>Se pool esgotar, reinicializa para manter diversidade.</li>
          </ul>
        </li>
        <li>Guarda <code>default_raw_ct</code> (com zeros) e gera <code>display_ct</code> (com corte de zeros).</li>
        <li>Calcula HMAC‑SHA256 sobre <code>raw</code> com <code>mac_key</code>, produzindo <code>tag</code>.</li>
      </ol>
    </li>
    <li><strong>Saída:</strong> <code>(display_ct: str, tag: str)</code></li>
  </ul>

  <h4>3.7 Função <code>decrypt</code></h4>
  <img src="https://github.com/user-attachments/assets/9ad56602-f16c-4cb5-b592-30671a9d0384"></img>
  <br />
  <br />
  <p><strong>Objetivo:</strong> validar integridade e reconstruir o texto original.</p>
  <ul>
    <li><strong>Entrada:</strong> <code>ct</code> (ignored), <code>tag: str</code>, <code>matrix</code>, <code>mac_key</code>.</li>
    <li><strong>Processamento:</strong>
      <ol>
        <li>Recalcula HMAC sobre <code>default_raw_ct</code> e compara com <code>tag</code>; falha se divergente.</li>
        <li>Divide <code>raw</code> em blocos de 6 dígitos e converte em (d,r,c) para lookup na matriz.</li>
      </ol>
    </li>
    <li><strong>Saída:</strong> mensagem original <code>str</code></li>
  </ul>

  <h4>3.8 Função <code>validate_message</code></h4>
  <img src="https://github.com/user-attachments/assets/7479f7e0-a3cd-405f-a004-7002b9f34b75"></img>
  <br />
  <br />
  <p><strong>Objetivo:</strong> garantir que a mensagem contenha apenas símbolos permitidos.</p>
  <ul>
    <li><strong>Entrada:</strong> <code>msg: str</code></li>
    <li><strong>Processamento:</strong> verifica `all(ch in SYMBOLS)`.</li>
    <li><strong>Saída:</strong> <code>bool</code></li>
  </ul>

  <h4>3.9 Função <code>clear_terminal</code></h4>
  <img src="https://github.com/user-attachments/assets/dbad6048-4b01-4bf7-a3b5-18b165b4f8df"></img>
  <br />
  <br />
  <p><strong>Objetivo:</strong> limpar a tela do terminal.</p>
  <ul>
    <li><strong>Entrada:</strong> nenhuma</li>
    <li><strong>Processamento:</strong> Identifica o sistema operacional e executa o comando apropriado para limpar a tela.</li>
    <li><strong>Saída:</strong> nenhuma</li>
  </ul>

  <h4>3.10 Função <code>main</code></h4>
  <img src="https://github.com/user-attachments/assets/ef87c394-886e-4dc1-939b-5e14307e0d5c"></img>
  <br />
  <br />
  <p><strong>Objetivo:</strong> orquestrar o fluxo de geração da matriz, criptografia e decriptação.</p>
  <ul>
    <li>Solicita passphrase, deriva <code>matrix_seed</code> e <code>mac_key</code>.</li>
    <li>Decide dimensões e gera matriz.</li>
    <li>Loop de input até mensagem válida.</li>
    <li>Chama <code>encrypt</code>, exibe ciphertext, tag e salt.</li>
    <li>Chama <code>decrypt</code> para demonstrar decriptação e exibe resultado.</li>
  </ul>
</div>

<hr />

### Instalação

> [!IMPORTANT]  
> Requer Python 3.6 ou superior para garantir compatibilidade total com os recursos utilizados no código

Clone o repositório:

    git clone https://github.com/seu-usuario/CryptoMatrix.git

Acesse o diretório:

    cd CryptoMatrix/

Execute a ferramenta:

    python3 cryptoMatrix.py
<hr />

## Apoio ao Projeto

Se você quiser contribuir com o projeto, sinta-se à vontade para abrir Issues ou fazer Pull Requests.
  
<hr />

Este projeto está licenciado sob a GNU Affero General Public License v3.0 (Modificada)
