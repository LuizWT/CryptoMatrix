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
      <strong>Uso da Chave:</strong> A chave fornecida pelo usuário é usada para definir a SEED do gerador de números aleatórios (<code>random.seed(key)</code>), garantindo que a matriz gerada seja a mesma para uma mesma chave em processos distintos.
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
  <img src="https://github.com/user-attachments/assets/4044dfbf-e091-42ed-ae93-e079350dd065"></img>
  <br>
  <br>
  <p><strong>Objetivo e Funcionamento:</strong></p>
  <ul>
    <li>
      <strong>Entrada:</strong> <code>key</code> (chave para definir o estado do gerador aleatório) e <code>size</code> (tamanho da matriz, padrão 7).
    </li>
    <li>
      <strong>Processamento:</strong>
      <ol>
        <li>Cria uma lista contendo as letras de A-Z e a letra <code>"Ç"</code>.</li>
        <li>Define a SEED do gerador aleatório com a chave para garantir um embaralhamento determinístico.</li>
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
  <img src="https://github.com/user-attachments/assets/815da89a-53bc-4311-b046-661ea9e91e37"></img>
  <br>
  <br>
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
  <img src="https://github.com/user-attachments/assets/e430f69c-c1a6-4a87-aee0-381ed54e0e42"></img>
  <br>
  <br>
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
  <img src="https://github.com/user-attachments/assets/08554779-d3b0-445d-8734-1e40d47ebba9"></img>
  <br>
  <br>
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
  <img src="https://github.com/user-attachments/assets/65bfc2fa-2514-4e14-b96e-a9bee889cde3"></img>
  <br>
  <br>
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
  <ul>
    <li>A utilização de tokens especiais para espaços, com prefixos aleatórios (de A-Z), torna a mensagem criptografada menos previsível.</li>
    <li>A reinicialização da pool de posições garante que mensagens com muitas repetições de um mesmo caractere possam ser criptografadas sem perder a diversidade de posições.</li>
  </ul>
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
<hr>

## Apoio ao Projeto

Se você quiser contribuir com o projeto, sinta-se à vontade para abrir Issues ou fazer Pull Requests.
  
<hr>

Este projeto está licenciado sob a GNU Affero General Public License v3.0 (Modificada)
