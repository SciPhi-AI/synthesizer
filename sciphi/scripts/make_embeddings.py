import pandas as pd
from sciphi.llm.embedding_helpers import process_documents
import json


def read_jsonl(file_path):
    """
    Generator function to read a JSONL (JSON Lines) file line by line.
    """
    counter = 0
    with open(file_path, "r") as f:
        for line in f:
            counter += 1
            if counter == 1:
                continue
            yield json.loads(line.strip())


document_ids = []
documents = []

for entry in read_jsonl("sample.json"):
    # dict_keys(['template', 'content_model', 'opening_text', 'wiki', 'statement_keywords', 'auxiliary_text', 'language', 'title', 'descriptions', 'page_id', 'create_timestamp', 'text', 'timestamp', 'redirect', 'heading', 'source_text', 'version_type', 'coordinates', 'version', 'external_link', 'labels', 'namespace_text', 'statement_count', 'sitelink_count', 'namespace', 'text_bytes', 'label_count', 'incoming_links', 'category', 'outgoing_link', 'popularity_score'])
    document_ids.append(entry["page_id"])
    documents.append(entry["text"])
    print(entry)


# import pdb

# pdb.set_trace()

# # Step 2: Prepare Data for Processing
# # Assuming each entry in the data has a 'pageid' as a unique identifier and 'text' as content
# document_ids = [entry["pageid"] for entry in data]
# documents = [entry["text"] for entry in data]

# # Step 3: Process the Data
# df = process_documents(documents, document_ids)

# # Save the processed data if needed
# df.to_csv("processed_wikipedia_data.csv", index=False)


# import os
# import pandas as pd

# from sciphi.llm.embedding_helpers import (
#     process_documents,
#     sectionize_documents,
#     sentencize,
# )


# def get_contexts():
#     SIM_MODEL = "/kaggle/input/sentencetransformers-allminilml6v2/sentence-transformers_all-MiniLM-L6-v2"
#     DEVICE = 0
#     MAX_LENGTH = 384
#     BATCH_SIZE = 16

#     WIKI_PATH = "/kaggle/input/wikipedia-20230701"
#     wiki_files = os.listdir(WIKI_PATH)

#     trn = pd.read_csv("/kaggle/input/kaggle-llm-science-exam/test.csv").drop(
#         "id", 1
#     )

#     model = SentenceTransformer(SIM_MODEL, device="cuda")
#     model.max_seq_length = MAX_LENGTH
#     model = model.half()

#     sentence_index = read_index(
#         "/kaggle/input/wikipedia-2023-07-faiss-index/wikipedia_202307.index"
#     )

# )

#     # Get the top 20 pages that are likely to contain the topic of interest
#     search_score, search_index = sentence_index.search(prompt_embeddings, 20)

#     # Save memory - delete sentence_index since it is no longer necessary
#     del sentence_index
#     del prompt_embeddings
#     _ = gc.collect()
#     libc.malloc_trim(0)

#     df = pd.read_parquet(
#         "/kaggle/input/wikipedia-20230701/wiki_2023_index.parquet",
#         columns=["id", "file"],
#     )


# # import os
# # import gc
# # import pandas as pd
# # import numpy as np
# # import re
# # from tqdm.auto import tqdm


# # import faiss
# # from faiss import write_index, read_index

# # from sentence_transformers import SentenceTransformer

# # import torch
# # import ctypes

# # libc = ctypes.CDLL("libc.so.6")

# # from dataclasses import dataclass
# # from typing import Optional, Union

# # import torch
# # import numpy as np
# # import pandas as pd
# # from datasets import Dataset
# # from transformers import AutoTokenizer
# # from transformers import AutoModelForMultipleChoice, TrainingArguments, Trainer
# # from transformers.tokenization_utils_base import (
# #     PreTrainedTokenizerBase,
# #     PaddingStrategy,
# # )
# # from torch.utils.data import DataLoader


# # def get_contexts():
# #     SIM_MODEL = "/kaggle/input/sentencetransformers-allminilml6v2/sentence-transformers_all-MiniLM-L6-v2"
# #     DEVICE = 0
# #     MAX_LENGTH = 384
# #     BATCH_SIZE = 16

# #     WIKI_PATH = "/kaggle/input/wikipedia-20230701"
# #     wiki_files = os.listdir(WIKI_PATH)

# #     trn = pd.read_csv("/kaggle/input/kaggle-llm-science-exam/test.csv").drop(
# #         "id", 1
# #     )

# #     model = SentenceTransformer(SIM_MODEL, device="cuda")
# #     model.max_seq_length = MAX_LENGTH
# #     model = model.half()

# #     sentence_index = read_index(
# #         "/kaggle/input/wikipedia-2023-07-faiss-index/wikipedia_202307.index"
# #     )

# #     # prompt_embeddings = model.encode(trn.prompt.values, batch_size=BATCH_SIZE, device=DEVICE, show_progress_bar=True, convert_to_tensor=True, normalize_embeddings=True)
# #     prompt_embeddings = model.encode(
# #         trn.apply(
# #             lambda row: f"{row['prompt']}\n{row['A']}\n{row['B']}\n{row['C']}\n{row['D']}\n{row['E']}",
# #             axis=1,
# #         ).values,
# #         batch_size=BATCH_SIZE,
# #         device=DEVICE,
# #         show_progress_bar=True,
# #         convert_to_tensor=True,
# #         normalize_embeddings=True,
# #     )

# #     prompt_embeddings = prompt_embeddings.detach().cpu().numpy()
# #     _ = gc.collect()

# #     # Get the top 20 pages that are likely to contain the topic of interest
# #     search_score, search_index = sentence_index.search(prompt_embeddings, 20)

# #     # Save memory - delete sentence_index since it is no longer necessary
# #     del sentence_index
# #     del prompt_embeddings
# #     _ = gc.collect()
# #     libc.malloc_trim(0)

# #     df = pd.read_parquet(
# #         "/kaggle/input/wikipedia-20230701/wiki_2023_index.parquet",
# #         columns=["id", "file"],
# #     )

# #     # Get the article and associated file location using the index
# #     wikipedia_file_data = []

# #     for i, (scr, idx) in tqdm(
# #         enumerate(zip(search_score, search_index)), total=len(search_score)
# #     ):
# #         scr_idx = idx
# #         _df = df.loc[scr_idx].copy()
# #         _df["prompt_id"] = i
# #         wikipedia_file_data.append(_df)
# #     wikipedia_file_data = pd.concat(wikipedia_file_data).reset_index(drop=True)
# #     wikipedia_file_data = (
# #         wikipedia_file_data[["id", "prompt_id", "file"]]
# #         .drop_duplicates()
# #         .sort_values(["file", "id"])
# #         .reset_index(drop=True)
# #     )

# #     # Save memory - delete df since it is no longer necessary
# #     del df
# #     _ = gc.collect()
# #     libc.malloc_trim(0)

# #     # Get the full text data
# #     wiki_text_data = []

# #     for file in tqdm(
# #         wikipedia_file_data.file.unique(),
# #         total=len(wikipedia_file_data.file.unique()),
# #     ):
# #         _id = [
# #             str(i)
# #             for i in wikipedia_file_data[wikipedia_file_data["file"] == file][
# #                 "id"
# #             ].tolist()
# #         ]
# #         _df = pd.read_parquet(
# #             f"{WIKI_PATH}/{file}", columns=["id", "text", "title"]
# #         )

# #         _df_temp = _df[_df["id"].isin(_id)].copy()
# #         del _df
# #         _ = gc.collect()
# #         libc.malloc_trim(0)
# #         wiki_text_data.append(_df_temp)
# #     wiki_text_data = (
# #         pd.concat(wiki_text_data).drop_duplicates().reset_index(drop=True)
# #     )
# #     _ = gc.collect()

# #     # Parse documents into sentences
# #     processed_wiki_text_data = process_documents(
# #         wiki_text_data.text.values, wiki_text_data.id.values
# #     )

# #     # Get embeddings of the wiki text data
# #     wiki_data_embeddings = model.encode(
# #         processed_wiki_text_data.text,
# #         batch_size=BATCH_SIZE,
# #         device=DEVICE,
# #         show_progress_bar=True,
# #         convert_to_tensor=True,
# #         normalize_embeddings=True,
# #     )  # .half()
# #     wiki_data_embeddings = wiki_data_embeddings.detach().cpu().numpy()

# #     _ = gc.collect()

# #     # Combine all answers
# #     trn["answer_all"] = trn.apply(
# #         lambda x: " ".join([x["A"], x["B"], x["C"], x["D"], x["E"]]), axis=1
# #     )

# #     # Search using the prompt and answers to guide the search
# #     trn["prompt_answer_stem"] = trn["prompt"] + " " + trn["answer_all"]

# #     question_embeddings = model.encode(
# #         trn.prompt_answer_stem.values,
# #         batch_size=BATCH_SIZE,
# #         device=DEVICE,
# #         show_progress_bar=True,
# #         convert_to_tensor=True,
# #         normalize_embeddings=True,
# #     )
# #     question_embeddings = question_embeddings.detach().cpu().numpy()

# #     # Parameter to determine how many relevant sentences to include
# #     NUM_SENTENCES_INCLUDE = 6

# #     # List containing just Context
# #     contexts = []

# #     for r in tqdm(trn.itertuples(), total=len(trn)):
# #         prompt_id = r.Index

# #         prompt_indices = processed_wiki_text_data[
# #             processed_wiki_text_data["document_id"].isin(
# #                 wikipedia_file_data[
# #                     wikipedia_file_data["prompt_id"] == prompt_id
# #                 ]["id"].values
# #             )
# #         ].index.values

# #         if prompt_indices.shape[0] > 0:
# #             prompt_index = faiss.index_factory(
# #                 wiki_data_embeddings.shape[1], "Flat"
# #             )
# #             prompt_index.add(wiki_data_embeddings[prompt_indices])

# #             context = ""

# #             # Get the top matches
# #             ss, ii = prompt_index.search(
# #                 question_embeddings, NUM_SENTENCES_INCLUDE
# #             )
# #             for _s, _i in zip(ss[prompt_id], ii[prompt_id]):
# #                 context += (
# #                     processed_wiki_text_data.loc[prompt_indices]["text"].iloc[
# #                         _i
# #                     ]
# #                     + " "
# #                 )
# #         contexts.append(context)

# #     trn["context"] = contexts

# #     trn[["prompt", "context", "A", "B", "C", "D", "E"]].to_csv(
# #         "./test_context.csv", index=False
# #     )


# # @dataclass
# # class DataCollatorForMultipleChoice:
# #     tokenizer: PreTrainedTokenizerBase
# #     padding: Union[bool, str, PaddingStrategy] = True
# #     max_length: Optional[int] = None
# #     pad_to_multiple_of: Optional[int] = None

# #     def __call__(self, features):
# #         label_name = "label" if "label" in features[0].keys() else "labels"
# #         labels = [feature.pop(label_name) for feature in features]
# #         batch_size = len(features)
# #         num_choices = len(features[0]["input_ids"])
# #         flattened_features = [
# #             [{k: v[i] for k, v in feature.items()} for i in range(num_choices)]
# #             for feature in features
# #         ]
# #         flattened_features = sum(flattened_features, [])

# #         batch = self.tokenizer.pad(
# #             flattened_features,
# #             padding=self.padding,
# #             max_length=self.max_length,
# #             pad_to_multiple_of=self.pad_to_multiple_of,
# #             return_tensors="pt",
# #         )
# #         batch = {
# #             k: v.view(batch_size, num_choices, -1) for k, v in batch.items()
# #         }
# #         batch["labels"] = torch.tensor(labels, dtype=torch.int64)
# #         return batch


# # def generate_openbook_output():
# #     test_df = pd.read_csv("test_context.csv")
# #     test_df.index = list(range(len(test_df)))
# #     test_df["id"] = list(range(len(test_df)))
# #     test_df["prompt"] = (
# #         test_df["context"].apply(lambda x: x[:1750])
# #         + " #### "
# #         + test_df["prompt"]
# #     )
# #     test_df["answer"] = "A"
# #     model_dir = "/kaggle/input/llm-science-run-context-2"
# #     tokenizer = AutoTokenizer.from_pretrained(model_dir)
# #     model = AutoModelForMultipleChoice.from_pretrained(model_dir).cuda()
# #     model.eval()

# #     # We'll create a dictionary to convert option names (A, B, C, D, E) into indices and back again
# #     options = "ABCDE"
# #     indices = list(range(5))

# #     option_to_index = {
# #         option: index for option, index in zip(options, indices)
# #     }
# #     index_to_option = {
# #         index: option for option, index in zip(options, indices)
# #     }

# #     def preprocess(example):
# #         # The AutoModelForMultipleChoice class expects a set of question/answer pairs
# #         # so we'll copy our question 5 times before tokenizing
# #         first_sentence = [example["prompt"]] * 5
# #         second_sentence = []
# #         for option in options:
# #             second_sentence.append(example[option])
# #         # Our tokenizer will turn our text into token IDs BERT can understand
# #         tokenized_example = tokenizer(
# #             first_sentence, second_sentence, truncation=True
# #         )
# #         tokenized_example["label"] = option_to_index[example["answer"]]
# #         return tokenized_example

# #     tokenized_test_dataset = Dataset.from_pandas(
# #         test_df[["id", "prompt", "A", "B", "C", "D", "E", "answer"]].drop(
# #             columns=["id"]
# #         )
# #     ).map(
# #         preprocess,
# #         remove_columns=["prompt", "A", "B", "C", "D", "E", "answer"],
# #     )
# #     tokenized_test_dataset = tokenized_test_dataset.remove_columns(
# #         ["__index_level_0__"]
# #     )
# #     data_collator = DataCollatorForMultipleChoice(tokenizer=tokenizer)
# #     test_dataloader = DataLoader(
# #         tokenized_test_dataset,
# #         batch_size=1,
# #         shuffle=False,
# #         collate_fn=data_collator,
# #     )

# #     test_predictions = []
# #     for batch in test_dataloader:
# #         for k in batch.keys():
# #             batch[k] = batch[k].cuda()
# #         with torch.no_grad():
# #             outputs = model(**batch)
# #         test_predictions.append(outputs.logits.cpu().detach())

# #     test_predictions = torch.cat(test_predictions)

# #     predictions_as_ids = np.argsort(-test_predictions, 1)

# #     predictions_as_answer_letters = np.array(list("ABCDE"))[predictions_as_ids]
# #     # predictions_as_answer_letters[:3]

# #     predictions_as_string = test_df["prediction"] = [
# #         " ".join(row) for row in predictions_as_answer_letters[:, :3]
# #     ]

# #     submission = test_df[["id", "prediction"]]
# #     submission.to_csv("submission_backup.csv", index=False)
