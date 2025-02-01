from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import io
load_dotenv()
def pdf_to_text(upload_file):
    processed_files = []
    text_completed = ""

    # Processar apenas arquivos novos
    for pdfs in upload_file:
        if pdfs.name not in processed_files:
            pdf_reader = PdfReader(io.BytesIO(pdfs.read()))
            pages = len(pdf_reader.pages)

            for page in range(pages):
                page_content = pdf_reader.pages[page].extract_text()
                processed_files.append(pdfs.name)
                text_completed += " ".join(page_content.split("\n"))

    return text_completed
def file_chat(question, model, files=None):
    llm = ChatGoogleGenerativeAI(model=model,temperature=0.9)   
    if files:
        text = pdf_to_text(files)
        char_split = CharacterTextSplitter(chunk_size=2000, chunk_overlap=1000, separator=" ")
        splits = char_split.split_text(text)

        db = FAISS.from_texts(texts=splits, embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-l6-v2"))
        docs = db.similarity_search(question, k=5)

        template = '''Você é um assistente pessoal que responde o usuário em português.
        Você tem acesso a esses documentos: {docs}. Use-os para dar uma resposta completa e didática ao usuário.
        Pergunta: {question}
        Se a pergunta não estiver relacionada aos documentos, responda com "Não tenho acesso a essa informação".
        '''
        
        prompt = PromptTemplate(template=template, input_variables=["question", "docs"])
        chain = prompt | llm
        response = chain.invoke({"docs": docs, "question": question})
        return response.content
#----------------------------------------------------------------