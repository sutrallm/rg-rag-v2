# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing 'GraphExtractionResult' and 'GraphExtractor' models."""

import json
import os
import random
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

from graphrag.index.typing import ErrorHandlerFn
from graphrag.index.utils.tokens import num_tokens_from_string
from graphrag.llm import CompletionLLM

from .prompts import SUMMARIZE_PROMPT

import asyncio

import graphrag.my_graphrag.model as model

# Max token size for input prompts
DEFAULT_MAX_INPUT_TOKENS = 4_000
# Max token count for LLM answers
DEFAULT_MAX_SUMMARY_LENGTH = 500


@dataclass
class SummarizationResult:
    """Unipartite graph extraction result class definition."""

    items: str | tuple[str, str]
    description: str


class SummarizeExtractor:
    """Unipartite graph extractor class definition."""

    _llm: CompletionLLM
    _entity_name_key: str
    _input_descriptions_key: str
    _summarization_prompt: str
    _on_error: ErrorHandlerFn
    _max_summary_length: int
    _max_input_tokens: int

    def __init__(
        self,
        llm_invoker: CompletionLLM,
        entity_name_key: str | None = None,
        input_descriptions_key: str | None = None,
        summarization_prompt: str | None = None,
        on_error: ErrorHandlerFn | None = None,
        max_summary_length: int | None = None,
        max_input_tokens: int | None = None,
    ):
        """Init method definition."""
        # TODO: streamline construction
        self._llm = llm_invoker
        self._entity_name_key = entity_name_key or "entity_name"
        self._input_descriptions_key = input_descriptions_key or "description_list"

        # 240805 define the prompts on prompts.py
        # self._summarization_prompt = summarization_prompt or SUMMARIZE_PROMPT
        self._summarization_prompt = SUMMARIZE_PROMPT
        self._on_error = on_error or (lambda _e, _s, _d: None)
        self._max_summary_length = max_summary_length or DEFAULT_MAX_SUMMARY_LENGTH
        self._max_input_tokens = max_input_tokens or DEFAULT_MAX_INPUT_TOKENS

        tmp_prompt_dir = ''
        prefix = ''
        try:
            cur_file_path = Path(os.path.realpath(__file__))
            tmp_prompt_dir = os.path.join(cur_file_path.parents[5], 'prompts', 'tmp')
            if os.path.isdir(tmp_prompt_dir):
                now = datetime.now()
                timestamp = now.strftime("%Y%m%d%H%M%S") + f"_{now.microsecond:06d}"
                random_id = random.randint(100000, 999999)
                prefix = f'index_prompt2_{timestamp}_{random_id}_'
        except:
            pass

        self._tmp_prompt_dir = tmp_prompt_dir
        self._prefix = prefix

        self._lock = asyncio.Lock()

    async def __call__(
        self,
        items: str | tuple[str, str],
        descriptions: list[str],
    ) -> SummarizationResult:
        """Call method definition."""
        result = ""
        if len(descriptions) == 0:
            result = ""
        if len(descriptions) == 1:
            result = descriptions[0]
        else:
            result = await self._summarize_descriptions(items, descriptions)

        return SummarizationResult(
            items=items,
            description=result or "",
        )

    async def _summarize_descriptions(
        self, items: str | tuple[str, str], descriptions: list[str]
    ) -> str:
        """Summarize descriptions into a single description."""
        sorted_items = sorted(items) if isinstance(items, list) else items

        # Safety check, should always be a list
        if not isinstance(descriptions, list):
            descriptions = [descriptions]

            # Iterate over descriptions, adding all until the max input tokens is reached
        usable_tokens = self._max_input_tokens - num_tokens_from_string(
            self._summarization_prompt
        )
        descriptions_collected = []
        result = ""

        for i, description in enumerate(descriptions):
            usable_tokens -= num_tokens_from_string(description)
            descriptions_collected.append(description)

            # If buffer is full, or all descriptions have been added, summarize
            if (usable_tokens < 0 and len(descriptions_collected) > 1) or (
                i == len(descriptions) - 1
            ):
                # Calculate result (final or partial)
                result = await self._summarize_descriptions_with_llm(
                    sorted_items, descriptions_collected
                )

                # If we go for another loop, reset values to new
                if i != len(descriptions) - 1:
                    descriptions_collected = [result]
                    usable_tokens = (
                        self._max_input_tokens
                        - num_tokens_from_string(self._summarization_prompt)
                        - num_tokens_from_string(result)
                    )

        return result

    async def _summarize_descriptions_with_llm(
        self, items: str | tuple[str, str] | list[str], descriptions: list[str]
    ):
        """Summarize descriptions using the LLM."""
        summarization_prompt = self._summarization_prompt.format(entity_name=json.dumps(items), description_list=json.dumps(sorted(descriptions)))
        output = model.get_response_from_sgl(summarization_prompt)

        await self._export_prompt(
            prompt_input=summarization_prompt,
            prompt_output=output,
            prompt_type_name='summary',
        )

        return output

    async def _export_prompt(
            self,
            prompt_input: str,
            prompt_output: str,
            prompt_type_name: str,
    ) -> None:
        async with self._lock:
            try:
                tmp_prompt_dir = self._tmp_prompt_dir
                prefix = self._prefix
                if tmp_prompt_dir and prefix:
                    with open(os.path.join(tmp_prompt_dir, f'{prefix}{prompt_type_name}_input.txt'), 'w') as f:
                            f.write(prompt_input)
                            f.flush()

                    with open(os.path.join(tmp_prompt_dir, f'{prefix}{prompt_type_name}_output.txt'), 'w') as f:
                            f.write(prompt_output)
                            f.flush()
            except:
                pass
