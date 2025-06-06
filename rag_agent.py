import os
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter

from config import VECTORSTORE_DIR  # Assuming VECTORSTORE_DIR set here
from utils import load_document, extract_base64_image

# Load env variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)

def add_to_vectorstore(text: str):
    splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    vectorstore = FAISS.from_texts(chunks, embedding)
    vectorstore.save_local(VECTORSTORE_DIR)

def classify_file_with_llm(file_path: str, uploaded_by: str):
    text = ""
    base64_image_url = None

    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".jpg", ".jpeg", ".png"]:
        base64_image_url = extract_base64_image(file_path)
    else:
        docs = load_document(file_path)
        text = "\n\n".join([doc.page_content for doc in docs])

    if text:
        add_to_vectorstore(text)

    today = datetime.now().strftime("%d-%b-%Y")

    system_prompt = (
        "You are a multimodal assistant. Given the document (text and/or image), "
        "classify it into one of these categories: [Home, Finance, Family, Entertainment, Health, Lifestyle].\n\n"
        "Return exactly in this format:\n"
        "Category: <category>\n"
        "Tag: <short tag>\n"
        f"Uploaded By: {uploaded_by}\n"
        f"Date Uploaded: {today}"
    )

    user_content = []
    if text:
        user_content.append({"type": "text", "text": text[:1500]})
    if base64_image_url:
        user_content.append({"type": "image_url", "image_url": {"url": base64_image_url}})

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ])

    return response.content.strip()
