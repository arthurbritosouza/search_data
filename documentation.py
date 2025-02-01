from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.memory import ConversationSummaryMemory
from langchain.prompts import PromptTemplate
from langchain_core.runnables import chain
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import os

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

memory = ConversationSummaryMemory(llm=llm)
history_messages = memory.chat_memory.messages
SaveDocTopic = []
keys_valeu = {}

@chain
def extract_keyword(inputs):
    question = inputs["question"]
    llm = inputs["llm"]

    # Traduz a pergunta para inglês
    prompt_translate = PromptTemplate(
        input_variables=["question"],
        template="Traduza a seguinte frase para inglês: {question}. Apenas me retorne a frase em inglês."
    )
    chain_translate = prompt_translate | llm
    translated_question = chain_translate.invoke({"question": question}).content
    print("Texto traduzido:", translated_question)

    # Extrai a palavra-chave do texto traduzido
    prompt_template = PromptTemplate(
        input_variables=["question"],
        template='''Extraia apenas a palavra-chave da seguinte frase: {question}.
        Apenas retorne uma palavra-chave mais relevante. Exemplo: "How do I create an agent in langchain?" Keyword: agent'''
    )
    chain_keyword = prompt_template | llm
    keyword = chain_keyword.invoke({"question": translated_question}).content
    print("Palavra-chave extraída:", keyword)

    return {"keyword": keyword}

@chain
def search_link(inputs):
    url_doc = keys_valeu["url_doc"]
    keyword = inputs["keyword"]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    url = requests.get(url_doc, headers=headers)
    resposta = url.text
    soup = BeautifulSoup(resposta, 'html.parser')
    links = soup.find_all('a', href=True)
    link_href = [link['href'] for link in links]

    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = InMemoryVectorStore.from_texts(texts=link_href,embedding=embedding_model)
    retriever = vectorstore.as_retriever(search_type="mmr", k=1)
    # Buscando a URL mais relevante para a palavra-chave
    
    result = retriever.invoke(keyword)

    if result:
        result_page = result[0].page_content  # Obtendo o link da melhor correspondência
        print("Página encontrada:", result_page)
        return {"url_keyword": result_page}
    else:
        print("Nenhuma correspondência encontrada para o termo:", keyword)
        return None

def request_url(url_keyword, url_doc):
    '''Tenta diferentes formas de formar a url a url valida'''

    #? Pega o último elemento da url da documentação pega pela vector store
    final = url_keyword.split("/")[-1]
    print("Final:", final)

    #?0 - Primeira tentativa: Usa a url extraida da documentação tirando o ultimo paramêtro da url
    #?1 - Segunda tentativa: Adiciona '/' antes do 'final' da url extraida da documentação
    #?2 - Terceira tentativa: Sem adicionar '/' antes do 'final'
    #?4 - Quarta tentativa: Retira o ultimo elemento da url,e adiciona o final da url retirada da documentação
    attempts = [ '/'.join(url_doc.split('/')[:-1]) + '/' + url_keyword,'/'.join(url_doc.split('/')) + '/' + final,'/'.join(url_doc.split('/')) + final,'/'.join(url_doc.split('/')[:-1]) + '/' + final]
    print("Tentativas:", attempts)
    for attempt in attempts:
        print(f"Tentando acessar: {attempt}")
        get_request = requests.get(attempt)

        if get_request.status_code == 200:
            print("200 - URL válida encontrada!")
            return attempt
        else:
            print("Erro - URL inválida")

@chain
def get_url(inputs):
    '''Pegando a url para a verificação'''
    url_doc = keys_valeu["url_doc"]
    url_keyword = inputs["url_keyword"]


    url_function = request_url(url_keyword, url_doc)
    if url_function:
        return {"url_function": url_function}
    else:
        return {"url_function": url_doc}

@chain
def get_data(inputs):
    '''Extrai o texto da documentação e usa para responder a pergunta.'''

    # Truncar o histórico para evitar crescimento excessivo
    if len(history_messages) > 10:
        memory.chat_memory.messages = memory.chat_memory.messages[-10:]

    history = "\n".join([f"{msg.type.capitalize()}: {msg.content}" for msg in memory.chat_memory.messages])

    url = inputs["url_function"]
    question = keys_valeu["question"]
    llm = keys_valeu["llm"]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    text_content = soup.get_text()

    # Limitar o crescimento de SaveDocTopic
    if len(SaveDocTopic) > 5:
        SaveDocTopic.pop(0)
    SaveDocTopic.append(text_content)

    template = '''
         Você tem acesso total à informação da documentação {text}.
         Use todos os dados ao seu alcance sobre a biblioteca para responder à pergunta.
         Histórico: {history}
         Pergunta: {question}
         No final da resposta sempre mostre um exemplo didático com um código de exemplo bem estruturado, com comentários explicativos.
         '''
    prompt = PromptTemplate(template=template, input_variables=['text', 'question', 'history'])
    chain = prompt | llm
    response = chain.invoke({"text": text_content, "question": question, 'history': history})
    print(response.content)
    return response.content

def run_search(url_doc, model, question):
    llm = ChatGoogleGenerativeAI(model=model,google_api_key=api_key)
    combined_functions = extract_keyword | search_link | get_url | get_data
    inputs = {
        "url_doc": url_doc,
        "llm": llm,
        "question": question
    }
    keys_valeu.update(inputs)
    response = combined_functions.invoke(inputs)
    return response

def chat(user_input, model):
    history = "\n".join([f"{msg.type.capitalize()}: {msg.content}" for msg in memory.chat_memory.messages])
    template = ''' 
    Responda o Usuário, caso seja sobre o assunto que tem os documentos e está no seu histórico, responda com base nessas informações.
    Histórico: {history}
    Documentos: {SaveDocTopic}
    Usuário: {user_input}
    '''
    prompt = PromptTemplate(input_variables=["history", "user_input", "SaveDocTopic"], template=template)
    llm = ChatGoogleGenerativeAI(model=model,google_api_key=api_key)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"user_input": user_input, "history": history, "SaveDocTopic": SaveDocTopic})

def classify_input(user_input, model):
    llm = ChatGoogleGenerativeAI(model=model,google_api_key=api_key)
    template = '''
        Classifique o seguinte input do usuário como "documentação" ou "conversa".
        - Se o input mencionar tópicos técnicos ou palavras-chave da documentação, como "Como faço para...", classifique como "documentação".
        - Caso contrário, classifique como "conversa".
        Apenas responda com uma destas palavras: "documentação" ou "conversa".
        Input: {user_input}
    '''
    prompt = PromptTemplate(input_variables=["user_input"], template=template)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"user_input": user_input})
    return response

def main(url_documentation, model, user_input):
    response = classify_input(user_input, model)
    if response == "documentação":
        print("Documentação")
        return run_search(url_documentation, model, user_input)
    elif response == "conversa":
        print("Conversa")   
        return chat(user_input, model)


main("https://laravel.com/docs/11.x/readme","gemini-2.0-flash-exp","Como faço uma rota??")
# main("https://www.crummy.com/software/BeautifulSoup/bs4/doc/#","gemini-2.0-flash-exp","O que o beatiful soup faz?")
# main("https://python.langchain.com/api_reference/index.html","gemini-2.0-flash-exp","O que é um agents? ?")
# main("https://pandas.pydata.org/docs/reference/frame.html","gemini-2.0-flash-exp","o que é um memory usage? ")
########NÃO FUNCIONANDO
# main("https://python.langchain.com/api_reference/core/runnables.html","gemini-1.5-flash","como faço uma RunnableSequence?")
# main("https://python.langchain.com/api_reference/core/runnables.html","gemini-2.0-flash-exp","como faço uma RunnableSequence?")
# main("https://huggingface.co/transformers/v3.0.2/index.html","gemini-2.0-flash-exp","O que são models?")