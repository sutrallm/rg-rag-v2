# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A file containing prompts definition."""

# SUMMARIZE_PROMPT = """
# You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
# Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
# Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
# If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
# Make sure it is written in third person, and include the entity names so we the have full context.
#
# #######
# -Data-
# Entities: {entity_name}
# Description List: {description_list}
# #######
# Output:
# """

# 240805 new prompt
SUMMARIZE_PROMPT = '''
You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given an entity and a list of descriptions related to it, combine all the information into a single, comprehensive description. Include all relevant details from the provided descriptions.
If any descriptions are contradictory, resolve the contradictions to provide a coherent summary.
Ensure each piece of information is accurately represented and avoid combining separate details incorrectly. Verify each description independently to avoid incorrect merging.
Don't make anything up in the summary.
Ensure the summary is written in the third person and includes the entity name for full context.
The response should only contain the summary content. Do not include any introductory phrases like "Here is a comprehensive summary" or notes such as "I have combined all relevant information".

== Data
Entity:
{entity_name}

Description List:
{description_list}
'''
