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

async def get_response(req:ChatRequest):
    vector_store = get_vector_store(req.chat_id)
    retriver = vector_store.as_retriever(search_kwargs={"k":10})
    print(f"success full geting the retriver")
    prompt = PromptTemplate.from_template(
    "You are a very good answer giver. You are given a query: '{query}' and a context: '{context}'. "
    "You must answer the query using the context only.")  
    prompt2= PromptTemplate.from_template(
        " you are a summerizer , you have the summerize this text'{text}'"
    )
    chain1 = RunnableParallel(
        {
            "query":RunnablePassthrough(),
            "context":retriver

        }
    ) 
    parser=StrOutputParser()
    chain2=chain1 |prompt|model| parser|prompt2|model|parser
    print(f"start the api call")
    response = await chain2.ainvoke(req.question)
    print(response)
    return str(response)
