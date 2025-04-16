<h1>CryptoMatrix</h1>
<h3>Sistema de Criptografia por Matriz com Chave Compartilhada</h3>

<div class="section">
  <h3>1. Visão Geral</h3>
  <p>
    Esse código implementa um sistema simples de criptografia e decriptação baseado na geração de uma matriz quadrada embaralhada contendo as letras do alfabeto (com acréscimo da letra <code>"Ç"</code>). A matriz é gerada de forma determinística a partir de uma chave compartilhada, permitindo que tanto a parte que criptografa quanto a parte que descriptografa possam reproduzir exatamente a mesma configuração.
  </p>
  <p>
    Cada caractere da mensagem é representado pela posição (linha e coluna) em que ocorre na matriz. Quando um caractere se repete, uma posição diferente é escolhida para criptografia. Para os espaços, o sistema utiliza tokens especiais: cada token é formado por um prefixo aleatório (qualquer letra de A-Z, exceto <code>Ç</code>) seguido por dois dígitos aleatórios, facilitando sua identificação durante a decriptação.
  </p>
</div>

<div class="section">
  <h3>2. Dependências e Considerações</h3>
  <ul>
    <li>
      <strong>Módulos Utilizados:</strong>
      <ul>
        <li><code>random</code>: Para gerar números aleatórios e embaralhar a lista de caracteres.</li>
        <li><code>string</code>: Para acessar a constante <code>ascii_uppercase</code>, que fornece as letras maiúsculas de A-Z.</li>
      </ul>
    </li>
    <li>
      <strong>Uso da Chave:</strong> A chave fornecida pelo usuário é usada para definir a semente do gerador de números aleatórios (<code>random.seed(key)</code>), garantindo que a matriz gerada seja a mesma para uma mesma chave em processos distintos.
    </li>
    <li>
      <strong>Aplicações Reais:</strong>
      <ul>
        <li>Comunicação segura entre partes que compartilham uma chave secreta.</li>
        <li>Criação de puzzles ou desafios de criptografia.</li>
        <li>Implementações educacionais para introdução aos conceitos de substituição de caracteres e criptografia simétrica com matriz.</li>
      </ul>
    </li>
  </ul>
</div>

<div class="section">
  <h3>3. Explicação Detalhada do Código</h3>

  <h4>3.1 Função <code>generate_matrix</code></h4>
  <pre><code>def generate_matrix(key, size=7):
    alphabet = list(string.ascii_uppercase + "Ç")
    random.seed(key)  # Usa a chave para definir a semente do gerador de números aleatórios
    while len(alphabet) < size * size:
        alphabet += alphabet  # Duplicação da lista para garantir que haja caracteres suficientes para preencher a matriz (total de size*size elementos)
    random.shuffle(alphabet)  # Embaralha a lista de caracteres com base na semente definida
    matrix = [alphabet[i * size:(i + 1) * size] for i in range(size)]  # Divide a lista embaralhada em "size" sublistas
    return matrix</code></pre>
  
  <p><strong>Objetivo e Funcionamento:</strong></p>
  <ul>
    <li>
      <strong>Entrada:</strong> <code>key</code> (chave para definir o estado do gerador aleatório) e <code>size</code> (tamanho da matriz, padrão 7).
    </li>
    <li>
      <strong>Processamento:</strong>
      <ol>
        <li>Cria uma lista contendo as letras de A-Z e a letra <code>"Ç"</code>.</li>
        <li>Define a semente do gerador aleatório com a chave para garantir um embaralhamento determinístico.</li>
        <li>Duplica os elementos da lista se necessário para preencher a matriz.</li>
        <li>Embaralha a lista.</li>
        <li>Divide a lista embaralhada em sublistas de tamanho <code>size</code>.</li>
      </ol>
    </li>
    <li>
      <strong>Saída:</strong> Retorna a matriz gerada (lista de listas representando as linhas da matriz).
    </li>
  </ul>

  <h4>3.2 Função <code>print_matrix</code></h4>
  <pre><code>def print_matrix(matrix):
    for i, row in enumerate(matrix):
        print(f"{i+1}: " + " ".join(row))</code></pre>
  
  <p><strong>Objetivo e Funcionamento:</strong></p>
  <ul>
    <li>
      <strong>Entrada:</strong> <code>matrix</code> (a matriz gerada).
    </li>
    <li>
      <strong>Processamento:</strong> Percorre cada linha da matriz e imprime o número da linha e os caracteres, separados por espaços.
    </li>
    <li>
      <strong>Saída:</strong> Exibição da matriz no console de forma organizada.
    </li>
  </ul>

  <h4>3.3 Função <code>encrypt</code></h4>
  <pre><code>def encrypt(message, matrix):
    encrypted = ""
    # Cria um dicionário com todas as posições disponíveis para cada caractere na matriz.
    positions_full = {}
    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            if cell not in positions_full:
                positions_full[cell] = []
            positions_full[cell].append((i+1, j+1))
    # Cria uma pool para uso durante a criptografia (cópia das posições originais)
    positions_pool = {char: pos_list.copy() for char, pos_list in positions_full.items()}
    for char in message.upper():
        if char == ' ':
            # Para espaços, gera um token: um prefixo aleatório (letra de A-Z) seguido de dois dígitos aleatórios.
            prefix = random.choice(string.ascii_uppercase)
            token = prefix + str(random.randint(11, 77))
            encrypted += token
        else:
            if char in positions_pool:
                # Se a pool de posições para o caractere estiver esgotada, reinicializa-a com as posições originais.
                if not positions_pool[char]:
                    positions_pool[char] = positions_full[char].copy()
                # Seleciona aleatoriamente uma posição da pool e a remove.
                r, c = random.choice(positions_pool[char])
                encrypted += f"{r}{c}"
                positions_pool[char].remove((r, c))
            else:
                # Se o caractere não existir na matriz, adiciona um token padrão "XX".
                encrypted += "XX"
    return encrypted
  </code></pre>
  
  <p><strong>Objetivo e Funcionamento:</strong></p>
  <ul>
    <li>
      <strong>Entrada:</strong> <code>message</code> (mensagem a ser criptografada) e <code>matrix</code>.
    </li>
    <li>
      <strong>Processamento:</strong>
      <ol>
        <li>Inicializa a string <code>encrypted</code>.</li>
        <li>Constrói <code>positions_full</code> mapeando cada caractere da matriz para suas posições (linha, coluna).</li>
        <li>Cria <code>positions_pool</code> como uma cópia de <code>positions_full</code> para gerenciar as posições usadas.</li>
        <li>Para cada caractere da mensagem (em maiúsculas):
          <ul>
            <li>Se for espaço, gera um token com um prefixo aleatório (A-Z) e dois dígitos aleatórios (entre 11 e 77).</li>
            <li>Para outros caracteres, seleciona e remove uma posição aleatória da pool; se esgotada, reinicializa a pool.</li>
          </ul>
        </li>
      </ol>
    </li>
    <li>
      <strong>Saída:</strong> Mensagem criptografada, composta por tokens representando as posições ou espaços.
    </li>
  </ul>

  <h4>3.4 Função <code>decrypt</code></h4>
  <pre>
def decrypt(encrypted_text, matrix):
    decrypted = ""
    i = 0
    while i < len(encrypted_text):
        char = encrypted_text[i]
        # Se o token começa com uma letra (A-Z) e os próximos dois caracteres são dígitos, é um espaço
        if char in string.ascii_uppercase and i + 2 < len(encrypted_text) and encrypted_text[i+1:i+3].isdigit():
            decrypted += ' '
            i += 3
        else:
            token = encrypted_text[i:i+2]
            row = int(token[0]) - 1
            col = int(token[1]) - 1
            decrypted += matrix[row][col]
            i += 2
    return decrypted
  </pre>
  <p><strong>Objetivo e Funcionamento:</strong></p>
  <ul>
    <li><strong>Entrada:</strong> <code>encrypted_text</code>: texto criptografado; <code>matrix</code>: matriz utilizada na criptografia.</li>
    <li><strong>Processamento:</strong>
      <ul>
        <li>Verifica, token por token, se representa um espaço (token de 3 caracteres) ou um caractere da matriz (token de 2 dígitos).</li>
        <li>Converte os tokens de 2 dígitos em índices para recuperar o caractere correspondente da matriz.</li>
      </ul>
    </li>
    <li><strong>Saída:</strong> Retorna a mensagem original descriptografada.</li>
  </ul>

  <h4>3.5 Função <code>main</code></h4>
  <pre>
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
  </pre>
  <p><strong>Objetivo e Funcionamento:</strong></p>
  <ul>
    <li>Solicita a chave e gera a matriz determinística.</li>
    <li>Exibe a matriz e solicita a mensagem a ser criptografada.</li>
    <li>Criptografa a mensagem e exibe o resultado.</li>
    <li>Descriptografa a mensagem e exibe a mensagem original.</li>
    <li>O bloco <code>if __name__ == "__main__":</code> garante que a função <code>main</code> seja executada apenas quando o script for chamado diretamente.</li>
  </ul>
</div>

<div class="section">
  <h3>4. Possíveis Aplicações em Cenários Reais</h3>
  <ul>
    <li><strong>Comunicação Segura:</strong> Permite o envio de mensagens criptografadas entre partes que compartilham uma chave secreta.</li>
    <li><strong>Desafios e Puzzles:</strong> Pode ser adaptado para criar enigmas ou desafios onde os jogadores precisam descobrir a chave para interpretar uma mensagem oculta.</li>
    <li><strong>Ensino:</strong> Ideal para uso didático, introduzindo conceitos de criptografia por substituição e uso de chaves compartilhadas.</li>
  </ul>
</div>

<div class="section">
  <h3>5. Observações Finais</h3>
  <p>
    - A utilização de tokens especiais para espaços, com prefixos aleatórios (de A-Z), torna a mensagem criptografada menos previsível.<br>
    - A reinicialização da pool de posições garante que mensagens com muitas repetições de um mesmo caractere possam ser criptografadas sem perder a diversidade de posições.<br>
  </p>
</div>

### Instalação

> [!IMPORTANT]  
> Requer Python 3.6 ou superior para garantir compatibilidade total com os recursos utilizados no código
Clone o repositório:

    git clone https://github.com/LuizWT/CryptoMatrix.git

Acesse o diretório:

    cd CryptoMatrix/

Execute a ferramenta:

    python3 cryptoMatrix.py
