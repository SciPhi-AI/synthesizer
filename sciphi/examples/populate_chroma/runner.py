"""A module for populating ChromaDB with a dataset."""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread

import chromadb
import dotenv
import openai
from chromadb.config import Settings
from datasets import load_dataset
from openai.embeddings_utils import get_embeddings

from sciphi.core.utils import get_configured_logger

dotenv.load_dotenv()


def chunk_text(text: str, chunk_size: int) -> list[str]:
    """Chunk a text into a list of strings of size chunk_size."""
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def worker(worker_args: tuple) -> None:
    """Worker function to populate ChromaDB with a batch of entries."""
    thread_name = current_thread().name
    entries_batch, parsed_ids, logger, logger_interval = worker_args
    logger.info(f"Starting worker thread: {thread_name}")

    local_buffer: dict[str, list] = {
        "documents": [],
        "embeddings": [],
        "metadatas": [],
        "ids": [],
    }
    n_entries_local = len(parsed_ids)
    n_samples_iter_local = 0

    for entry in entries_batch:
        chunks = chunk_text(entry["code"], chunk_size)
        raw_ids = [
            f"id_{i}"
            for i in range(n_entries_local, n_entries_local + len(chunks))
        ]
        n_entries_local += len(chunks)
        n_samples_iter_local += 1
        if n_samples_iter_local % logger_interval == 0:
            logger.info(
                f"Thread {thread_name} processed {n_samples_iter_local} samples"
            )
            logger.info(
                (
                    "Sanity check on the local_buffer - "
                    + "\n".join(
                        [f"{k}: {len(v)}" for k, v in local_buffer.items()]
                    )
                )
            )

        if set(raw_ids).issubset(set(parsed_ids)):
            logger.debug(f"Skipping ids = {raw_ids} as they already exist")
            continue

        local_buffer["documents"].extend(chunks)
        local_buffer["embeddings"].extend(
            get_embeddings(chunks, engine=embedding_engine)
        )
        local_buffer["metadatas"].extend(
            [
                {
                    "package": entry["package"],
                    "path": entry["path"],
                    "filename": entry["filename"],
                }
            ]
            * len(chunks)
        )
        local_buffer["ids"].extend(raw_ids)

        # Write to database in chunks
        if len(local_buffer["documents"]) >= batch_size:
            logger.debug(f"Inserting ids = {local_buffer['ids']}")
            try:
                collection.add(
                    embeddings=local_buffer["embeddings"],
                    documents=local_buffer["documents"],
                    metadatas=local_buffer["metadatas"],
                    ids=local_buffer["ids"],
                )
            except Exception as e:
                logger.error(
                    f"Failed to insert ids = {local_buffer['ids']}, with {e} skipping."
                )
            local_buffer = {
                "documents": [],
                "embeddings": [],
                "metadatas": [],
                "ids": [],
            }


def batch_dataset(dataset, batch_size):
    batch = []
    for entry in dataset:
        batch.append(entry)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


if __name__ == "__main__":
    # TODO - Move to proper CLI based approach, like Fire.
    # For now, we are getting it running quick and dirty.

    # Chroma environment variables
    chroma_addr = os.environ["CHROMA_REMOTE_ADDR"]
    chroma_port = os.environ["CHROMA_REMOTE_PORT"]
    chroma_token = os.environ["CHROMA_TOKEN"]
    chroma_auth_provider = os.environ["CHROMA_AUTH_PROVIDER"]

    # OpenAI environment variables
    openai_api_key = os.environ["OPENAI_API_KEY"]
    openai.api_key = openai_api_key
    embedding_engine = "text-embedding-ada-002"

    # HF dataset
    dataset_name = "vikp/pypi_clean"
    streaming = False
    # Script variables
    # For chunking the code into smaller pieces
    chunk_size = 2048
    # For batching the embedding calls & inserts into ChromaDB
    batch_size = 64
    batches_per_split = 8
    # Process dataset in multiple threads
    num_threads = 2
    # For logging
    # TODO - Modify to sure we are logging by-process
    log_level = "INFO"
    sample_log_interval = 10

    # Output collectionn name
    collection_name = (
        f"{dataset_name.replace('/', '_')}_chunk_size_eq__{chunk_size}"
    )

    logger = get_configured_logger("populate_chroma_db", log_level)
    logger.info("Starting to populate ChromaDB")

    if not chroma_token or not chroma_addr or not chroma_port:
        raise ValueError(
            f"ChromaDB environment variables not set correctly, found: chroma_token={chroma_token}, chroma_addr={chroma_addr}, chroma_port={chroma_port}"
        )

    if not openai_api_key:
        raise ValueError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )

    client = chromadb.HttpClient(
        host=chroma_addr,
        port=chroma_port,
        settings=Settings(
            chroma_client_auth_provider=chroma_auth_provider,
            chroma_client_auth_credentials=chroma_token,
        ),
    )

    try:
        collection = client.create_collection(name=collection_name)
    except Exception as e:
        logger.info(
            f"Collection {collection_name} likely already exists, skipping creation. For completeness, here is the exception: {e}"
        )
        collection = client.get_collection(name=collection_name)

    parsed_ids = collection.get(include=[])["ids"]
    logger.info("Loading the HF dataset now...")
    dataset = load_dataset(dataset_name, streaming=streaming)
    if not streaming:
        dataset = dataset["train"].shuffle(seed=42)

    n_samples_iter = 0

    # Count the number of chunks we have already parsed
    n_entries = len(parsed_ids)
    if n_entries > 0:
        logger.info(f"Loaded {n_entries} entries from ChromaDB")

    logger.info("Creating the dataset batches...")
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        args_for_workers = (
            (batch, parsed_ids, logger, sample_log_interval)
            for batch in batch_dataset(dataset, batches_per_split * batch_size)
        )
        # The map method blocks until all results are returned
        list(executor.map(worker, args_for_workers))
