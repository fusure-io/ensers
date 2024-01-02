import os
from langchain.document_loaders import PyPDFLoader,Docx2txtLoader,TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap  = 20,
    length_function = len,
    add_start_index = True,
)

class LocalLoader:
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
    
    def load_unstructured(self,dir_path):
         
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
            return docs
            
        except Exception as e:
            return "error"+str(e)

    def load_structured(self,dir_path):
        """
        Loads a file with structured data.
        Supported format:Json file with an array of objects
        """
        try:
            if os.path.exists(dir_path):
                for filename in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, filename)
                    if filename.endswith(".json"):
                        with open(file_path, 'r', encoding='utf-8') as json_file:
                            json_data = json.load(json_file)
                            print(json_data)
                            fields = list(x for x in json_data[0].keys())
                            return json_data,fields
        except Exception as e:
            return "error"+str(e)
