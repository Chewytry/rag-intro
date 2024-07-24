import argparse
import os
import shutil
import logging
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from utils.get_embedding_function import get_embedding_function
from langchain.vectorstores.chroma import Chroma


CHROMA_PATH = "chroma"
DATA_PATH = "data"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def populate_database():
    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

def populate_database_alt():
    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    logging.info(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        logging.info(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]

        # Log progress of adding documents
        for i, chunk in enumerate(new_chunks, 1):
            db.add_documents([chunk], ids=[chunk.metadata["id"]])
            logging.info(f"Added document {i}/{len(new_chunks)}: {chunk.metadata['id']}")

        db.persist()
        logging.info("Database persisted successfully.")
    else:
        logging.info("✅ No new documents to add")



def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

def show_data_files():
    files = os.listdir(DATA_PATH)
    return files

def show_database_contents():
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
    existing_items = db.get(include=["ids", "metadatas"])
    existing_ids = existing_items["ids"]
    metadatas = existing_items["metadatas"]

    documents = [{"id": doc_id, "metadata": metadata} for doc_id, metadata in zip(existing_ids, metadatas)]
    return documents

def add_file_to_data(file_path):
    if os.path.exists(file_path):
        shutil.copy(file_path, DATA_PATH)
        return f"File {file_path} added to data directory."
    else:
        return f"File {file_path} does not exist."

def remove_file_from_data(file_name):
    file_path = os.path.join(DATA_PATH, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return f"File {file_path} removed from data directory."
    else:
        return f"File {file_path} does not exist in data directory."