import os, sys, asyncio
from extract_tools import extract_text_from_pdf, extract_text_from_file, extract_text_from_image
from main import get_user, update_user_vector_store
homedir = '/home/aibudy/'
# Check if a file has been processed before
def is_file_processed(file_path, processed_files):
    return file_path in processed_files

# Process the file
async def process_file(file_path):
    print(file_path)
    extension = file_path.split('.')[-1].lower()
    if extension in ['jpeg','jpg','png']:
        text = await extract_text_from_image(file_path)
    elif extension in ['pdf']:
        text = await extract_text_from_pdf(file_path)
    elif extension in ['docx','doc','txt']:
        text = await extract_text_from_file(file_path)
    else:
        print("Unsupported file format")
        return

    user_obj = get_user('damyan')
    update_user_vector_store(user_obj, text, file_path)

async def process_files(directory, processed_files):
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        # Skip directories
        if os.path.isdir(file_path):
            continue

        # Skip files already processed
        if is_file_processed(file_path, processed_files):
            continue

        # Call the asynchronous function
        await process_file(file_path)

        # Add the file to the set of processed files
        processed_files.add(file_path)

async def main_():
    if len(sys.argv) != 2:
        print('Usage: python process_files.py <directory>')
        sys.exit(1)

    # Directory path
    directory = sys.argv[1]

    # Set to store processed files
    processed_files = set()
    try:
        with open(homedir + 'processed_files.txt') as f:
            for line in f:
                processed_files.add(line.strip())
    except FileNotFoundError:
        pass

    # Process each file in the directory
    await process_files(directory, processed_files)


    with open(homedir + 'processed_files.txt', 'w') as f:
        for file_path in processed_files:
            f.write(file_path + '\n')

asyncio.run(main_())