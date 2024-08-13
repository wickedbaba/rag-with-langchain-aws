import uuid
from psycopg2 import connect
from lib.support import s3_support
from lib.support.git_repo_support import get_repo_content_from_s3


import boto3, os, json, traceback
import langchain

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain_community.vectorstores.pgvector import PGVector

from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings

from langchain_community.document_loaders import TextLoader

from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnableParallel, RunnablePassthrough



class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}

class DirectContentLoader:
    def __init__(self, content):
        self.content = content

    def load(self):
        return [Document(self.content)]

def convert_to_chunks(content):
    try:
        loader = DirectContentLoader(content)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)
        
        return chunks
    except Exception as e:
        traceback.print_exc()
        print("Getting error in convert_to_chunks",e)

def convert_to_embeddings(chunks,existing_store=None):
    try:
        bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-west-2')
        bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", client=bedrock_client)

        if existing_store is None:
            vector_store = FAISS.from_documents(chunks, bedrock_embeddings)
        else:
            vector_store = existing_store
            vector_store.add_documents(chunks)

        return vector_store
    except Exception as e:
        traceback.print_exc()
        print("Getting error in convert_to_embeddings",e)


def process_document(content):
    try:
        vector_store = None
        for context_i in content:
            # print(context_i)
            chunks = convert_to_chunks(context_i)
            vector_store = convert_to_embeddings(chunks, vector_store)

        return vector_store
    except Exception as e:
        traceback.print_exc()
        print("Getting error in process_document",e)

def content_parser(content):

    net_context = ""
    code_file_extensions = ['.py', '.cpp', '.js', '.html', '.css', '.java', '.rb', '.go', '.ts', '.php', 
                            '.txt', '.cfg', '.ini', '.yml', '.yaml', '.json', '.xml', '.toml']
    
    for key, value in content.items():
        if any(key.lower().endswith(extension) for extension in code_file_extensions):
            net_context += f"{value}"
    
    return net_context

def initiate_session(payload):
    session_id = str(uuid.uuid4())
    content = get_repo_content_from_s3(payload['repo_name'], payload['branch'])
    str_content = content_parser(content)

    export_context_from_s3(session_id, [str_content])
    return {"session_id": session_id}


def execute(payload):

    try:

        # -----------------------User Defined Input---------------------------------------------------------------
        content = get_context_from_s3(payload)
            
        # user_question = "How to make a good readme?" 
        user_question = payload['user_input']


        # -----------------------Pre-Defined Input---------------------------------------------------------------

        # TODO: refine the template here
        template = """
        instruction: "You are an AI assistant that helps with code analysis, debugging, and optimization. Based on the provided context, answer user questions about finding errors, understanding the logic, or suggesting improvements.",
        Note: "You will get a Python-based codebase at the beginning of the context, followed by series of questions and answers between you and the user ",

        formatting_guidelines: "Please provide a detailed analysis of the user query, along with suggestions if required. Include code snippets if necessary.",
        constraints: "The solution should be efficient and consider the current architecture of the system. Avoid suggesting major refactoring unless absolutely necessary."

        content: {content}

        user_question: {user_question}
        """

        template_1 = """
        instruction: "You are an AI assistant specialized in code generation and optimization. Based on the provided context, generate precise and efficient code snippets to address the user's query.",
        Note: "You will receive a Python-based codebase at the beginning of the context, followed by a series of questions and answers between you and the user.",

        formatting_guidelines: "Ensure the code is well-commented and follows best practices. Provide explanations for any complex logic.",
        constraints: "The generated code should be compatible with the existing system architecture and avoid unnecessary dependencies."

        content: {content}

        user_question: {user_question}
        """

        template_2 = """
        instruction: "You are an AI assistant focused on code refactoring and enhancement. Based on the provided context, suggest improvements and optimizations to the user's code.",
        Note: "You will receive a Python-based codebase at the beginning of the context, followed by a series of questions and answers between you and the user.",

        formatting_guidelines: "Provide clear and concise code improvements. Include comments to explain the changes and their benefits.",
        constraints: "Ensure the refactored code maintains the original functionality and integrates seamlessly with the existing codebase."

        content: {content}

        user_question: {user_question}
        """

        template_3 = """
        instruction: "You are an AI assistant with expertise in debugging and troubleshooting. Based on the provided context, identify and fix errors in the user's code.",
        Note: "You will receive a Python-based codebase at the beginning of the context, followed by a series of questions and answers between you and the user.",

        formatting_guidelines: "Highlight the errors and provide corrected code snippets. Include explanations for the fixes and any potential side effects.",
        constraints: "Ensure the fixes are efficient and do not introduce new issues. Maintain the overall structure and logic of the original code."

        content: {content}

        user_question: {user_question}
        """

        prompt = ChatPromptTemplate.from_template(template)
        parser = StrOutputParser()

        # -----------------------------Model Initialization---------------------------------------------------------
        
        model_name = "anthropic.claude-3-sonnet-20240229-v1:0"
        print("Accessing Model")
        bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-west-2')
        model = ChatBedrock(model_id=model_name, model_kwargs={"temperature": 0.1}, client=bedrock_client)

        # ---------------------------Function Calls-----------------------------------------------------------

        print("Processing document...")
        vector_store = process_document(content)

        # chunks = convert_to_chunks(content)
        # print(chunks)
        # print("Setting up vector store... \n\n\n\n")
        # vector_store = convert_to_embeddings(chunks)

  
        chain = (
            {"content": vector_store.as_retriever(), "user_question": RunnablePassthrough()}
            | prompt
            | model
            | parser
        )
        
        print("Generating answer...")
        response = chain.invoke(user_question)
        print(f"\n\n\nAnswer: {response}")



   

        # TODO - change input and output fields
        content.append(str({
                "user_input": user_question,
                "assistant_response": response
            }))
        session_id = payload['session_id']
        export_context_from_s3(session_id, content)

        return  response
        # while True:
        #     user_question = input("\nEnter your question (or 'quit' to exit): ")
        #     if user_question.lower() == 'quit':
        #         break

        #     print("Generating answer...")
        #     response = chain.invoke(user_question)
        #     print(f"\nAnswer: {response}")
    except Exception as e: 
        traceback.print_exc()
        print("Getting error in main.py",e)

def get_context_from_s3(payload):
    s3_key = f"session_data/{payload['session_id']}/context.json"
    context = s3_support.read_json_from_s3(os.environ['REPO_EXPORT_BUCKET'], s3_key)
    return context

def export_context_from_s3(session_id, context):
    s3_key = f"session_data/{session_id}/context.json"
    s3_support.write_json_to_s3(context, os.environ['REPO_EXPORT_BUCKET'], s3_key)
    return True
