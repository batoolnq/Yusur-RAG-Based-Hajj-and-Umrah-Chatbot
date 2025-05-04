#-------------------------------
# English Documents Extraction
#-------------------------------

# Mount to Google Colab
from google.colab import drive
drive.mount('/content/drive')

import os
from langchain.document_loaders import PyPDFDirectoryLoader

# Define the directory in Google Drive where PDFs are stored
pdf_directory = "/content/drive/My Drive/English_Yusur_Dataset/"  

# Define the output file where extracted text will be saved
output_file = "/content/drive/My Drive/extractedEng_text.txt"

# Ensure the directory exists
if not os.path.exists(pdf_directory):
    print(f"Error: Directory '{pdf_directory}' not found. Check your Google Drive path.")
else:
    print(f"Processing PDFs from: {pdf_directory}")

    # Load all PDFs from the directory
    loader = PyPDFDirectoryLoader(pdf_directory)
    documents = loader.load()

    # Extract text from all documents
    extracted_texts = []
    for doc in documents:
        filename = doc.metadata["source"].split("/")[-1]  # Get PDF filename
        extracted_texts.append(f"{doc.page_content}\n")

    # Save extracted text from all PDFs into a single text file
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(extracted_texts))

    print(f"Extraction complete! Text saved to: {output_file}")


#-------------------------------
# Arabic Documents Extraction
#-------------------------------


import requests
import PyPDF2
import re
import os
import time

# Function to split PDF into smaller chunks (e.g., every 2 pages)
def split_pdf(pdf_path, output_folder, chunk_size=2):
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(reader.pages)
        pdf_chunks = []

        for i in range(0, total_pages, chunk_size):
            writer = PyPDF2.PdfWriter()
            chunk_path = os.path.join(output_folder, f"chunk_{i//chunk_size}.pdf")

            for j in range(i, min(i + chunk_size, total_pages)):
                writer.add_page(reader.pages[j])

            with open(chunk_path, "wb") as output_pdf:
                writer.write(output_pdf)

            pdf_chunks.append(chunk_path)

    return pdf_chunks

# Function to extract text from a given PDF chunk with retries
def extract_text_from_pdf(pdf_path, api_key, retries=3, delay=5):
    url = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"
    
    for attempt in range(retries):
        try:
            with open(pdf_path, "rb") as file:
                files = {"pdf": file}
                headers = {"Authorization": f"Basic {api_key}"}
                response = requests.post(url, files=files, headers=headers, timeout=60)  # Increased timeout

            if response.status_code == 429:  # Rate limit error
                print("⚠️ API rate limit reached. Waiting before retrying...")
                time.sleep(30)  # Wait and retry
                continue

            if response.status_code != 200:
                print(f"⚠️ API Error {response.status_code}: {response.text}")
                time.sleep(delay)
                continue

            extracted_data = response.json()  # May cause JSONDecodeError

            # Ensure valid response structure
            if "data" in extracted_data and "chunks" in extracted_data["data"]:
                extracted_texts = []
                
                for chunk in extracted_data["data"]["chunks"]:
                    text = chunk["text"].strip()

                    # Remove English words while keeping Arabic, numbers, and punctuation
                    cleaned_text = re.sub(r"[a-zA-Z]+", "", text)  

                    # Replace multiple newlines with a single newline
                    cleaned_text = re.sub(r"\n{2,}", "\n", cleaned_text)

                    # Remove unwanted headers
                    if not re.match(r"^(###\s*Additional Elements|###\s*Visual Elements|###\s*Map Details|###\s*Map Description|###\s*Visual Elements|###\s*Map Annotations)", cleaned_text):
                        extracted_texts.append(cleaned_text)

                return "\n".join(extracted_texts).strip()

            else:
                print("⚠️ No valid text extracted, retrying...")
                time.sleep(delay)

        except requests.exceptions.JSONDecodeError:
            print("⚠️ JSONDecodeError: Empty or invalid response, retrying...")
            time.sleep(delay)

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Request failed: {e}, retrying...")
            time.sleep(delay)

    print("❌ Failed to extract text after multiple retries.")
    return ""

# Main function to process large PDFs
def process_large_pdf(pdf_path, api_key, output_folder="pdf_chunks"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_chunks = split_pdf(pdf_path, output_folder)
    full_extracted_text = ""

    for chunk in pdf_chunks:
        print(f"Processing {chunk}...")
        time.sleep(2)  # Prevent rate limiting
        chunk_text = extract_text_from_pdf(chunk, api_key)
        full_extracted_text += chunk_text + "\n"

    # Remove extra newlines and save the cleaned extracted text
    full_extracted_text = re.sub(r"\n{2,}", "\n", full_extracted_text).strip()
    
    output_file_path = os.path.splitext(pdf_path)[0] + "_extracted.txt"
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(full_extracted_text)

    print(f"✅ Extracted text saved to {output_file_path}")
    return full_extracted_text

# Usage example
pdf_path = r"C:\Users\batoo\Dropbox\My PC (DESKTOP-JC1408G)\Downloads\Arabic_Merged_PDF.pdf"
api_key = "YzhzdGM0Zno2ZHo0NW4wMGk4eXIxOjBYTDJFazlzZFI0M1dncUFkSTdwZkpnUG9HaXg0OUZt"

extracted_text = process_large_pdf(pdf_path, api_key)
print(extracted_text)

# Clean the Extracted Files
import re

def remove_english_words(text):
    # Remove English words and symbols
    cleaned_text = re.sub(r"[a-zA-Z#,.()-]+", "", text)  # Remove English words
    
    # Remove only truly standalone numbers (not part of a sentence)
    #cleaned_text = re.sub(r"(?<!\S)(?<!\d)\b\d+\b(?!\d)(?!\S)", "", cleaned_text)  

    cleaned_text = re.sub(r"\n\s*\n+", "\n", cleaned_text)  # Replace multiple newlines with a single newline
    cleaned_text = re.sub(r"\*", "", cleaned_text)  # Remove all asterisks
    cleaned_text = re.sub(r"[ ]{2,}", " ", cleaned_text)  # Remove extra spaces
    cleaned_text = re.sub(r'(?<!\S)(\*?:\s*|""\s*|"\s*"|[0-9]+\s*\*\s*[0-9]*\*:)\s*(?!\S)', "", cleaned_text)  # Remove empty quotations and patterns
    cleaned_text = re.sub(r"\(\s*\)|\{\s*\}|\[\s*\]|\<\s*\>", "", cleaned_text)  # Remove empty brackets

    return cleaned_text.strip()

# Example usage
cleaned_text = remove_english_words(extractedText)
print(cleaned_text)

with open("extractedAra_text.txt", "w", encoding="utf-8") as file:
    file.write(cleaned_text)



