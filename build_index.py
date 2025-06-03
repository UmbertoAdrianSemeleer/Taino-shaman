import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Load PDF and extract text ===
def load_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# === Split into chunks ===
def split_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_text(text)

# === Build vector DB ===
if __name__ == "__main__":
    print("Building vector DB...")
    text = load_pdf_text("taino_book.pdf")  # Change to your actual file name
    chunks = split_text(text)

    embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectorstore = FAISS.from_texts(chunks, embedding)
    vectorstore.save_local("shaman_index")
    print("Vector DB saved as 'shaman_index'")
