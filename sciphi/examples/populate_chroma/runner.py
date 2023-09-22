"""A module for populating ChromaDB with a dataset."""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread
from typing import Generator

import chromadb
import dotenv
import openai
from chromadb.config import Settings
from datasets import Dataset, load_dataset
from openai.embeddings_utils import get_embeddings
from retrying import retry

from sciphi.core.utils import get_configured_logger

dotenv.load_dotenv()


def chunk_text(text: str, chunk_size: int) -> list[str]:
    """Chunk a text into a list of strings of size chunk_size."""
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


# Define a retrying decorator with specific parameters
@retry(
    stop_max_attempt_number=3, wait_fixed=2000
)  # Retries 3 times with a 2-second wait between retries
def robust_get_embeddings(chunks: list[str], engine: str) -> list[list[float]]:
    try:
        return get_embeddings(chunks, engine=engine)
    except Exception as e:
        logger.error(
            f"Failed to get embeddings for chunks {chunks}, with error {e}"
        )
        raise  # Reraise the exception to be caught by the retrying mechanism


def worker(worker_args: tuple) -> None:
    """Worker function to populate ChromaDB with a batch of entries."""
    thread_name = current_thread().name
    (
        collection,
        entries_batch,
        chunk_size,
        batch_size,
        max_embedding_batch_size,
        embedding_engine,
        logger,
        logger_interval,
    ) = worker_args

    local_buffer: dict[str, list] = {
        "documents": [],
        "embeddings": [],
        "metadatas": [],
        "ids": [],
    }

    logger.info(
        f"Iterating over a batch of size {len(entries_batch)} in {thread_name}..."
    )

    for n_samples_iter_local, (entry, raw_ids) in enumerate(
        entries_batch, start=1
    ):
        chunks = chunk_text(entry["code"], chunk_size)
        if n_samples_iter_local % logger_interval == 0:
            logger.info(
                f"Thread {thread_name} processed {n_samples_iter_local} samples"
            )

        local_buffer["documents"].extend(chunks)

        for i in range(0, len(chunks), max_embedding_batch_size):
            batch_of_chunks = chunks[i : i + max_embedding_batch_size]
            local_buffer["embeddings"].extend(
                get_embeddings(batch_of_chunks, engine=embedding_engine)
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


def batch_dataset(
    dataset: Dataset, batch_size: int, parsed_ids: set[str]
) -> Generator[list[tuple[dict, list[str]]], None, None]:
    # Count the number of chunks we have already parsed
    n_entries = len(parsed_ids)
    if n_entries > 0:
        logger.info(f"Loaded {n_entries} entries from ChromaDB")

    batch = []
    n_entries = 0
    for entry in dataset:
        chunks = chunk_text(entry["code"], chunk_size)
        raw_ids = [
            f"id_{i}" for i in range(n_entries, n_entries + len(chunks))
        ]
        n_entries += len(chunks)

        if set(raw_ids).issubset(parsed_ids):
            logger.debug(f"Skipping ids = {raw_ids} as they already exist")
            continue
        batch.append((entry, raw_ids))
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
    max_embedding_batch_size = 2048
    # Process dataset in multiple threads
    num_threads = 6
    # For logging
    # TODO - Modify to sure we are logging by-process
    log_level = "INFO"
    sample_log_interval = 100

    # Output collectionn name
    collection_name = (
        f"{dataset_name.replace('/', '_')}_chunk_size_eq_{chunk_size}"
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
    parsed_ids = set(collection.get(include=[])["ids"])

    dataset = load_dataset(dataset_name, streaming=streaming)
    if not streaming:
        dataset = dataset["train"].shuffle(seed=42)

    logger.info("Creating the dataset batches...")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        split_size = batches_per_split * batch_size
        args_for_workers = (
            (
                collection,
                batch,
                chunk_size,
                batch_size,
                max_embedding_batch_size,
                embedding_engine,
                logger,
                sample_log_interval,
            )
            for batch in batch_dataset(dataset, split_size, parsed_ids)
        )
        # The map method blocks until all results are returned
        list(executor.map(worker, args_for_workers))
