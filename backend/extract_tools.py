from fastapi import HTTPException
from openai import OpenAI
import fitz, base64, time, os, textract

def chatOpenAI(messages_to_ai, temperature, max_tokens = None, model="gpt-4o", max_retries=3, base_delay=2):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    retries = 0
    last_error = ''
    while retries < max_retries:
        try:
            # Attempt to create the chat completion
            response = client.chat.completions.create(
                model = model,
                temperature = temperature,
                messages = messages_to_ai,
                seed = 42,
                # max_tokens = max_tokens if max_tokens else None
            )
            return response

        except Exception as e:
            wait_time = base_delay * (2 ** retries)
            print(f"Encountered {str(e)} error. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
            last_error = str(e)

    # If max retries reached, raise an exception
    raise Exception("Max retries reached due to errors. Last error was: " + last_error)


async def extract_text_from_pdf(filepath: str) -> str:

    text = ""
    try:
        pdf_document = fitz.open(filepath)
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while extracting text from the PDF.")

    return text

async def extract_text_from_file(file_path: str) -> str:
    text = textract.process(file_path).decode('utf-8')
    return text

async def extract_text_from_image(filepath) -> str:

    try:
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        image_to_openai = encode_image(filepath)

        PROMPT_MESSAGES = [
            {
                "role": "user",
                "content": [
                    "You are an AI assistant that analyzes the content of photos.",
                    "Provide a confident description of the video:\n",
                    {"image": image_to_openai, "resize": 768},
                    "\nReturn only the description without any additional explanation.\n"
                ],
            },
        ]
        result = chatOpenAI(PROMPT_MESSAGES, 0.7, 200, model="gpt-4o")
        extracted_text = result.choices[0].message.content
        extracted_text = extracted_text.replace("'", r"").replace('"', r'')

    except Exception as e:
        print(f"Error extracting text from image with pytesseract : {e}")
        raise HTTPException(status_code=500, detail="An error occurred while extracting text from the image.")

    print(f"Extracted text: {extracted_text}")
    return extracted_text
