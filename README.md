# Synthesizer[ΨΦ]: A multi-purpose LLM framework 💡

<p align="center">
<img width="716" alt="SciPhi Logo" src="https://github.com/emrgnt-cmplxty/sciphi/assets/68796651/195367d8-54fd-4281-ace0-87ea8523f982">
</p>

With Synthesizer, users can:

- **Custom Data Creation**: Generate datasets via LLMs that are tailored to your needs.
   - Anthropic, OpenAI, vLLM, and HuggingFace.
- **Retrieval-Augmented Generation (RAG) on Demand**: Built-in RAG Provider Interface to anchor generated data to real-world sources. 
   - Turnkey integration with Agent Search API. 
- **Custom Data Creation**: Generate datasets via LLMs that are tailored to your needs, for LLM training, RAG, and more.

---

## Fast Setup

```bash
pip install sciphi-synthesizer
```

### Using Synthesizer

1. **Generate synthetic question-answer pairs**

   ```bash
   export SCIPHI_API_KEY=MY_SCIPHI_API_KEY
   python -m synthesizer.scripts.data_augmenter run --dataset="wiki_qa"
   ```

   ```bash
   tail augmented_output/config_name_eq_answer_question__dataset_name_eq_wiki_qa.jsonl
   { "formatted_prompt": "... ### Question:\nwhat country did wine originate in\n\n### Input:\n1. URL: https://en.wikipedia.org/wiki/History%20of%20wine (Score: 0.85)\nTitle:History of wine....",
   { "completion": "Wine originated in the South Caucasus, which is now part of modern-day Armenia ..."
   ```

2. **Evaluate RAG pipeline performance**

   ```bash
   export SCIPHI_API_KEY=MY_SCIPHI_API_KEY
   python -m synthesizer.scripts.rag_harness --rag_provider="agent-search" --llm_provider_name="sciphi" --n_samples=25
   ```

### Documentation

For more detailed information, tutorials, and API references, please visit the official [Synthesizer Documentation](https://sciphi.readthedocs.io/en/latest/).

### Community & Support

- Engage with our vibrant community on [Discord](https://discord.gg/j9GxfbxqAe).
- For tailored inquiries or feedback, please [email us](mailto:owen@sciphi.ai).

### Developing with Synthesizer

Quickly set up RAG augmented generation with your choice of provider, from OpenAI, Anhtropic, vLLM, and SciPhi:

```python
# Requires SCIPHI_API_KEY in env

from synthesizer.core import LLMProviderName, RAGProviderName
from synthesizer.interface import LLMInterfaceManager, RAGInterfaceManager
from synthesizer.llm import GenerationConfig

# RAG Provider Settings
rag_interface = RAGInterfaceManager.get_interface_from_args(
    RAGProviderName("agent-search"),
    limit_hierarchical_url_results=rag_limit_hierarchical_url_results,
    limit_final_pagerank_results=rag_limit_final_pagerank_results,
)
rag_context = rag_interface.get_rag_context(query)

# LLM Provider Settings
llm_interface = LLMInterfaceManager.get_interface_from_args(
    LLMProviderName("openai"),
)

generation_config = GenerationConfig(
    model_name=llm_model_name,
    max_tokens_to_sample=llm_max_tokens_to_sample,
    temperature=llm_temperature,
    top_p=llm_top_p,
    # other generation params here ...
)

formatted_prompt = raw_prompt.format(rag_context=rag_context)
completion = llm_interface.get_completion(formatted_prompt, generation_config)
```