from sci_phi.prompt import Prompt
import random


def random_sample(vars_and_weights: dict) -> str:
    """Randomly sample a weighted dictionary"""
    keys, weights = zip(*vars_and_weights.items())
    if len(keys) == 0:
        raise IndexError("Cannot randomly sample an empty input.")
    return random.choices(keys, weights)[0]


def synthesize(
    outer_prompt: Prompt, input_generators: dict, batch_size: int = 1_024
) -> list[str]:
    """Synthesize a list of prompts from the given input generators."""
    results = []
    prompt_templates = {
        k: input_generators[k].pop("prompt_templates")
        for k in input_generators
    }

    while len(results) < batch_size:
        result = {}
        for inner_key, inner_generator in input_generators.items():
            inner_prompt = Prompt(
                text=random_sample(prompt_templates[inner_key]),
                expected_inputs=set(inner_generator.keys()),
            )

            generated_inputs = {
                k: random_sample(v) for k, v in inner_generator.items()
            }

            formatted_inner = inner_prompt.format(**generated_inputs)
            # TODO - Do we want to keep generator shards somewhere?
            result[inner_key] = formatted_inner

        result["formatted_prompt"] = outer_prompt.format(**result)
        result["raw_prompt"] = outer_prompt
        results.append(result)

    return results
