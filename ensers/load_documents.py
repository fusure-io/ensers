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
    
    def load_docs(self,dir_path,unique_id=None):
         
        """
        Loads a file with unstructured data.
        Supported format:
            1. PDF 
            2. Txt
            3. Docx
        """
        try:
            unstructured_docs=[]
            structured_docs=[]
            no_of_unstructured_docs = 0
            no_of_structured_docs = 0

            if os.path.exists(dir_path):
                for filename in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, filename)

                    if filename.endswith(".pdf"):
                        no_of_unstructured_docs+=1
                        loader = PyPDFLoader(file_path)
                        unstructured_docs = unstructured_docs+loader.load_and_split(text_splitter)
                    elif filename.endswith(".docx"):
                        no_of_unstructured_docs+=1
                        loader = Docx2txtLoader(file_path)
                        unstructured_docs = unstructured_docs+loader.load_and_split(text_splitter)
                    elif filename.endswith(".txt"):
                        no_of_unstructured_docs+=1
                        loader = TextLoader(file_path)
                        unstructured_docs = unstructured_docs+loader.load_and_split(text_splitter)

                    elif filename.endswith(".json"):
                        no_of_structured_docs+=1
                        with open(file_path, 'r', encoding='utf-8') as json_file:
                            json_data = json.load(json_file)
                            
                            structured_docs=structured_docs+[Document(page_content=json.dumps(item),
                            metadata={
                                "id":item[unique_id] if unique_id else None,
                                "source":filename,
                                "item_number":idx+1
                            }) for idx,item in enumerate(json_data)]
                            
            return unstructured_docs,structured_docs,no_of_unstructured_docs,no_of_structured_docs
            
        except Exception as e:
            return "error"+str(e)

# b=LocalFileLoader()
# print(json.loads(b.load_docs(dir_path='/workspaces/ensers/test')[1][0].page_content))

