from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableParallel,RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from models.pymodel import ChatRequest, LLMResponseFormat
from retriver.fas import get_vector_store,chat_vector_store
from langchain_core.documents import Document
from uuid import uuid4
load_dotenv()
model = ChatGoogleGenerativeAI(
   model="gemini-3-flash-preview",
)

async def get_response(req:ChatRequest,chatfileloc:str):
    vector_store_doc = get_vector_store(chatfileloc)
    vector_store_chat= chat_vector_store(chatfileloc)
    retriver = vector_store_doc.as_retriever(search_kwargs={"k":20})
    chat_retriver = vector_store_chat.as_retriever(search_kwargs={"k":20})
    print(f"successfully getting the retriever")
    
    # Setup Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=LLMResponseFormat)
    
    # Updated prompt template with format instructions
    prompt = PromptTemplate(
        template=(
            "You are a very good teaching assistant. You give a concise and clear answer to questions.\n\n"
            "Question: {question}\n\n"
            "Context from knowledge base:\n{context}\n\n"
            "Previous chat history:\n{chathistory}\n\n"
            "Relevant information from past conversations:\n{relevant_information}\n\n"
            "Answer the question using the context and any related information from the chat history.\n"
            "Provide key points, assess your confidence, cite sources, and suggest follow-up questions.\n\n"
            "{format_instructions}"
        ),
        input_variables=["question", "context", "chathistory", "relevant_information"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Get context from retriever
    context_docs = retriver.invoke(req.question)
    context_chat = chat_retriver.invoke(req.question)
    # Format context as string
    context_str = "\n\n".join([doc.page_content for doc in context_docs])
    
    # Format chat history array into readable string
    chat_history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in req.chat_history]) if req.chat_history else "No previous chat history"
    relevant_information_from_old_chat = "\n".join([doc.page_content for doc in context_chat]) if context_chat else "No relevant past information"
    
    # Chain construction with Pydantic parser
    chain = prompt | model | parser
    
    print(f"starting the API call")
    # Invoke with dictionary of variables
    response: LLMResponseFormat = await chain.ainvoke({
        "question": req.question,
        "context": context_str,
        "chathistory": chat_history_str,
        "relevant_information": relevant_information_from_old_chat
    })
    
    # Store the answer for future retrieval
    chat_doc = Document(
        page_content=f"Q: {req.question}\nA: {response.answer}\nKey Points: {', '.join(response.key_points)}",
        metadata={"source": "AI", "question": req.question, "confidence": response.confidence_level}
    )
    doc_uuid = str(uuid4())
    vector_store_chat.add_documents(documents=[chat_doc], ids=[doc_uuid])
    return response
