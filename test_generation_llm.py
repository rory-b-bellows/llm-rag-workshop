
import json
import os
from elasticsearch import Elasticsearch
from shuttleai import *

def retrieve_documents(query, index_name="course-questions", max_results=5):
    es = Elasticsearch("http://localhost:9200")
    
    search_query = {
        "size": max_results,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "data-engineering-zoomcamp"
                    }
                }
            }
        }
    }
    
    response = es.search(index=index_name, body=search_query)
    documents = [hit['_source'] for hit in response['hits']['hits']]
    return documents

def build_context(documents):
    context = ""

    for doc in documents:
        doc_str = f"Section: {doc['section']}\nQuestion: {doc['question']}\nAnswer: {doc['text']}\n\n"
        context += doc_str
    
    context = context.strip()
    return context


def build_prompt(user_question, documents):
    context = build_context(documents)
    return f"""
    You're a course teaching assistant.
    Answer the user QUESTION based on CONTEXT - the documents retrieved from our FAQ database.
    Don't use other information outside of the provided CONTEXT.  

    QUESTION: {user_question}

    CONTEXT:

    {context}
    """.strip()

# def ask_openai(prompt, model="gpt-3.5-turbo"):
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     answer = response.choices[0].message.content
#     return answer

def ask_shuttleai(prompt, model='gpt-3.5-turbo-0125',temperature=0):
    response = shuttle.chat_completion(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        # tools=tools,
        # tool_choice="auto"
    )
    # print(response)
    answer = response['choices'][0]['message']['content']
    # answer = response.choices[0].message.content
    return answer

def qa_bot(user_question):
    context_docs = retrieve_documents(user_question)
    prompt = build_prompt(user_question, context_docs)
    # answer = ask_openai(prompt)
    answer = ask_shuttleai(prompt)
    return answer


if __name__ == '__main__':
    from dotenv import load_dotenv

    SHUTTLE_KEY = os.getenv('SHUTTLE_AI_API_KEY')
    shuttle = ShuttleClient(SHUTTLE_KEY)

    list_user_questions = [
        "I'm getting invalid reference format: repository name must be lowercase",
        "I can't connect to postgres port 5432, my password doesn't work",
        "how can I run kafka?",
    ]
    for user_question in list_user_questions:
        print(f"QUESTION: {user_question}\n")
        answer = qa_bot(user_question)
        print(answer)
        print("\n")
   
    # response = shuttle.chat_completion(
    #     model="gpt-3.5-turbo-0125",
    #     messages=[{"role": "user", "content": "Could you summarize Shakespeare's A Midsummer Night's Dream"}],
    #     # temperature=0,
    #     # tools=tools,
    #     # tool_choice="auto"
    # )
    # print(response)

    # user_question = "How do I join the course after it has started?"
    # # user_question = "What's the plot of Harry Potter's first book?"

    # context_docs = retrieve_documents(user_question)

    # context = ""

    # for doc in context_docs:
    #     doc_str = f"Section: {doc['section']}\nQuestion: {doc['question']}\nAnswer: {doc['text']}\n\n"
    #     context += doc_str

    # context = context.strip()
    # # print(context)

    # prompt = f"""
    # You're a course teaching assistant. Answer the user QUESTION based on CONTEXT - the documents retrieved from our FAQ database. 
    # Only use the facts from the CONTEXT. If the CONTEXT doesn't contan the answer, return "NONE"

    # QUESTION: {user_question}

    # CONTEXT:

    # {context}
    # """.strip()

    # response = shuttle.chat_completion(
    #     model="gpt-3.5-turbo-0125",
    #     messages=[{"role": "user", "content": prompt}],
    #     # temperature=0,
    #     # tools=tools,
    #     # tool_choice="auto"
    # )
    # print(response)