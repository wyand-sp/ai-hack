import os
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
from extract_tools import extract_text_from_pdf, extract_text_from_file, extract_text_from_image


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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
if not PINECONE_API_KEY or not PINECONE_ENVIRONMENT or not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY, PINECONE_API_KEY, or PINECONE_ENVIRONMENT not set.")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

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

    # Check if the index exists
    index_list = pc.list_indexes().names()
    if index_name not in index_list:
        print(f"Creating new Pinecone index for user: {username}")
        pc.create_index(
            name=index_name,
            dimension=1024,  # Match dimension to embeddings
            metric='euclidean',  # Adjust based on your use case
            spec=ServerlessSpec(
                cloud='aws',  # You can customize this based on your cloud provider
                region=PINECONE_ENVIRONMENT  # Use the environment variable for region
            )
        )

    # Return the Pinecone Index object
    return pc.Index(index_name)

def update_user_vector_store(user: UserData, payload: str, URI: str):
    try:
        # Get or create Pinecone index for the user
        index = get_or_create_user_index(user.username)

        # Generate embeddings for the payload
        embeddings = pc.inference.embed(
            "multilingual-e5-large",
            inputs=[payload],
            parameters={
                "input_type": "passage"
            }
        )

        # Use UUID to uniquely identify the vector
        vector_id = str(uuid4())

        # Metadata to store with the vector (URI and username)
        metadata = {
            "user": user.username,
            "URI": URI,
        }

        # Upsert vector to the user-specific Pinecone index
        # index.upsert(vectors=[(vector_id, embeddings[0], metadata)])
        index.upsert(vectors=[(vector_id, embeddings[0].values, metadata)])

        print(f"Vector upserted for user {user.username} with URI: {URI}")

    except Exception as e:
        print(f"Error updating user vector store: {e}")
        raise Exception("An error occurred while updating the user vector store.")


@app.post("/login")
def login(login_request: LoginRequest):
    print(f"python version: {sys.version}")
    username = login_request.username
    get_user(username)
    return {"message": f"User {username} logged in."}

@app.post("/consume_browser")
async def consume_browser(
    user: str = Body(..., example="test"),
    payload: Optional[str] = Body(..., example="Your payload data here"),
    URI: Optional[str] = Body(..., example="http://example.com/your-uri")
):
    try:
        user_obj = get_user(user)
        update_user_vector_store(user_obj, payload, URI)
        return {"message": "User vector updated."}
    except Exception as e:
        print(f"Error updating user vector store: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the user vector store.")


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    user = get_user(username)

    try:
        while True:
            try:
                # Wait for new data
                data = await websocket.receive_text()

                # Check if the client wants to close the connection
                if data == "close":
                    await websocket.close()
                    break

                # Get or create the Pinecone index for the user
                index = get_or_create_user_index(user.username)

                try:
                    # Embed the query
                    x = pc.inference.embed(
                        model='multilingual-e5-large',
                        inputs=[data],
                        parameters={
                            "input_type": "query"
                        }
                    )
                except Exception as e:
                    print(f"Error embedding data: {e}")
                    raise HTTPException(status_code=500, detail="An error occurred while embedding the data.")

                try:
                    # Query the Pinecone index
                    results = index.query(
                        vector=x[0].values,
                        top_k=1,
                        include_values=False,
                        include_metadata=True
                    )
                except Exception as e:
                    print(f"Error querying Pinecone index: {e}")
                    raise HTTPException(status_code=500, detail="An error occurred while querying the Pinecone index.")

                # Convert the results into a JSON-serializable format
                serializable_results = []
                for match in results['matches']:
                    serializable_results.append({
                        'metadata': match.get('metadata', {'URI'})
                    })
                return_string = ''
                for x in serializable_results:
                    if x['metadata']['URI'].startswith('http'):
                        return_string += f'<br><a target="_blank" style="color: green;" href="'+ x['metadata']['URI'] + '">'
                    return_string += f'<br>' + x['metadata']['URI']

                # Send the results as JSON text via WebSocket
                await websocket.send_text(return_string)

            except WebSocketDisconnect:
                print("WebSocket connection closed")
                break

    except Exception as e:
        print(f"GENERAL PINECONE FAIL {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the WebSocket communication.")

@app.post("/upload")
async def upload_file(
    username: str = Depends(get_current_username),
    file: UploadFile = File(...)
):
    try:
        user_obj = get_user(username)

        try:
            file_to_tmp = await file.read()
            if len(file_to_tmp) > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File size exceeds the limit of 5MB.")
        except Exception as e:
            print(f"Error reading the file: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while reading the file.")

        filename_tmp = f"/tmp/{uuid4()}"
        with open(filename_tmp, "wb") as f:
            f.write(file_to_tmp)

        # Validate file type
        allowed_extensions = {'txt', 'pdf', 'docx','jpeg','jpg','png'}
        filename = file.filename
        extension = filename.split('.')[-1].lower()
        if extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        if extension in ['jpeg','jpg','png']:
            try:
                # Extract text from the image
                extracted_text = await extract_text_from_image(filename_tmp)
            except Exception as e:
                print(f"Error extracitng text from the image: {e}")
                raise HTTPException(status_code=500, detail="An error occurred while extracting text from the image.")
        elif extension in ['pdf']:
            try:
                # Extract text from the file
                extracted_text = await extract_text_from_pdf(filename_tmp)
            except Exception as e:
                print(f"Error extracting text from file: {e}")
                raise HTTPException(status_code=500, detail="An error occurred while extracting text from the file.")
        else:
            try:
                # Extract text from the file
                extracted_text = await extract_text_from_file(filename_tmp)
            except Exception as e:
                print(f"Error extracting text from file: {e}")
                raise HTTPException(status_code=500, detail="An error occurred while extracting text from the file.")

        # Remove the temporary file
        os.remove(filename_tmp)
        try:
            # Generate embeddings and update vector store
            update_user_vector_store(user_obj, extracted_text, filename)
        except Exception as e:
            print(f"Error updating user vector store: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while updating the user vector store.")

        return {"message": "File uploaded and processed successfully."}


    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")