import pandas as pd
from collections.abc import Iterable
from tqdm import tqdm
import blingfire as bf


def process_documents(
    documents: Iterable[str],
    document_ids: Iterable,
    split_sentences: bool = True,
    filter_len: int = 3,
    disable_progress_bar: bool = False,
) -> pd.DataFrame:
    """
    Main helper function to process documents from the EMR.

    :param documents: Iterable containing documents which are strings
    :param document_ids: Iterable containing document unique identifiers
    :param document_type: String denoting the document type to be processed
    :param document_sections: List of sections for a given document type to process
    :param split_sentences: Flag to determine whether to further split sections into sentences
    :param filter_len: Minimum character length of a sentence (otherwise filter out)
    :param disable_progress_bar: Flag to disable tqdm progress bar
    :return: Pandas DataFrame containing the columns `document_id`, `text`, `section`, `offset`
    """

    df = sectionize_documents(documents, document_ids, disable_progress_bar)

    if split_sentences:
        df = sentencize(
            df.text.values,
            df.document_id.values,
            df.offset.values,
            filter_len,
            disable_progress_bar,
        )
    return df


def sectionize_documents(
    documents: Iterable[str],
    document_ids: Iterable,
    disable_progress_bar: bool = False,
) -> pd.DataFrame:
    """
    Obtains the sections of the imaging reports and returns only the
    selected sections (defaults to FINDINGS, IMPRESSION, and ADDENDUM).

    :param documents: Iterable containing documents which are strings
    :param document_ids: Iterable containing document unique identifiers
    :param disable_progress_bar: Flag to disable tqdm progress bar
    :return: Pandas DataFrame containing the columns `document_id`, `text`, `offset`
    """
    processed_documents = []
    for document_id, document in tqdm(
        zip(document_ids, documents),
        total=len(documents),
        disable=disable_progress_bar,
    ):
        text, start, end = (document, 0, len(document))
        row = {
            "document_id": document_id,
            "text": text,
            "offset": (start, end),
        }
        processed_documents.append(row)

    _df = pd.DataFrame(processed_documents)
    if _df.shape[0] > 0:
        return _df.sort_values(["document_id", "offset"]).reset_index(
            drop=True
        )
    else:
        return _df


def sentencize(
    documents: Iterable[str],
    document_ids: Iterable,
    offsets: Iterable[tuple[int, int]],
    filter_len: int = 3,
    disable_progress_bar: bool = False,
) -> pd.DataFrame:
    """
    Split a document into sentences. Can be used with `sectionize_documents`
    to further split documents into more manageable pieces. Takes in offsets
    to ensure that after splitting, the sentences can be matched to the
    location in the original documents.

    :param documents: Iterable containing documents which are strings
    :param document_ids: Iterable containing document unique identifiers
    :param offsets: Iterable tuple of the start and end indices
    :param filter_len: Minimum character length of a sentence (otherwise filter out)
    :return: Pandas DataFrame containing the columns `document_id`, `text`, `section`, `offset`
    """

    document_sentences = []
    for document, document_id, offset in tqdm(
        zip(documents, document_ids, offsets),
        total=len(documents),
        disable=disable_progress_bar,
    ):
        try:
            _, sentence_offsets = bf.text_to_sentences_and_offsets(document)
            for o in sentence_offsets:
                if o[1] - o[0] > filter_len:
                    sentence = document[o[0] : o[1]]
                    abs_offsets = (o[0] + offset[0], o[1] + offset[0])
                    row = {
                        "document_id": document_id,
                        "text": sentence,
                        "offset": abs_offsets,
                    }
                    document_sentences.append(row)
        except:
            continue
    return pd.DataFrame(document_sentences)
