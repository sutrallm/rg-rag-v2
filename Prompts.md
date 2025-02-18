# Prompts

### Index

**Denoise**

```
Reorganise the following text into bullet points. Focus on the principles described,
removing any dialogue style or references to individuals. Do not omit any details.
There is no need to include headings. Do not add anything beyond what is mentioned
in the text. Use "#" as the bullet marker.

e.g.

# point 1
# point 2
# point 3

== Text

{input_text}
```

**Raptor**

Split the raptor summary prompt into several steps:

<details>
<summary>1. Generate summary text prompt:</summary>

```
Summarize the following text in bullet points without any reference to tables or figures. 
The summary needs to be self-contained. Don’t mention that it is a summary. Put a blank 
line between the bullets.

<text>
{text}
</text>
```
</details>

<details>
<summary>2. Refine summary text prompt:</summary>

```
Please refine the following text to eliminate any redundant or repetitive descriptions. 
Ensure the result is concise, clear, and free of unnecessary details while preserving 
key points. Organize the information in bullet points, with a blank line between each. 
Present the output in a logical order, prioritizing clarity and brevity. Output only  the refined 
text without any introductory remarks. Do not mention “Here is the refined text” in your response.

<text>
{text}
</text>
```
</details>

<details>
<summary>3. Add heading prompt:</summary>

```
Please provide a concise and descriptive heading that captures the core theme of the following 
text. Output only the heading text.

<text>
{text}
</text>
```
</details>

<details>
<summary>4. Program combines summary text and heading as the final summary prompt:</summary>

```
<heading>heading text from step 3</heading>
summary text from step 2
```
</details>

**GraphRAG**

<details>
<summary>1. Extract entity and relationship</summary>

```
== Goal
Given a text document that is potentially relevant to this activity, first identify all necessary entities from the text to capture the information and ideas presented. Next, report all relationships among the identified entities.

== Steps
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: Suggest several labels or categories for the entity. The categories should not be specific, but should be as general as possible.
- entity_description: A comprehensive description of the entity’s attributes and activities
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
The Verdantis’s Central Institution is scheduled to meet on Monday and Thursday, with the institution planning to release its latest policy decision on Thursday at 1:30 p.m. PDT, followed by a press conference where Central Institution Chair Martin Smith will take questions. Investors expect the Market Strategy Committee to hold its benchmark interest rate steady in a range of 3.5%-3.75%.

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
    <entity_description>The Central Institution committee makes key decisions about interest rates and the growth of Verdantis’s money supply.</entity_description>
</entity>
<relationship>
    <source_entity>MARTIN SMITH</source_entity>
    <target_entity>CENTRAL INSTITUTION</target_entity>
    <relationship_description>Martin Smith is the Chair of the Central Institution and will answer questions at a press conference.</relationship_description>
    <relationship_strength>9</relationship_strength>
</relationship>

== Example 2:
Text:
TechGlobal’s (TG) stock skyrocketed in its opening day on the Global Exchange Thursday. But IPO experts warn that the semiconductor corporation’s debut on the public markets isn’t indicative of how other newly listed companies may perform.

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

The exchange initiated in Firuzabad’s capital, Tiruzia, led to the four men and one woman, who are also Firuzi nationals, boarding a chartered flight to Krohaara.

They were welcomed by senior Aurelian officials and are now on their way to Aurelia’s capital, Cashion.

The Aurelians include 39-year-old businessman Samuel Namara, who has been held in Tiruzia’s Alhamia Prison, as well as journalist Durke Bataglani, 59, and environmentalist Meggie Tazbah, 53, who also holds Bratinas nationality.

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
    <entity_description>Aurelian who spent time in Tiruzia’s Alhamia Prison.</entity_description>
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
```
</details>

<details>
<summary>2. Gleaning</summary>

```
A source text is provided below, along with the entities and relationships extracted from it in XML format. However, some entities or relationships might be missing. Please identify and list the missing ones if any using the same format. Ensure that only entities and relationships explicitly mentioned in the source text are added. Do not create any additional entities or relationships beyond those mentioned in the text. If you are not able to identify any additional ones, just put the single word NOMORE in your reply, do not add any extra punctuation, characters, or explanations.

== Source Text

{input_text}

== Entities and Relationships

{previous_output}

== Important Reminder

If you find any missing entities or relationships, add them using the exact same tags as the provided XML format. Do not create new XML tags beyond those in the provided example.
```
</details>

<details>
<summary>3.	Invalid entity removal</summary>

```
A source text and a list of entities are provided below. Identify all entities whose <entity_name> appears in the source text. Return only the matching entities in their original xml format.

== Source Text

{input_text}

== Entities

{entities}

== Important Reminder

You must output the entities in their original XML format.
```
</details>

<details>
<summary>4.	Summarize description for entity</summary>

```
You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given an entity and a list of descriptions related to it, combine all the information into a single, comprehensive description. Include all relevant details from the provided descriptions.
If any descriptions are contradictory, resolve the contradictions to provide a coherent summary.
Ensure each piece of information is accurately represented and avoid combining separate details incorrectly. Verify each description independently to avoid incorrect merging.
Don’t make anything up in the summary.
Ensure the summary is written in the third person and includes the entity name for full context.
The response should only contain the summary content. Do not include any introductory phrases like “Here is a comprehensive summary” or notes such as “I have combined all relevant information”.

== Data
Entity:
{entity_name}

Description List:
{description_list}
```

<details>
<summary>5.	Generate community report</summary>

```
You are provided with the text below. Your task is to compile a comprehensive report aimed at equipping decision-makers with essential insights. An insight is a deep understanding derived from data analysis that uncovers patterns, explains underlying reasons, and highlights the significance of the data. Do not add any information that cannot be directly derived from the text. Do not use meta keywords such as “text”, “net,” “network,” “entity,” “relationship,” or “insight” in your response.

Report Requirements: 

Title: The report must have a concise title that reflects its contents. Include the names of key entities where applicable. Avoid generic titles such as “Insight into…” or similar phrases.

Summary: Provide an executive summary of the insights. Present the summary in a clear and direct manner.

Insights: List and explain the insights derived from the text. Provide a heading for each insight. Do not include the word “insight” in the headings or explanations.

=== Text

{input_text}
```
</details>
