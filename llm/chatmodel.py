from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableParallel,RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from models.pymodel import ChatRequest
from retriver.fas import get_vector_store
load_dotenv()
model = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
)

async def get_response(req:ChatRequest,chatfileloc:str):
    vector_store = get_vector_store(chatfileloc)
    retriver = vector_store.as_retriever(search_kwargs={"k":20})
    print(f"successfully getting the retriever")
    
    # Fixed prompt template - no quotes around variables
    prompt = PromptTemplate.from_template(
        "You are a very good teaching assistant. You give a concise and clear answer to the question you are asked. "
        "You are given a question: {question} and a context from the knowledge base: {context} "
        "and you have a previous chat history: {chathistory}. "
        "You must answer the question using the context and any related information from the chat history."
    )
    
    parser = StrOutputParser()
    
    # Get context from retriever
    context_docs = retriver.invoke(req.question)
    # Format context as string
    context_str = "\n\n".join([doc.page_content for doc in context_docs])
    
    # Format chat history array into readable string
    chat_history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in req.chat_history]) if req.chat_history else "No previous chat history"
    
    # Correct chain construction
    chain = prompt | model | parser
    
    print(f"starting the API call")
    # Invoke with dictionary of variables
    response = await chain.ainvoke({
        "question": req.question,
        "context": context_str,
        "chathistory": chat_history_str
    })
    print(response)
    return str(response)
