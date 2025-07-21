# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing 'CommunityReportsResult' and 'CommunityReportsExtractor' models."""

import logging
import traceback
from dataclasses import dataclass
from typing import Any

from graphrag.index.typing import ErrorHandlerFn
from graphrag.index.utils import dict_has_keys_with_types
from graphrag.llm import CompletionLLM

from .prompts import COMMUNITY_REPORT_PROMPT
from graphrag.my_graphrag.db import save_new_community_report
import graphrag.my_graphrag.cloud as model

import re
import csv
import json
import xml.etree.ElementTree as ET

import os
import random
from datetime import datetime
from pathlib import Path

import asyncio

log = logging.getLogger(__name__)


@dataclass
class CommunityReportsResult:
    """Community reports result class definition."""

    output: str
    structured_output: dict


class CommunityReportsExtractor:
    """Community reports extractor class definition."""

    _llm: CompletionLLM
    _input_text_key: str
    _extraction_prompt: str
    _output_formatter_prompt: str
    _on_error: ErrorHandlerFn
    _max_report_length: int

    def __init__(
        self,
        llm_invoker: CompletionLLM,
        input_text_key: str | None = None,
        extraction_prompt: str | None = None,
        on_error: ErrorHandlerFn | None = None,
        max_report_length: int | None = None,
    ):
        """Init method definition."""
        self._llm = llm_invoker
        self._input_text_key = input_text_key or "input_text"
        self._extraction_prompt = extraction_prompt or COMMUNITY_REPORT_PROMPT
        self._on_error = on_error or (lambda _e, _s, _d: None)
        self._max_report_length = max_report_length or 1500

        tmp_prompt_dir = ''
        prefix = ''
        try:
            cur_file_path = Path(os.path.realpath(__file__))
            tmp_prompt_dir = os.path.join(cur_file_path.parents[5], 'prompts', 'tmp')
            if os.path.isdir(tmp_prompt_dir):
                now = datetime.now()
                timestamp = now.strftime("%Y%m%d%H%M%S") + f"_{now.microsecond:06d}"
                random_id = random.randint(100000, 999999)
                prefix = f'index_prompt3_{timestamp}_{random_id}_'
        except:
            pass

        self._tmp_prompt_dir = tmp_prompt_dir
        self._prefix = prefix

        self._lock = asyncio.Lock()

    async def __call__(self, inputs: dict[str, Any]):
        """Call method definition."""
        try:
            original_input = inputs[self._input_text_key]
            converted_input = self._convert_input(original_input)

            desc_list = re.findall(r'<description>(.*?)</description>', converted_input, re.DOTALL)
            desc_input = '\n\n'.join(desc_list)

            community_prompt = COMMUNITY_REPORT_PROMPT.format(input_text=desc_input)
            output = model.get_response_from_sgl(community_prompt)

            await self._export_prompt(
                prompt_input=community_prompt,
                prompt_output=output,
                prompt_type_name='community_report',
            )

            save_new_community_report(
                converted_input,
                output,
            )

        except Exception as e:
            log.exception("error generating community report")
            self._on_error(e, traceback.format_exc(), None)

        # no need to continue the graphrag process
        return CommunityReportsResult(
            structured_output={},
            output='',
        )

    def _get_text_output(self, parsed_output: dict) -> str:
        title = parsed_output.get("title", "Report")
        summary = parsed_output.get("summary", "")
        findings = parsed_output.get("findings", [])

        def finding_summary(finding: dict):
            if isinstance(finding, str):
                return finding
            return finding.get("summary")

        def finding_explanation(finding: dict):
            if isinstance(finding, str):
                return ""
            return finding.get("explanation")

        report_sections = "\n\n".join(
            f"## {finding_summary(f)}\n\n{finding_explanation(f)}" for f in findings
        )
        return f"# {title}\n\n{summary}\n\n{report_sections}"

    # 240805
    def _convert_input(self, input_text: str) -> str:
        entities_section = re.search(r'(?i)^[^a-zA-Z]*entities[^a-zA-Z]*$\s*(.*?)\s*(?i)^[^a-zA-Z]*relationships[^a-zA-Z]*$', input_text, re.DOTALL | re.MULTILINE)
        relationships_section = re.search(r'(?i)^[^a-zA-Z]*relationships[^a-zA-Z]*$\s*(.*)', input_text, re.DOTALL | re.MULTILINE)

        entities_xml = []
        if entities_section:
            try:
                lines = entities_section.group(1).strip().split('\n')
                lines = [line for line in lines if line.strip()]
                csv_reader = csv.reader(lines)

                headers = next(csv_reader)
                for i, header in enumerate(headers):
                    header = header.strip().lower()
                    if 'id' in header:
                        headers[i] = 'id'
                    elif header == 'title':
                        headers[i] = 'entity'

                for row in csv_reader:
                    try:
                        record = dict(zip(headers, row))
                        xml_record = ET.Element('root')
                        for header in headers:
                            if header in ('id', 'entity', 'description'):
                                sub_element = ET.SubElement(xml_record, header)
                                sub_element.text = record[header].strip('"')
                        entities_xml.append(
                            ET.tostring(xml_record, encoding='unicode', method='xml').replace('<root>', '').replace('</root>', '').strip())
                    except Exception as e:
                        pass
            except Exception as e:
                entities_xml = []

        relationships_xml = []
        if relationships_section:
            try:
                lines = relationships_section.group(1).strip().split('\n')
                lines = [line for line in lines if line.strip()]
                csv_reader = csv.reader(lines)

                headers = next(csv_reader)
                for i, header in enumerate(headers):
                    header = header.strip().lower()
                    if 'id' in header:
                        headers[i] = 'id'

                for row in csv_reader:
                    try:
                        record = dict(zip(headers, row))
                        xml_record = ET.Element('root')
                        for header in headers:
                            if header in ('id', 'source', 'target', 'description'):
                                sub_element = ET.SubElement(xml_record, header)
                                sub_element.text = record[header].strip('"')
                        relationships_xml.append(
                            ET.tostring(xml_record, encoding='unicode', method='xml').replace('<root>', '').replace('</root>', '').strip())
                    except Exception as e:
                        pass
            except Exception as e:
                relationships_xml = []

        input_text_list = []
        if len(entities_xml) > 0:
            input_text_list = ['Entities:'] + entities_xml
        if len(relationships_xml) > 0:
            input_text_list += ['Relationships:'] + relationships_xml

        return '\n\n'.join(input_text_list)

    def _convert_output(self, llm_response: str) -> dict[str, Any]:
        # original format:
        # {{
        #     "title": <report_title>,
        #     "summary": <executive_summary>,
        #     "rating": <impact_severity_rating>,
        #     "rating_explanation": <rating_explanation>,
        #     "findings": [
        #         {{
        #             "summary":<insight_1_summary>,
        #             "explanation": <insight_1_explanation>
        #         }},
        #         {{
        #             "summary":<insight_2_summary>,
        #             "explanation": <insight_2_explanation>
        #         }}
        #     ]
        # }}

        # new format:
        # <title>Your Report Title</title>
        # <summary>Executive summary of the net.</summary>
        # <rating>Impact severity score.</rating>
        # <rating_explanation>Explanation for the impact severity score.</rating_explanation>
        # <findings>
        #     <insight>
        #         <insight_summary>Summary of Insight 1</insight_summary>
        #         <insight_explanation>Detailed explanation of Insight 1.</insight_explanation>
        #     </insight>
        #     ...
        # </findings>

        result = {}

        try:
            title_match = re.findall(r"<title>(.*?)</title>", llm_response, re.DOTALL)
            title = title_match[0] if title_match else None

            summary_match = re.findall(r"<summary>(.*?)</summary>", llm_response, re.DOTALL)
            summary = summary_match[0] if summary_match else None

            rating_match = re.findall(r"<rating>(.*?)</rating>", llm_response, re.DOTALL)
            rating = str(round(float(rating_match[0]), 1)) if rating_match else None

            rating_explanation_match = re.findall(r"<rating_explanation>(.*?)</rating_explanation>", llm_response, re.DOTALL)
            rating_explanation = rating_explanation_match[0] if rating_explanation_match else None

            findings = []
            insight_blocks = re.findall(r"<insight>(.*?)</insight>", llm_response, re.DOTALL)
            for block in insight_blocks:
                insight_summary = re.findall(r"<insight_summary>(.*?)</insight_summary>", block, re.DOTALL)
                insight_explanation = re.findall(r"<insight_explanation>(.*?)</insight_explanation>", block, re.DOTALL)

                if insight_summary and insight_explanation:
                    findings.append(
                        {
                            'summary': insight_summary[0],
                            'explanation': insight_explanation[0]
                        }
                    )

            if title and summary and rating and rating_explanation and len(findings) != 0:
                result = {
                    "title": title,
                    "summary": summary,
                    "rating": rating,
                    "rating_explanation": rating_explanation,
                    "findings": findings
                }
        except:
            pass

        return result

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

