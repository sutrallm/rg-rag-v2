# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A file containing prompts definition."""

# GRAPH_EXTRACTION_PROMPT = """
# -Goal-
# Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.
#
# -Steps-
# 1. Identify all entities. For each identified entity, extract the following information:
# - entity_name: Name of the entity, capitalized
# - entity_type: One of the following types: [{entity_types}]
# - entity_description: Comprehensive description of the entity's attributes and activities
# Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)
#
# 2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
# For each pair of related entities, extract the following information:
# - source_entity: name of the source entity, as identified in step 1
# - target_entity: name of the target entity, as identified in step 1
# - relationship_description: explanation as to why you think the source entity and the target entity are related to each other
# - relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
#  Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_strength>)
#
# 3. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.
#
# 4. When finished, output {completion_delimiter}
#
# ######################
# -Examples-
# ######################
# Example 1:
# Entity_types: ORGANIZATION,PERSON
# Text:
# The Verdantis's Central Institution is scheduled to meet on Monday and Thursday, with the institution planning to release its latest policy decision on Thursday at 1:30 p.m. PDT, followed by a press conference where Central Institution Chair Martin Smith will take questions. Investors expect the Market Strategy Committee to hold its benchmark interest rate steady in a range of 3.5%-3.75%.
# ######################
# Output:
# ("entity"{tuple_delimiter}CENTRAL INSTITUTION{tuple_delimiter}ORGANIZATION{tuple_delimiter}The Central Institution is the Federal Reserve of Verdantis, which is setting interest rates on Monday and Thursday)
# {record_delimiter}
# ("entity"{tuple_delimiter}MARTIN SMITH{tuple_delimiter}PERSON{tuple_delimiter}Martin Smith is the chair of the Central Institution)
# {record_delimiter}
# ("entity"{tuple_delimiter}MARKET STRATEGY COMMITTEE{tuple_delimiter}ORGANIZATION{tuple_delimiter}The Central Institution committee makes key decisions about interest rates and the growth of Verdantis's money supply)
# {record_delimiter}
# ("relationship"{tuple_delimiter}MARTIN SMITH{tuple_delimiter}CENTRAL INSTITUTION{tuple_delimiter}Martin Smith is the Chair of the Central Institution and will answer questions at a press conference{tuple_delimiter}9)
# {completion_delimiter}
#
# ######################
# Example 2:
# Entity_types: ORGANIZATION
# Text:
# TechGlobal's (TG) stock skyrocketed in its opening day on the Global Exchange Thursday. But IPO experts warn that the semiconductor corporation's debut on the public markets isn't indicative of how other newly listed companies may perform.
#
# TechGlobal, a formerly public company, was taken private by Vision Holdings in 2014. The well-established chip designer says it powers 85% of premium smartphones.
# ######################
# Output:
# ("entity"{tuple_delimiter}TECHGLOBAL{tuple_delimiter}ORGANIZATION{tuple_delimiter}TechGlobal is a stock now listed on the Global Exchange which powers 85% of premium smartphones)
# {record_delimiter}
# ("entity"{tuple_delimiter}VISION HOLDINGS{tuple_delimiter}ORGANIZATION{tuple_delimiter}Vision Holdings is a firm that previously owned TechGlobal)
# {record_delimiter}
# ("relationship"{tuple_delimiter}TECHGLOBAL{tuple_delimiter}VISION HOLDINGS{tuple_delimiter}Vision Holdings formerly owned TechGlobal from 2014 until present{tuple_delimiter}5)
# {completion_delimiter}
#
# ######################
# Example 3:
# Entity_types: ORGANIZATION,GEO,PERSON
# Text:
# Five Aurelians jailed for 8 years in Firuzabad and widely regarded as hostages are on their way home to Aurelia.
#
# The swap orchestrated by Quintara was finalized when $8bn of Firuzi funds were transferred to financial institutions in Krohaara, the capital of Quintara.
#
# The exchange initiated in Firuzabad's capital, Tiruzia, led to the four men and one woman, who are also Firuzi nationals, boarding a chartered flight to Krohaara.
#
# They were welcomed by senior Aurelian officials and are now on their way to Aurelia's capital, Cashion.
#
# The Aurelians include 39-year-old businessman Samuel Namara, who has been held in Tiruzia's Alhamia Prison, as well as journalist Durke Bataglani, 59, and environmentalist Meggie Tazbah, 53, who also holds Bratinas nationality.
# ######################
# Output:
# ("entity"{tuple_delimiter}FIRUZABAD{tuple_delimiter}GEO{tuple_delimiter}Firuzabad held Aurelians as hostages)
# {record_delimiter}
# ("entity"{tuple_delimiter}AURELIA{tuple_delimiter}GEO{tuple_delimiter}Country seeking to release hostages)
# {record_delimiter}
# ("entity"{tuple_delimiter}QUINTARA{tuple_delimiter}GEO{tuple_delimiter}Country that negotiated a swap of money in exchange for hostages)
# {record_delimiter}
# {record_delimiter}
# ("entity"{tuple_delimiter}TIRUZIA{tuple_delimiter}GEO{tuple_delimiter}Capital of Firuzabad where the Aurelians were being held)
# {record_delimiter}
# ("entity"{tuple_delimiter}KROHAARA{tuple_delimiter}GEO{tuple_delimiter}Capital city in Quintara)
# {record_delimiter}
# ("entity"{tuple_delimiter}CASHION{tuple_delimiter}GEO{tuple_delimiter}Capital city in Aurelia)
# {record_delimiter}
# ("entity"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}PERSON{tuple_delimiter}Aurelian who spent time in Tiruzia's Alhamia Prison)
# {record_delimiter}
# ("entity"{tuple_delimiter}ALHAMIA PRISON{tuple_delimiter}GEO{tuple_delimiter}Prison in Tiruzia)
# {record_delimiter}
# ("entity"{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}PERSON{tuple_delimiter}Aurelian journalist who was held hostage)
# {record_delimiter}
# ("entity"{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}PERSON{tuple_delimiter}Bratinas national and environmentalist who was held hostage)
# {record_delimiter}
# ("relationship"{tuple_delimiter}FIRUZABAD{tuple_delimiter}AURELIA{tuple_delimiter}Firuzabad negotiated a hostage exchange with Aurelia{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}QUINTARA{tuple_delimiter}AURELIA{tuple_delimiter}Quintara brokered the hostage exchange between Firuzabad and Aurelia{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}QUINTARA{tuple_delimiter}FIRUZABAD{tuple_delimiter}Quintara brokered the hostage exchange between Firuzabad and Aurelia{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}ALHAMIA PRISON{tuple_delimiter}Samuel Namara was a prisoner at Alhamia prison{tuple_delimiter}8)
# {record_delimiter}
# ("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}Samuel Namara and Meggie Tazbah were exchanged in the same hostage release{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}Samuel Namara and Durke Bataglani were exchanged in the same hostage release{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}Meggie Tazbah and Durke Bataglani were exchanged in the same hostage release{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}FIRUZABAD{tuple_delimiter}Samuel Namara was a hostage in Firuzabad{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}FIRUZABAD{tuple_delimiter}Meggie Tazbah was a hostage in Firuzabad{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}FIRUZABAD{tuple_delimiter}Durke Bataglani was a hostage in Firuzabad{tuple_delimiter}2)
# {completion_delimiter}
#
# ######################
# -Real Data-
# ######################
# Entity_types: {entity_types}
# Text: {input_text}
# ######################
# Output:"""

CONTINUE_PROMPT = "MANY entities and relationships were missed in the last extraction. Remember to ONLY emit entities that match any of the previously extracted types. Add them below using the same format:\n"
LOOP_PROMPT = "It appears some entities and relationships may have still been missed.  Answer YES | NO if there are still entities or relationships that need to be added.\n"

# 240805 new prompt
GRAPH_EXTRACTION_PROMPT = '''
== Goal
Given a text document that is potentially relevant to this activity, first identify all necessary entities from the text to capture the information and ideas presented. Next, report all relationships among the identified entities.

== Steps
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: Suggest several labels or categories for the entity. The categories should not be specific, but should be as general as possible.
- entity_description: A comprehensive description of the entity's attributes and activities
Each entity should be XML formatted as follows:

<entity>
    <entity_name>entity_name</entity_name>
    <entity_type>entity_type</entity_type>
    <entity_description>entity_description</entity_description>
</entity>

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
Each relationship should be XML formatted as follows:

<relationship>
    <source_entity>source_entity</source_entity>
    <target_entity>target_entity</target_entity>
    <relationship_description>relationship_description</relationship_description>
    <relationship_strength>relationship_strength</relationship_strength>
</relationship>

== Example 1:
Text:
The Verdantis's Central Institution is scheduled to meet on Monday and Thursday, with the institution planning to release its latest policy decision on Thursday at 1:30 p.m. PDT, followed by a press conference where Central Institution Chair Martin Smith will take questions. Investors expect the Market Strategy Committee to hold its benchmark interest rate steady in a range of 3.5%-3.75%.

Output:
<entity>
    <entity_name>CENTRAL INSTITUTION</entity_name>
    <entity_type>ORGANIZATION</entity_type>
    <entity_description>The Central Institution is the Federal Reserve of Verdantis, which is setting interest rates on Monday and Thursday.</entity_description>
</entity>
<entity>
    <entity_name>MARTIN SMITH</entity_name>
    <entity_type>PERSON</entity_type>
    <entity_description>Martin Smith is the chair of the Central Institution.</entity_description>
</entity>
<entity>
    <entity_name>MARKET STRATEGY COMMITTEE</entity_name>
    <entity_type>ORGANIZATION</entity_type>
    <entity_description>The Central Institution committee makes key decisions about interest rates and the growth of Verdantis's money supply.</entity_description>
</entity>
<relationship>
    <source_entity>MARTIN SMITH</source_entity>
    <target_entity>CENTRAL INSTITUTION</target_entity>
    <relationship_description>Martin Smith is the Chair of the Central Institution and will answer questions at a press conference.</relationship_description>
    <relationship_strength>9</relationship_strength>
</relationship>

== Example 2:
Text:
TechGlobal's (TG) stock skyrocketed in its opening day on the Global Exchange Thursday. But IPO experts warn that the semiconductor corporation's debut on the public markets isn't indicative of how other newly listed companies may perform.

TechGlobal, a formerly public company, was taken private by Vision Holdings in 2014. The well-established chip designer says it powers 85% of premium smartphones.

Output:
<entity>
    <entity_name>TECHGLOBAL</entity_name>
    <entity_type>ORGANIZATION</entity_type>
    <entity_description>TechGlobal is a stock now listed on the Global Exchange which powers 85% of premium smartphones.</entity_description>
</entity>
<entity>
    <entity_name>VISION HOLDINGS</entity_name>
    <entity_type>ORGANIZATION</entity_type>
    <entity_description>Vision Holdings is a firm that previously owned TechGlobal.</entity_description>
</entity>
<relationship>
    <source_entity>TECHGLOBAL</source_entity>
    <target_entity>VISION HOLDINGS</target_entity>
    <relationship_description>Vision Holdings formerly owned TechGlobal from 2014 until present.</relationship_description>
    <relationship_strength>5</relationship_strength>
</relationship>

== Example 3:
Text:
Five Aurelians jailed for 8 years in Firuzabad and widely regarded as hostages are on their way home to Aurelia.

The swap orchestrated by Quintara was finalized when $8bn of Firuzi funds were transferred to financial institutions in Krohaara, the capital of Quintara.

The exchange initiated in Firuzabad's capital, Tiruzia, led to the four men and one woman, who are also Firuzi nationals, boarding a chartered flight to Krohaara.

They were welcomed by senior Aurelian officials and are now on their way to Aurelia's capital, Cashion.

The Aurelians include 39-year-old businessman Samuel Namara, who has been held in Tiruzia's Alhamia Prison, as well as journalist Durke Bataglani, 59, and environmentalist Meggie Tazbah, 53, who also holds Bratinas nationality.

Output:
<entity>
    <entity_name>FIRUZABAD</entity_name>
    <entity_type>GEO</entity_type>
    <entity_description>Firuzabad held Aurelians as hostages.</entity_description>
</entity>
<entity>
    <entity_name>AURELIA</entity_name>
    <entity_type>GEO</entity_type>
    <entity_description>Country seeking to release hostages.</entity_description>
</entity>
<entity>
    <entity_name>QUINTARA</entity_name>
    <entity_type>GEO</entity_type>
    <entity_description>Country that negotiated a swap of money in exchange for hostages.</entity_description>
</entity>
<entity>
    <entity_name>TIRUZIA</entity_name>
    <entity_type>GEO</entity_type>
    <entity_description>Capital of Firuzabad where the Aurelians were being held.</entity_description>
</entity>
<entity>
    <entity_name>KROHAARA</entity_name>
    <entity_type>GEO</entity_type>
    <entity_description>Capital city in Quintara.</entity_description>
</entity>
<entity>
    <entity_name>CASHION</entity_name>
    <entity_type>GEO</entity_type>
    <entity_description>Capital city in Aurelia.</entity_description>
</entity>
<entity>
    <entity_name>SAMUEL NAMARA</entity_name>
    <entity_type>PERSON</entity_type>
    <entity_description>Aurelian who spent time in Tiruzia's Alhamia Prison.</entity_description>
</entity>
<entity>
    <entity_name>ALHAMIA PRISON</entity_name>
    <entity_type>GEO</entity_type>
    <entity_description>Prison in Tiruzia.</entity_description>
</entity>
<entity>
    <entity_name>DURKE BATAGLANI</entity_name>
    <entity_type>PERSON</entity_type>
    <entity_description>Aurelian journalist who was held hostage.</entity_description>
</entity>
<entity>
    <entity_name>MEGGIE TAZBAH</entity_name>
    <entity_type>PERSON</entity_type>
    <entity_description>Bratinas national and environmentalist who was held hostage.</entity_description>
</entity>
<relationship>
    <source_entity>FIRUZABAD</source_entity>
    <target_entity>AURELIA</target_entity>
    <relationship_description>Firuzabad negotiated a hostage exchange with Aurelia.</relationship_description>
    <relationship_strength>2</relationship_strength>
</relationship>
<relationship>
    <source_entity>QUINTARA</source_entity>
    <target_entity>AURELIA</target_entity>
    <relationship_description>Quintara brokered the hostage exchange between Firuzabad and Aurelia.</relationship_description>
    <relationship_strength>2</relationship_strength>
</relationship>
<relationship>
    <source_entity>QUINTARA</source_entity>
    <target_entity>FIRUZABAD</target_entity>
    <relationship_description>Quintara brokered the hostage exchange between Firuzabad and Aurelia.</relationship_description>
    <relationship_strength>2</relationship_strength>
</relationship>
<relationship>
    <source_entity>SAMUEL NAMARA</source_entity>
    <target_entity>ALHAMIA PRISON</target_entity>
    <relationship_description>Samuel Namara was a prisoner at Alhamia prison.</relationship_description>
    <relationship_strength>8</relationship_strength>
</relationship>
<relationship>
    <source_entity>SAMUEL NAMARA</source_entity>
    <target_entity>MEGGIE TAZBAH</target_entity>
    <relationship_description>Samuel Namara and Meggie Tazbah were exchanged in the same hostage release.</relationship_description>
    <relationship_strength>2</relationship_strength>
</relationship>
<relationship>
    <source_entity>SAMUEL NAMARA</source_entity>
    <target_entity>DURKE BATAGLANI</target_entity>
    <relationship_description>Samuel Namara and Durke Bataglani were exchanged in the same hostage release.</relationship_description>
    <relationship_strength>2</relationship_strength>
</relationship>
<relationship>
    <source_entity>MEGGIE TAZBAH</source_entity>
    <target_entity>DURKE BATAGLANI</target_entity>
    <relationship_description>Meggie Tazbah and Durke Bataglani were exchanged in the same hostage release.</relationship_description>
    <relationship_strength>2</relationship_strength>
</relationship>
<relationship>
    <source_entity>SAMUEL NAMARA</source_entity>
    <target_entity>FIRUZABAD</target_entity>
    <relationship_description>Samuel Namara was a hostage in Firuzabad.</relationship_description>
    <relationship_strength>2</relationship_strength>
</relationship>
<relationship>
    <source_entity>MEGGIE TAZBAH</source_entity>
    <target_entity>FIRUZABAD</target_entity>
    <relationship_description>Meggie Tazbah was a hostage in Firuzabad.</relationship_description>
    <relationship_strength>2</relationship_strength>
</relationship>
<relationship>
    <source_entity>DURKE BATAGLANI</source_entity>
    <target_entity>FIRUZABAD</target_entity>
    <relationship_description>Durke Bataglani was a hostage in Firuzabad.</relationship_description>
    <relationship_strength>2</relationship_strength>
</relationship>

== Real Data
Text:

{input_text}
'''

GLEANING_PROMPT = '''
A source text is provided below, along with the entities and relationships extracted from it in XML format. However, some entities or relationships might be missing. Please identify and list the missing ones if any using the same format. Ensure that only entities and relationships explicitly mentioned in the source text are added. Do not create any additional entities or relationships beyond those mentioned in the text. If you are not able to identify any additional ones, just put the single word NOMORE in your reply, do not add any extra punctuation, characters, or explanations.

== Source Text

{input_text}

== Entities and Relationships

{previous_output}

== Important Reminder

If you find any missing entities or relationships, add them using the exact same tags as the provided XML format. Do not create new XML tags beyond those in the provided example.
'''

ENTITIES_IDENTIFICATION_PROMPT = '''
A source text and a list of entities are provided below. Identify all entities whose <entity_name> appears in the source text. Return only the matching entities in their original XML format.

== Source Text

{input_text}

== Entities

{entities}

== Important Reminder

You must output the entities in their original XML format.
'''
