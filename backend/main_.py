import os
import textract
import mlflow
import sys
from uuid import uuid4
from typing import List, Optional
from fastapi import (
    FastAPI, WebSocket, Depends, UploadFile, File,
    HTTPException, Header, status, WebSocketDisconnect, Body
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory user data storage
users = {}

# Ensure OPENAI_API_KEY and PINECONE_API_KEY are set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
if not OPENAI_API_KEY or not PINECONE_API_KEY or not PINECONE_ENVIRONMENT:
    raise ValueError("OPENAI_API_KEY, PINECONE_API_KEY, or PINECONE_ENVIRONMENT not set.")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Load embedding model
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Initialize LLM
llm = OpenAI(
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY,
)

class UserData(BaseModel):
    username: str
    chat_history: List[str] = []

    class Config:
        arbitrary_types_allowed = True

def get_user(username: str) -> UserData:
    if username not in users:
        users[username] = UserData(username=username)
    return users[username]

class LoginRequest(BaseModel):
    username: str

async def get_current_username(x_username: str = Header(None)):
    if not x_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username",
        )
    return x_username

def get_or_create_user_index(username: str):
    """Get or create a Pinecone index for the user."""
    # Use the username to create a unique index name
    index_name = f"user-index-{username}"

    # Check if the index exists, create it if not
    index_list = pc.list_indexes()
    if index_name not in index_list.names():
        print(f"Creating new Pinecone index for user: {username}")
        pc.create_index(
            name=index_name,
            dimension=1536,  # Match dimension to embeddings
            metric='euclidean',  # Adjust based on your use case
            spec=ServerlessSpec(
                cloud='aws',  # You can customize this
                region=PINECONE_ENVIRONMENT  # Use the environment variable
            )
        )

    # Connect to the user's index
    return pc.index(index_name)

def update_user_vector_store(user: UserData, payload: str, URI: str):
    try:
        # Get or create Pinecone index for the user
        index = get_or_create_user_index(user.username)

        # Generate embeddings for the payload
        embeddings = embedding_model.embed_documents([payload])

        # Use UUID to uniquely identify the vector
        vector_id = str(uuid4())

        # Metadata to store with the vector (URI and username)
        metadata = {
            "user": user.username,
            "URI": URI,
        }

        # Upsert vector to Pinecone index
        index.upsert(vectors=[(vector_id, embeddings[0], metadata)])

        print(f"Vector upserted for user {user.username} with URI: {URI}")

    except Exception as e:
        print(f"Error updating user vector store: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the user vector store.")


@app.post("/login")
def login(login_request: LoginRequest):
    print(f"python version: {sys.version}")
    username = login_request.username
    get_user(username)
    return {"message": f"User {username} logged in."}

@app.post("/consume_browser")
async def consume_browser(
    user: str = Depends(get_current_username),
    payload:  Optional[str] = Body(..., example="Your payload data here"),
    URI: Optional[str] = Body(..., example="http://example.com/your-uri")
):
    try:
        # Get user object
        user_obj = get_user(user)

        # Generate embeddings and update vector store,
        update_user_vector_store(user_obj, payload, URI)
        return {"message": "User vector updated."}
    except Exception as e:
        print(f"Error updating user vector store: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the user vector store.")

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    user = get_user(username)

    # Initialize conversation memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    mlflow.set_experiment("chatbot RAG")

    try:
        while True:
            data = await websocket.receive_text()
            user.chat_history.append(data)

            # Check if the user has an existing vector store in Pinecone
            index = get_or_create_user_index(user.username)
            vectors = index.describe_index_stats()  # Get stats to check if vectors exist

            if vectors['total_vector_count'] > 0:
                # Use ConversationalRetrievalChain if vector store has data
                retriever = index.as_retriever(search_kwargs={"k": 3})

                conversation = ConversationalRetrievalChain.from_llm(
                    llm=llm,
                    retriever=retriever,
                    memory=memory,
                    verbose=True
                )

                with mlflow.start_run():
                    mlflow.log_param("username", username)
                    mlflow.log_param("message", data)
                    mlflow.log_param("model", "OpenAI")
                    mlflow.log_param("temperature", llm.temperature)

                    # Run the conversation with the LLM and vector-based retrieval
                    response = conversation.run(data)

                    # Log model response and some metrics
                    mlflow.log_metric("response_length", len(response))
                    # Log the output
                    with open("output.txt", "w") as f:
                        f.write(response)
                    mlflow.log_artifact("output.txt")

            else:
                # Use a basic ConversationChain if there is no vector data for retrieval
                conversation = ConversationChain(
                    llm=llm,
                    memory=memory,
                    verbose=True
                )

                with mlflow.start_run():
                    mlflow.log_param("username", username)
                    mlflow.log_param("message", data)
                    mlflow.log_param("model", "OpenAI")
                    mlflow.log_param("temperature", llm.temperature)

                    # Run a standard conversation with no retrieval
                    response = conversation.run(input=data)

                    # Log model response and some metrics
                    mlflow.log_metric("response_length", len(response))
                    # Log the output
                    with open("output.txt", "w") as f:
                        f.write(response)
                    mlflow.log_artifact("output.txt")

            # Store the response in the user's chat history
            user.chat_history.append(response)

            # Send the response back to the client via WebSocket
            await websocket.send_text(response)

    except WebSocketDisconnect:
        print(f"User {username} disconnected")
    except Exception as e:
        print(f"Error during message handling: {e}")
        await websocket.send_text("An error occurred on the server.")