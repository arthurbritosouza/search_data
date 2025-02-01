from chat_file import file_chat
from documentation import main
import streamlit as st


st.header("📚 Seach Data", anchor="top")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

if "file" not in st.session_state:
    st.session_state.file = []

if "url_documentation" not in st.session_state:
    st.session_state.url_documentation = ""

   
with st.sidebar:
    model_options = [
        {"label": "Flash 2.0", "value": "gemini-2.0-flash-exp"},
        {"label": "Gemini 1.5 Pro", "value": "gemini-1.5-pro"},
        {"label": "Gemini 1.5 Flash", "value": "gemini-1.5-flash"},
        {"label": "Gemini 1.5 Flash-8B", "value": "gemini-1.5-flash-8b"},
    ]

    model_selectbox = st.selectbox("Selecione um modelo:", [opcao["label"] for opcao in model_options])
    model = next(opcao["value"] for opcao in model_options if opcao["label"] == model_selectbox)

    # Opções de entrada de dados
    options_data = [
        {"label": "Arquivos", "value": "arquivos"},
        {"label": "Documentação", "value": "documentacao"},
    ]

    option_selectbox = st.selectbox("Selecione o modo de operação:", [opcao["label"] for opcao in options_data])
    option = next(opcao["value"] for opcao in options_data if opcao["label"] == option_selectbox)

    def handle_file_upload():
        uploaded_files = st.sidebar.file_uploader("Faça upload dos seus arquivos:", type=["pdf", "docx", "txt", "md", "html"], accept_multiple_files=True)
        if uploaded_files:
            st.session_state.file = uploaded_files
            st.write("Arquivos carregados:")
            for file in st.session_state.file:
                st.write(file.name)

if option == "arquivos":
    handle_file_upload()
    
elif option == "documentacao":
    link_docss = st.session_state.url_documentation = st.sidebar.text_input("Insira o link para a documentação:")
    if link_docss:
        st.write(link_docss)

def exibir_chat():
    for mensagem in st.session_state.mensagens:
        chat_message = st.chat_message(mensagem["role"])
        chat_message.markdown(mensagem["content"])

st.divider()

question = st.chat_input("Diga algo para o chatbot...")
if question:
    st.session_state.mensagens.append({"role": "user", "content": question})

    if st.session_state.file:
        response = file_chat(question, model, st.session_state.file)
        
    elif st.session_state.url_documentation:
        response = main(st.session_state.url_documentation, model, question)

    st.session_state.mensagens.append({"role": "assistant", "content": response})

exibir_chat()
