from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

loader = CSVLoader(file_path="faq.csv")
documents = loader.load()

print(len(documents))

embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY')
db = FAISS.from_documents(documents, embeddings)

def retrieve_info(query):
    similar_response = db.similarity_search(query, k=3)

    page_contents_array = [doc.page_content for doc in similar_response]
    return page_contents_array

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613" , openai_api_key=os.getenv('OPENAI_API_KEY)

template = """
You are a nurse working as a consultant to patients. 
I will share a query with you that the patients ask and you will give me the best answer that 
I should send to this patients based on the given documents., 
and you will follow ALL of the rules below:

1/ Response should be very similar or even identical to the documents in the database., 
in terms of length, ton of voice, logical arguments and other details

2/ If the best response are irrelevant, then try to mimic the style of the best answer to the query

Below is a message I received from the patient:
{message}

Here is a list of best practies of how we normally respond to patient in similar scenarios:
{best_practice}

Please write the best response that I should send to this pateint based on the given documents.:
"""

prompt = PromptTemplate(
    input_variables=["message", "best_practice"],
    template=template
)

chain = LLMChain(llm=llm, prompt=prompt)


def generate_response(message):
    best_practice = retrieve_info(message)
    response = chain.run(message=message, best_practice=best_practice)
    return response


message = """bache ko bolte waqt dard hota hai"""
response = generate_response(message)
print(response)

def main():
    st.set_page_config(
        page_title="Nurses response generator", page_icon=":bird:")

    st.header("Nurses response generator :bird:")
    message = st.text_area("patient message")

    if message:
        st.write("Generating best medical response message...")

        result = generate_response(message)

        st.info(result)


if __name__ == '__main__':
    main()

