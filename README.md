<html>
  <h1>Projeto Assistente de Documentação e Arquivos</h1>
  <p>Este projeto é uma aplicação <strong>Streamlit</strong> que oferece duas funcionalidades principais:</p>
  <ul>
    <li>
      <strong>Interação com Arquivos</strong><br>
      Permite ao usuário fazer perguntas sobre dados presentes em arquivos (PDF, CSV, TXT, entre outros). O sistema extrai o conteúdo dos arquivos, realiza a indexação e, a partir de consultas do usuário, retorna respostas completas e didáticas baseadas nas informações contidas nesses documentos.
    </li>
    <li>
      <strong>Pesquisa e Consulta em Documentação</strong><br>
      Recebe uma URL de uma documentação, extrai todos os links presentes na página e, ao receber uma pergunta do usuário, identifica uma palavra-chave (como "agents", "routing", etc). Com base nessa palavra-chave, o sistema encontra o link correspondente ao tópico da documentação, extrai o conteúdo completo da página e utiliza esse contexto para responder à pergunta com relevância máxima.
    </li>
  </ul>

  <h2>Funcionalidades</h2>
  <ul>
    <li><strong>Integração com múltiplos formatos de arquivo:</strong> Suporte para PDF, CSV, TXT, entre outros.</li>
    <li><strong>Busca inteligente na documentação:</strong> Extração de links, indexação com FAISS e HuggingFaceEmbeddings, e identificação de palavras-chave para mapear o tópico da documentação.</li>
    <li><strong>Histórico e Memória de Conversação:</strong> Utiliza ConversationSummaryMemory para manter o contexto e histórico das interações.</li>
    <li><strong>Integração com modelos de linguagem:</strong> Utiliza ChatGoogleGenerativeAI para processar e gerar respostas.</li>
  </ul>

  <h2>Tecnologias Utilizadas</h2>
  <ul>
    <li><strong>Linguagens e Frameworks:</strong> Python, Streamlit</li>
    <li><strong>Bibliotecas e Ferramentas:</strong> LangChain, BeautifulSoup, Requests, FAISS, HuggingFaceEmbeddings, PyPDF2, Dotenv</li>
  </ul>

  <h2>Instalação</h2>
  <h3>Pré-requisitos</h3>
  <ul>
    <li>Python 3.8 ou superior</li>
    <li>Git</li>
    <li>Docker (opcional, para instalação via contêiner)</li>
  </ul>
  <h3>Passo a Passo</h3>
  <ol>
    <li>
      <strong>Clone o repositório:</strong>
      <pre>git clone https://github.com/arthurbritosouza/search_data.git
cd nome-do-repositorio</pre>
    </li>
    <li>
      <strong>Crie e ative um ambiente virtual (recomendado):</strong>
      <pre>python -m venv venv
source venv/bin/activate   # No Linux/Mac
venv\Scripts\activate      # No Windows</pre>
    </li>
    <li>
      <strong>Instale as dependências:</strong>
      <pre>pip install -r requirements.txt</pre>
    </li>
    <li>
      <strong>Configure as variáveis de ambiente:</strong> Crie um arquivo <code>.env</code> na raiz do projeto e adicione as variáveis necessárias (ex: chaves de API, configurações de modelo).
    </li>
    <li>
      <strong>Execute a aplicação:</strong>
      <pre>streamlit run main.py</pre>
    </li>
  </ol>

  <h2>Uso com Docker</h2>
  <ol>
      <strong>Pull da Imagem:</strong>
      <pre>docker pull britoarthur855482/documentation_ai:01
        
docker run -d -p 8501:8501 --name documentation_ai_container britoarthur855482/documentation_ai:01
</pre>
    </li>
  </ol>

</html>