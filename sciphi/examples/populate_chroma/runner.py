import os

import chromadb
import dotenv
import openai
from chromadb.config import Settings
from datasets import load_dataset
from openai.embeddings_utils import get_embeddings

from sciphi.core.utils import get_configured_logger

dotenv.load_dotenv()


def chunk_text(text: str, chunk_size: int) -> list[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


if __name__ == "__main__":
    chroma_addr = os.environ["CHROMA_REMOTE_ADDR"]
    chroma_port = os.environ["CHROMA_REMOTE_PORT"]
    chroma_token = os.environ["CHROMA_TOKEN"]
    chroma_auth_provider = os.environ["CHROMA_AUTH_PROVIDER"]
    openai_api_key = os.environ["OPENAI_API_KEY"]

    openai.api_key = openai_api_key
    dataset_name = "vikp/pypi_clean"
    chunk_size = 2048
    batch_size = 64
    sample_log_interval = 10
    collection_name = f"{dataset_name.replace('/', '_')}_chunk_size_eq_2048"
    log_level = "INFO"

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

    dataset = load_dataset(dataset_name, streaming=True)
    n_samples_iter = 0

    # Count the number of chunks we have already parsed
    n_entries = len(parsed_ids)
    if n_entries > 0:
        logger.info(f"Loaded {n_entries} entries from ChromaDB")

    buffer: dict[str, list] = {
        "documents": [],
        "embeddings": [],
        "metadatas": [],
        "ids": [],
    }

    for entry in dataset["train"]:
        chunks = chunk_text(entry["code"], chunk_size)
        raw_ids = [
            f"id_{i}" for i in range(n_entries, n_entries + len(chunks))
        ]
        n_entries += len(chunks)
        n_samples_iter += 1
        if n_samples_iter % sample_log_interval == 0:
            logger.info(
                f"Processed {n_samples_iter} samples, total chunks = {n_entries}"
            )
            logger.info(f"Current max id = {raw_ids[-1]}")
            logger.info(
                "Logging buffer info:\n"
                + "\n".join(
                    [
                        f"Sanity check -- There are {len(buffer[key])} entries in {key}"
                        for key in buffer
                    ]
                )
            )
        if set(raw_ids).issubset(set(parsed_ids)):
            logger.debug(f"Skipping ids = {raw_ids} as they already exist")
            continue

        buffer["documents"].extend(chunks)
        buffer["embeddings"].extend(get_embeddings(chunks))
        buffer["metadatas"].extend(
            [
                {
                    "package": entry["package"],
                    "path": entry["path"],
                    "filename": entry["filename"],
                }
            ]
            * len(chunks)
        )
        buffer["ids"].extend(raw_ids)

        if len(buffer["documents"]) >= batch_size:
            logger.debug(f"Inserting ids = {buffer['ids']}")
            collection.add(
                embeddings=buffer["embeddings"],
                documents=buffer["documents"],
                metadatas=buffer["metadatas"],
                ids=buffer["ids"],
            )
            buffer = {
                "documents": [],
                "embeddings": [],
                "metadatas": [],
                "ids": [],
            }
