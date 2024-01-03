import os
from langchain.document_loaders import PyPDFLoader,Docx2txtLoader,TextLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap  = 20,
    length_function = len,
    add_start_index = True,
)

class LocalFileLoader:
    def __init__(self):
        pass

    def extract_text_data(self,file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    
    def extract_pdf_data(self,file_path):
        pdf_document = fitz.open(file_path)

        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            text.append(page.get_text("text"))
        pdf_document.close()

        return text
    
    def load_docs(self,dir_path,fields=[]):
         
        """
        Loads a file with unstructured data.
        Supported format:
            1. PDF 
            2. Txt
            3. Docx
        """
        try:
            docs=[]
            if os.path.exists(dir_path):
                for filename in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, filename)

                    if filename.endswith(".pdf"):
                        loader = PyPDFLoader(file_path)
                        docs = docs+loader.load_and_split(text_splitter)
                    elif filename.endswith(".docx"):
                        loader = Docx2txtLoader(file_path)
                        docs = docs+loader.load_and_split(text_splitter)
                    elif filename.endswith(".txt"):
                        loader = TextLoader(file_path)
                        docs = docs+loader.load_and_split(text_splitter)
                    elif filename.endswith(".json"):
                        with open(file_path, 'r', encoding='utf-8') as json_file:
                            json_data = json.load(json_file)
                            if len(fields) ==0:
                                fields = list(x for x in json_data[0].keys())
                            docs=docs+[Document(page_content=str([f"{field}: {str(item[field])}, " for field in fields]).replace("['",'').replace("]'",'')) for item in json_data]
                            print('Done')
            return docs
            
        except Exception as e:
            return "error"+str(e)

