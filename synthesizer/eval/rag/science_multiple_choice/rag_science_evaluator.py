import os
from textwrap import dedent
from typing import Optional

import pandas as pd

from synthesizer.core.utils import get_data_dir
from synthesizer.eval.base import Evaluator
from synthesizer.interface import LLMInterface, RAGInterface

SYSTEM_TEMPLATE = dedent(
    """
    ### System Message
    You will be given multiple-choice problems, with associated context from wikipedia.
    Your task is to return ONLY the single letter which corresponds to the correct answer to the question.
    Wrap this answer in the leading text \\boxed{} to indicate your answer.
    """
)

SCIENCE_QUESTION_TEMPLATE = dedent(
    """
    ### Example {example_number}
        #### Question:
        {prompt}

            A: {A}
            B: {B}
            C: {C}
            D: {D}
            E: {E}
        
        #### Wikipedia Context:
            {search_context}
            
        #### Answer:
"""
)


class ScienceMultipleChoiceEvaluator(Evaluator):
    NAME: str = "Science Multiple Choice"
    PROMPT_FIELD = "prompt"
    ANSWER_FIELD = "answer"
    MAX_N_SHOT = 3
    DEFAULT_RESPONSE = "A"
    RAG_DISABLED_RESPONSE = "Not Available."

    def __init__(
        self,
        llm_interface: LLMInterface,
        rag_interface: Optional[RAGInterface] = None,
        n_few_shot: int = 3,
        n_samples: int = 100,
    ):
        self.llm_interface = llm_interface
        self.rag_interface = rag_interface
        if n_few_shot > ScienceMultipleChoiceEvaluator.MAX_N_SHOT:
            raise ValueError(
                f"The Science Multiple Choice Evaluator only supports {ScienceMultipleChoiceEvaluator} or fewer few shot examples."
            )
        self.n_few_shot = n_few_shot
        self.n_samples = n_samples

        self.prompts: list[str] = []
        self.instruction = self.n_shot_science_template()

        self.evals = pd.read_csv(
            os.path.join(
                get_data_dir(),
                "evals",
                f"{ScienceMultipleChoiceEvaluator.NAME.lower().replace(' ', '_')}.csv",
            )
        ).head(n_samples)

    def initialize_prompts(self):
        contexts = (
            [
                self.rag_interface.get_rag_context(prompt)
                for prompt in self.evals[
                    ScienceMultipleChoiceEvaluator.PROMPT_FIELD
                ].values
            ]
            if self.rag_interface
            else [ScienceMultipleChoiceEvaluator.RAG_DISABLED_RESPONSE]
            * len(self.evals)
        )

        self.prompts = [
            self.build_prompt(entry.to_dict(), contexts[i])
            for i, entry in self.evals.iterrows()
            if i <= self.n_samples
        ]

    def build_prompt(self, entry: dict, context: str) -> str:
        return (
            self.instruction
            + "\n"
            + SCIENCE_QUESTION_TEMPLATE.format(
                example_number=self.n_few_shot + 1,
                search_context=context,
                **entry,
            )
        )

    def evaluate_response(self, response: str, index: int) -> bool:
        cleaned_response = self.get_cleaned_response(response)
        return (
            cleaned_response
            == self.evals[ScienceMultipleChoiceEvaluator.ANSWER_FIELD][index]
        )

    def n_shot_science_template(self) -> str:
        instruction = SYSTEM_TEMPLATE
        example_number = 1
        if self.n_few_shot > 0:
            example_prompt = "Which of the following statements best characterizes the primary principle behind Einstein's theory of General Relativity as it pertains to gravitational forces in space?"
            instruction += (
                SCIENCE_QUESTION_TEMPLATE.format(
                    example_number=example_number,
                    prompt=example_prompt,
                    search_context=self.rag_interface.get_rag_context(
                        example_prompt
                    )
                    if self.rag_interface
                    else ScienceMultipleChoiceEvaluator.RAG_DISABLED_RESPONSE,
                    A='General Relativity postulates that gravity is caused by masses exchanging "graviton" particles between each other, thus attracting each other.',
                    B="General Relativity proposes that gravity is a manifestation of the curvature of spacetime, which is distorted by mass and energy.",
                    C='General Relativity argues that gravitational forces in space can be fully explained by the presence of "dark energy" that pervades the universe.',
                    D="General Relativity maintains that gravitational interactions are due to magnetic fields produced by celestial bodies in space.",
                    E='General Relativity suggests that gravity arises from the motion of particles through an invisible medium called "aether" that fills space.',
                )
                + "         \\boxed{B}"
            )
            example_number += 1

        if self.n_few_shot > 1:
            example_prompt = "Which of the following best describes the function of mitochondria in eukaryotic cells?"
            instruction += (
                SCIENCE_QUESTION_TEMPLATE.format(
                    example_number=example_number,
                    prompt=example_prompt,
                    search_context=self.rag_interface.get_rag_context(
                        example_prompt
                    )
                    if self.rag_interface
                    else ScienceMultipleChoiceEvaluator.RAG_DISABLED_RESPONSE,
                    A="Mitochondria are primarily responsible for protein synthesis using ribosomes.",
                    B="Mitochondria play a crucial role in producing energy through photosynthesis.",
                    C="Mitochondria facilitate the breakdown of sugars into carbon dioxide and water.",
                    D="Mitochondria produce ATP, providing energy for the cell through cellular respiration.",
                    E="Mitochondria are responsible for the storage and replication of DNA in the cell.",
                )
                + "         \\boxed{D}"
            )
            example_number += 1

        if self.n_few_shot > 2:
            example_prompt = "Which of the following statements best describes the process of oxidation?"
            instruction += (
                SCIENCE_QUESTION_TEMPLATE.format(
                    example_number=example_number,
                    prompt=example_prompt,
                    search_context=self.rag_interface.get_rag_context(
                        example_prompt
                    )
                    if self.rag_interface
                    else ScienceMultipleChoiceEvaluator.RAG_DISABLED_RESPONSE,
                    A="Oxidation involves the addition of oxygen to a molecule or the loss of electrons from an atom or molecule.",
                    B="Oxidation is the process by which a substance loses protons during a chemical reaction.",
                    C="Oxidation is the breaking down of larger molecules into smaller ones without the involvement of oxygen.",
                    D="Oxidation is the formation of ionic bonds between metal and non-metal atoms.",
                    E="Oxidation is the process by which a substance gains electrons during a chemical reaction.",
                )
                + "         \\boxed{A}"
            )
            example_number += 1

        return instruction

    def get_cleaned_response(self, response: str) -> str:
        if "\\boxed{" in response:
            return response.split("\\boxed{")[1].strip()[:1]
        # If the response is not a boxed response, return the default response
        return ScienceMultipleChoiceEvaluator.DEFAULT_RESPONSE
