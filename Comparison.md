#	Raptor vs Raptor in RG-RAG

###	Implementation

<table>
<tbody>
<tr valign="top">
<td>
</td>
<td>
<strong>Raptor</strong><br />
</td>
<td>
<strong>Raptor in RG-RAG</strong><br />
</td>
</tr>
<tr valign="top">
<td>
Model<br />
</td>
<td>
OpenAI model<br />
</td>
<td>
llama3.1 8b bf16<br />
</td>
</tr>
<tr valign="top">
<td>
Database<br />
</td>
<td>
Provide an option to save the chunks and summary chunks to a file by pickle.dump<br />
</td>
<td>
ChromaDB<br />
</td>
</tr>
<tr valign="top">
<td>
Denoise<br />
</td>
<td>
No denoise step<br />
</td>
<td>
Denoise each base chunk<br />
</td>
</tr>
<tr valign="top">
<td>
Chunking method<br />
</td>
<td>
max_tokens=100 for each chunk<br />
</td>
<td>
1. Split the denoised text into points:<br />
If there are blank lines, use a blank line ("\n\n") as the delimiter.<br />
If there are no blank lines, use "#" as the delimiter.<br />
Each split text segment is considered a point, and the number of tokens for each point is calculated.<br />
2. Combine the points into sub-chunks:<br />
If it is not the last sub-chunk, each sub-chunk must contain at least 300 tokens and should not overlap.<br />
Sub-chunks share the same chunk ID as the base chunk.<br />
</td>
</tr>
<tr valign="top">
<td>
Summary tree<br />
</td>
<td>
Stop when reaching 5 layers or can not get clusters any more<br />
</td>
<td>
Stop when we get only 1 root summary<br />
</td>
</tr>
<tr valign="top">
<td>
Number of query chunks<br />
</td>
<td>
10<br />
</td>
<td>
20<br />
</td>
</tr>
<tr valign="top">
<td>
Index<br />
</td>
<td>
1. Read the original texts and split them into chunks, with a maximum of 100 tokens each.<br />
2. Generate embeddings for the chunks and reduce the embedding dimensions.<br />
3. Compare the reduced embeddings and generate clusters for the chunks.<br />
4. Summarize each cluster.<br />
5. Repeat steps 2&ndash;4 until reaching five layers or until no more clusters can be formed.<br />
6. (Optional) Save the chunks and summary chunks to a file using pickle.dump.<br />
</td>
<td>
1. Denoise each base chunk and split the denoised text into sub-chunks.<br />
2. Generate embeddings for the chunks and reduce the embedding dimensions.<br />
3. Compare the reduced embeddings and generate clusters for the chunks.<br />
4. Summarize each cluster.<br />
5. Repeat steps 2&ndash;4 until only one root chunk remains.<br />
6. Repeat steps 1&ndash;5 for each group.<br />
7. Save the chunks and summary chunks to ChromaDB. Summary chunks should include the source chunk ID or summary chunk ID, which can be stored in ChromaDB for subsequent retrieval.<br />
</td>
</tr>
<tr valign="top">
<td>
Query<br />
</td>
<td>
1. Retrieve 10 potential chunks.<br />
2. Combine the retrieved text to form the context.<br />
3. Pass the context and the question to the prompt to generate the answer.<br />
</td>
<td>
1. Retrieve 20 potential chunks from all base chunks and summary chunks.<br />
2. The first prompt extracts relevant points from each chunk.<br />
3. Use a program to process the first output and generate the input text for the second prompt.<br />
4. The second prompt provides an answer based on all relevant points.<br />
5. Use a program to list the file names and group names of the relevant chunks.<br />
6. Use a program to combine the second answer with the relevant names to generate the final answer.<br />
</td>
</tr>
</tbody>
</table>

### Prompt

<table>
<tbody>
<tr valign="top">
<td>
</td>
<td>
<strong>Raptor</strong><br />
</td>
<td>
<strong>Raptor in RG-RAG</strong><br />
</td>
</tr>
<tr valign="top">
<td>
Summary prompt<br />
</td>
<td>
Write a summary of the following, including as many key details as possible: {context}:<br />
</td>
<td>
Prompt 1: Generate summary text<br />
Summarize the following text in bullet points without any reference to tables or figures. The summary needs to be self-contained. Don&rsquo;t mention that it is a summary. Put a blank line between the bullets.<br />
&lt;text&gt;<br />
{text}<br />
&lt;/text&gt;<br />
Prompt 2: Refine summary text<br />
Please refine the following text to eliminate any redundant or repetitive descriptions. Ensure the result is concise, clear, and free of unnecessary details while preserving key points. Organize the information in bullet points, with a blank line between each. Present the output in a logical order, prioritizing clarity and brevity. Output only the refined text without any introductory remarks. Do not mention &ldquo;Here is the refined text&rdquo; in your response.<br />
&lt;text&gt;<br />
{text}<br />
&lt;/text&gt;<br />
Prompt 3: Add heading<br />
Please provide a concise and descriptive heading that captures the core theme of the following text. Output only the heading text.<br />
&lt;text&gt;<br />
{text}<br />
&lt;/text&gt;<br />
Program: Combine summary text and heading as the final summary<br />
&lt;heading&gt;heading text from step 3&lt;/heading&gt;<br />
summary text from step 2<br />
</td>
</tr>
<tr valign="top">
<td>
Query prompt<br />
</td>
<td>
Given Context: {context} Give the best full answer amongst the option to question {question}<br />
</td>
<td>
Prompt 1: Extract relevant points for each chunk<br/> You are provided with a question and a piece of text below. Please determine whether the text is relevant to the question. Indicate your answer by putting yes or no within &lt;relevant&gt; &lt;/relevant&gt; tags. If the text is relevant, extract the relevant information in bullet points, placing the bullets within &lt;info&gt; &lt;/info&gt; tags. Add a blank line between each bullet. Do not mention the source of information or &ldquo;the text&rdquo; in your response. Put a heading for the relevant nformation. The heading should be in &lt;heading&gt;&lt;/heading&gt; tags and within &lt;info&gt; &lt;/info&gt; tags.<br/> <br/> &lt;question&gt;<br/> {question}<br/> &lt;/question&gt;<br/> <br/> &lt;text&gt;<br/> {context}<br/> &lt;/text&gt;<br />
<br/> Prompt 2: Consolidate all relevant points to generate the final answer<br />
You are provided with a question and some pieces of information below. Please provide a structured answer to the question based on the given information. Do not mention that your answer is based on these information. Provide as much detail in the answer as possible.<br />
&lt;question&gt;<br />
{question}<br />
&lt;/question&gt;<br />
{context}<br />
</td>
</tr>
</tbody>
</table>

# GraphRAG vs GraphRAG in RG-RAG

### Implementaton

<table>
<tbody>
<tr valign="top">
<td>
</td>
<td>
<strong>GraphRAG</strong><br />
</td>
<td>
<strong>GraphRAG in RG-RAG</strong><br />
</td>
</tr>
<tr valign="top">
<td>
Model<br />
</td>
<td>
OpenAI model<br />
</td>
<td>
llama3.1 8b bf16 and deepseek-r1 8b bf16<br />
</td>
</tr>
<tr valign="top">
<td>
Database<br />
</td>
<td>
Parquet<br />
</td>
<td>
ChromaDB<br />
</td>
</tr>
<tr valign="top">
<td>
Denoise<br />
</td>
<td>
No denoise step<br />
</td>
<td>
Denoise each base chunk<br />
</td>
</tr>
<tr valign="top">
<td>
Chunking method<br />
</td>
<td>
max_tokens=300, overlap=100 for each chunk<br />
</td>
<td>
1. Split the denoised text into points:<br />
If there are blank lines, use a blank line ("\n\n") as the delimiter.<br />
If there are no blank lines, use "#" as the delimiter.<br />
Each split text segment is considered a point, and the number of tokens for each point is calculated.<br />
2. Combine the points into sub-chunks:<br />
If it is not the last sub-chunk, each sub-chunk must contain at least 300 tokens and should not overlap.<br />
Sub-chunks share the same chunk ID as the base chunk.<br />
</td>
</tr>
<tr valign="top">
<td>
Data format for llm<br />
</td>
<td>
JSON<br />
</td>
<td>
XML<br />
</td>
</tr>
<tr valign="top">
<td>
Number of community reports for query<br />
</td>
<td>
Go through all community reports<br />
</td>
<td>
Use similarity search to get top 20 community reports<br />
</td>
</tr>
<tr valign="top">
<td>
Query step 1<br />
</td>
<td>
Limit max_tokens=1000 for each request to split all community reports into different batches. Extract relevant points for each batch using 1 prompt per batch.<br />
</td>
<td>
We firstly try to extract the relevant information for each report using 1 prompt per report.<br />
</td>
</tr>
<tr valign="top">
<td>
Query step 2<br />
</td>
<td>
Sort the relevant points from step 1 by predicted score and limit max_tokens=2000 to get the top number of points. Summarize the points to get the final answer.<br />
</td>
<td>
Summarize all relevant points from step 1 to get the final answer.<br />
</td>
</tr>
</tbody>
</table>

### Prompt

<table>
<tbody>

<tr valign="top">
<td>
</td>
<td>
<strong>GraphRAG</strong><br />
</td>
</tr>
<tr valign="top">
<td>
Index prompt1<br />
</td>
<td>
-Goal-<br />
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.<br />
-Steps-<br />
1. Identify all entities. For each identified entity, extract the following information:<br />
- entity_name: Name of the entity, capitalized<br />
- entity_type: One of the following types: [{entity_types}]<br />
- entity_description: Comprehensive description of the entity's attributes and activities<br />
Format each entity as ("entity"{tuple_delimiter}&lt;entity_name&gt;{tuple_delimiter}&lt;entity_type&gt;{tuple_delimiter}&lt;entity_description&gt;)<br />
2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.<br />
For each pair of related entities, extract the following information:<br />
- source_entity: name of the source entity, as identified in step 1<br />
- target_entity: name of the target entity, as identified in step 1<br />
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other<br />
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity<br />
Format each relationship as ("relationship"{tuple_delimiter}&lt;source_entity&gt;{tuple_delimiter}&lt;target_entity&gt;{tuple_delimiter}&lt;relationship_description&gt;{tuple_delimiter}&lt;relationship_strength&gt;)<br />
3. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.<br />
4. When finished, output {completion_delimiter}<br />
######################<br />
-Examples-<br />
######################<br />
Example 1:<br />
Entity_types: ORGANIZATION,PERSON<br />
Text:<br />
The Verdantis's Central Institution is scheduled to meet on Monday and Thursday, with the institution planning to release its latest policy decision on Thursday at 1:30 p.m. PDT, followed by a press conference where Central Institution Chair Martin Smith will take questions. Investors expect the Market Strategy Committee to hold its benchmark interest rate steady in a range of 3.5%-3.75%.<br />
######################<br />
Output:<br />
("entity"{tuple_delimiter}CENTRAL INSTITUTION{tuple_delimiter}ORGANIZATION{tuple_delimiter}The Central Institution is the Federal Reserve of Verdantis, which is setting interest rates on Monday and Thursday)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}MARTIN SMITH{tuple_delimiter}PERSON{tuple_delimiter}Martin Smith is the chair of the Central Institution)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}MARKET STRATEGY COMMITTEE{tuple_delimiter}ORGANIZATION{tuple_delimiter}The Central Institution committee makes key decisions about interest rates and the growth of Verdantis's money supply)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}MARTIN SMITH{tuple_delimiter}CENTRAL INSTITUTION{tuple_delimiter}Martin Smith is the Chair of the Central Institution and will answer questions at a press conference{tuple_delimiter}9)<br />
{completion_delimiter}<br />
######################<br />
Example 2:<br />
Entity_types: ORGANIZATION<br />
Text:<br />
TechGlobal's (TG) stock skyrocketed in its opening day on the Global Exchange Thursday. But IPO experts warn that the semiconductor corporation's debut on the public markets isn't indicative of how other newly listed companies may perform.<br />
TechGlobal, a formerly public company, was taken private by Vision Holdings in 2014. The well-established chip designer says it powers 85% of premium smartphones.<br />
######################<br />
Output:<br />
("entity"{tuple_delimiter}TECHGLOBAL{tuple_delimiter}ORGANIZATION{tuple_delimiter}TechGlobal is a stock now listed on the Global Exchange which powers 85% of premium smartphones)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}VISION HOLDINGS{tuple_delimiter}ORGANIZATION{tuple_delimiter}Vision Holdings is a firm that previously owned TechGlobal)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}TECHGLOBAL{tuple_delimiter}VISION HOLDINGS{tuple_delimiter}Vision Holdings formerly owned TechGlobal from 2014 until present{tuple_delimiter}5)<br />
{completion_delimiter}<br />
######################<br />
Example 3:<br />
Entity_types: ORGANIZATION,GEO,PERSON<br />
Text:<br />
Five Aurelians jailed for 8 years in Firuzabad and widely regarded as hostages are on their way home to Aurelia.<br />
The swap orchestrated by Quintara was finalized when $8bn of Firuzi funds were transferred to financial institutions in Krohaara, the capital of Quintara.<br />
The exchange initiated in Firuzabad's capital, Tiruzia, led to the four men and one woman, who are also Firuzi nationals, boarding a chartered flight to Krohaara.<br />
They were welcomed by senior Aurelian officials and are now on their way to Aurelia's capital, Cashion.<br />
The Aurelians include 39-year-old businessman Samuel Namara, who has been held in Tiruzia's Alhamia Prison, as well as journalist Durke Bataglani, 59, and environmentalist Meggie Tazbah, 53, who also holds Bratinas nationality.<br />
######################<br />
Output:<br />
("entity"{tuple_delimiter}FIRUZABAD{tuple_delimiter}GEO{tuple_delimiter}Firuzabad held Aurelians as hostages)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}AURELIA{tuple_delimiter}GEO{tuple_delimiter}Country seeking to release hostages)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}QUINTARA{tuple_delimiter}GEO{tuple_delimiter}Country that negotiated a swap of money in exchange for hostages)<br />
{record_delimiter}<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}TIRUZIA{tuple_delimiter}GEO{tuple_delimiter}Capital of Firuzabad where the Aurelians were being held)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}KROHAARA{tuple_delimiter}GEO{tuple_delimiter}Capital city in Quintara)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}CASHION{tuple_delimiter}GEO{tuple_delimiter}Capital city in Aurelia)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}PERSON{tuple_delimiter}Aurelian who spent time in Tiruzia's Alhamia Prison)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}ALHAMIA PRISON{tuple_delimiter}GEO{tuple_delimiter}Prison in Tiruzia)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}PERSON{tuple_delimiter}Aurelian journalist who was held hostage)<br />
{record_delimiter}<br />
("entity"{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}PERSON{tuple_delimiter}Bratinas national and environmentalist who was held hostage)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}FIRUZABAD{tuple_delimiter}AURELIA{tuple_delimiter}Firuzabad negotiated a hostage exchange with Aurelia{tuple_delimiter}2)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}QUINTARA{tuple_delimiter}AURELIA{tuple_delimiter}Quintara brokered the hostage exchange between Firuzabad and Aurelia{tuple_delimiter}2)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}QUINTARA{tuple_delimiter}FIRUZABAD{tuple_delimiter}Quintara brokered the hostage exchange between Firuzabad and Aurelia{tuple_delimiter}2)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}ALHAMIA PRISON{tuple_delimiter}Samuel Namara was a prisoner at Alhamia prison{tuple_delimiter}8)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}Samuel Namara and Meggie Tazbah were exchanged in the same hostage release{tuple_delimiter}2)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}Samuel Namara and Durke Bataglani were exchanged in the same hostage release{tuple_delimiter}2)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}Meggie Tazbah and Durke Bataglani were exchanged in the same hostage release{tuple_delimiter}2)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}FIRUZABAD{tuple_delimiter}Samuel Namara was a hostage in Firuzabad{tuple_delimiter}2)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}FIRUZABAD{tuple_delimiter}Meggie Tazbah was a hostage in Firuzabad{tuple_delimiter}2)<br />
{record_delimiter}<br />
("relationship"{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}FIRUZABAD{tuple_delimiter}Durke Bataglani was a hostage in Firuzabad{tuple_delimiter}2)<br />
{completion_delimiter}<br />
######################<br />
-Real Data-<br />
######################<br />
Entity_types: {entity_types}<br />
Text: {input_text}<br />
######################<br />
Output:<br />
</td>
</tr>
<tr valign="top">
<td>
Index prompt2<br />
</td>
<td>
You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.<br />
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.<br />
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.<br />
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.<br />
Make sure it is written in third person, and include the entity names so we have the full context.<br />
#######<br />
-Data-<br />
Entities: {entity_name}<br />
Description List: {description_list}<br />
#######<br />
Output:<br />
</td>
</td>
</tr>
<tr valign="top">
<td>
Index prompt3<br />
</td>
<td>
You are an AI assistant that helps a human analyst to perform general information discovery. Information discovery is the process of identifying and assessing relevant information associated with certain entities (e.g., organizations and individuals) within a network.<br />
# Goal<br />
Write a comprehensive report of a community, given a list of entities that belong to the community as well as their relationships and optional associated claims. The report will be used to inform decision-makers about information associated with the community and their potential impact. The content of this report includes an overview of the community's key entities, their legal compliance, technical capabilities, reputation, and noteworthy claims.<br />
# Report Structure<br />
The report should include the following sections:<br />
- TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.<br />
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.<br />
- IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community. IMPACT is the scored importance of a community.<br />
- RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.<br />
- DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.<br />
Return output as a well-formed JSON-formatted string with the following format:<br />
 {{<br />
 "title": &lt;report_title&gt;,<br />
 "summary": &lt;executive_summary&gt;,<br />
 "rating": &lt;impact_severity_rating&gt;,<br />
 "rating_explanation": &lt;rating_explanation&gt;,<br />
 "findings": [<br />
 {{<br />
 "summary":&lt;insight_1_summary&gt;,<br />
 "explanation": &lt;insight_1_explanation&gt;<br />
 }},<br />
 {{<br />
 "summary":&lt;insight_2_summary&gt;,<br />
 "explanation": &lt;insight_2_explanation&gt;<br />
 }}<br />
 ]<br />
 }}<br />
# Grounding Rules<br />
Points supported by data should list their data references as follows:<br />
"This is an example sentence supported by multiple data references [Data: &lt;dataset name&gt; (record ids); &lt;dataset name&gt; (record ids)]."<br />
Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.<br />
For example:<br />
"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."<br />
where 1, 5, 7, 23, 2, 34, 46, and 64 represent the id (not the index) of the relevant data record.<br />
Do not include information where the supporting evidence for it is not provided.<br />
# Example Input<br />
-----------<br />
Text:<br />
Entities<br />
id,entity,description<br />
5,VERDANT OASIS PLAZA,Verdant Oasis Plaza is the location of the Unity March<br />
6,HARMONY ASSEMBLY,Harmony Assembly is an organization that is holding a march at Verdant Oasis Plaza<br />
Relationships<br />
id,source,target,description<br />
37,VERDANT OASIS PLAZA,UNITY MARCH,Verdant Oasis Plaza is the location of the Unity March<br />
38,VERDANT OASIS PLAZA,HARMONY ASSEMBLY,Harmony Assembly is holding a march at Verdant Oasis Plaza<br />
39,VERDANT OASIS PLAZA,UNITY MARCH,The Unity March is taking place at Verdant Oasis Plaza<br />
40,VERDANT OASIS PLAZA,TRIBUNE SPOTLIGHT,Tribune Spotlight is reporting on the Unity march taking place at Verdant Oasis Plaza<br />
41,VERDANT OASIS PLAZA,BAILEY ASADI,Bailey Asadi is speaking at Verdant Oasis Plaza about the march<br />
43,HARMONY ASSEMBLY,UNITY MARCH,Harmony Assembly is organizing the Unity March<br />
Output:<br />
{{<br />
 "title": "Verdant Oasis Plaza and Unity March",<br />
 "summary": "The community revolves around the Verdant Oasis Plaza, which is the location of the Unity March. The plaza has relationships with the Harmony Assembly, Unity March, and Tribune Spotlight, all of which are associated with the march event.",<br />
 "rating": 5.0,<br />
 "rating_explanation": "The impact severity rating is moderate due to the potential for unrest or conflict during the Unity March.",<br />
 "findings": [<br />
 {{<br />
 "summary": "Verdant Oasis Plaza as the central location",<br />
 "explanation": "Verdant Oasis Plaza is the central entity in this community, serving as the location for the Unity March. This plaza is the common link between all other entities, suggesting its significance in the community. The plaza's association with the march could potentially lead to issues such as public disorder or conflict, depending on the nature of the march and the reactions it provokes. [Data: Entities (5), Relationships (37, 38, 39, 40, 41,+more)]"<br />
 }},<br />
 {{<br />
 "summary": "Harmony Assembly's role in the community",<br />
 "explanation": "Harmony Assembly is another key entity in this community, being the organizer of the march at Verdant Oasis Plaza. The nature of Harmony Assembly and its march could be a potential source of threat, depending on their objectives and the reactions they provoke. The relationship between Harmony Assembly and the plaza is crucial in understanding the dynamics of this community. [Data: Entities(6), Relationships (38, 43)]"<br />
 }},<br />
 {{<br />
 "summary": "Unity March as a significant event",<br />
 "explanation": "The Unity March is a significant event taking place at Verdant Oasis Plaza. This event is a key factor in the community's dynamics and could be a potential source of threat, depending on the nature of the march and the reactions it provokes. The relationship between the march and the plaza is crucial in understanding the dynamics of this community. [Data: Relationships (39)]"<br />
 }},<br />
 {{<br />
 "summary": "Role of Tribune Spotlight",<br />
 "explanation": "Tribune Spotlight is reporting on the Unity March taking place in Verdant Oasis Plaza. This suggests that the event has attracted media attention, which could amplify its impact on the community. The role of Tribune Spotlight could be significant in shaping public perception of the event and the entities involved. [Data: Relationships (40)]"<br />
 }}<br />
 ]<br />
}}<br />
# Real Data<br />
Use the following text for your answer. Do not make anything up in your answer.<br />
Text:<br />
{input_text}<br />
The report should include the following sections:<br />
- TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.<br />
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.<br />
- IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community. IMPACT is the scored importance of a community.<br />
- RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.<br />
- DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.<br />
Return output as a well-formed JSON-formatted string with the following format:<br />
 {{<br />
 "title": &lt;report_title&gt;,<br />
 "summary": &lt;executive_summary&gt;,<br />
 "rating": &lt;impact_severity_rating&gt;,<br />
 "rating_explanation": &lt;rating_explanation&gt;,<br />
 "findings": [<br />
 {{<br />
 "summary":&lt;insight_1_summary&gt;,<br />
 "explanation": &lt;insight_1_explanation&gt;<br />
 }},<br />
 {{<br />
 "summary":&lt;insight_2_summary&gt;,<br />
 "explanation": &lt;insight_2_explanation&gt;<br />
 }}<br />
 ]<br />
 }}<br />
# Grounding Rules<br />
Points supported by data should list their data references as follows:<br />
"This is an example sentence supported by multiple data references [Data: &lt;dataset name&gt; (record ids); &lt;dataset name&gt; (record ids)]."<br />
Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.<br />
For example:<br />
"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."<br />
where 1, 5, 7, 23, 2, 34, 46, and 64 represent the id (not the index) of the relevant data record.<br />
Do not include information where the supporting evidence for it is not provided.<br />
Output:<br />
</td>
</tr>
<tr valign="top">
<td>
Query prompt1<br />
</td>
<td>
---Role---<br />
You are a helpful assistant responding to questions about data in the tables provided.<br />
---Goal---<br />
Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.<br />
You should use the data provided in the data tables below as the primary context for generating the response.<br />
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.<br />
Each key point in the response should have the following element:<br />
- Description: A comprehensive description of the point.<br />
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.<br />
The response should be JSON formatted as follows:<br />
{{<br />
 "points": [<br />
 {{"description": "Description of point 1 [Data: Reports (report ids)]", "score": score_value}},<br />
 {{"description": "Description of point 2 [Data: Reports (report ids)]", "score": score_value}}<br />
 ]<br />
}}<br />
The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".<br />
Points supported by data should list the relevant reports as references as follows:<br />
"This is an example sentence supported by data references [Data: Reports (report ids)]"<br />
**Do not list more than 5 record ids in a single reference**. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.<br />
For example:<br />
"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (2, 7, 64, 46, 34, +more)]. He is also CEO of company X [Data: Reports (1, 3)]"<br />
where 1, 2, 3, 7, 34, 46, and 64 represent the id (not the index) of the relevant data report in the provided tables.<br />
Do not include information where the supporting evidence for it is not provided.<br />
---Data tables---<br />
{context_data}<br />
---Goal---<br />
Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.<br />
You should use the data provided in the data tables below as the primary context for generating the response.<br />
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.<br />
Each key point in the response should have the following element:<br />
- Description: A comprehensive description of the point.<br />
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.<br />
The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".<br />
Points supported by data should list the relevant reports as references as follows:<br />
"This is an example sentence supported by data references [Data: Reports (report ids)]"<br />
**Do not list more than 5 record ids in a single reference**. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.<br />
For example:<br />
"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (2, 7, 64, 46, 34, +more)]. He is also CEO of company X [Data: Reports (1, 3)]"<br />
where 1, 2, 3, 7, 34, 46, and 64 represent the id (not the index) of the relevant data report in the provided tables.<br />
Do not include information where the supporting evidence for it is not provided.<br />
The response should be JSON formatted as follows:<br />
{{<br />
 "points": [<br />
 {{"description": "Description of point 1 [Data: Reports (report ids)]", "score": score_value}},<br />
 {{"description": "Description of point 2 [Data: Reports (report ids)]", "score": score_value}}<br />
 ]<br />
}}<br />
</td>
</tr>
<tr valign="top">
<td>
Query prompt2<br />
</td>
<td>
---Role---<br />
You are a helpful assistant responding to questions about data in the tables provided.<br />
---Goal---<br />
Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.<br />
You should use the data provided in the data tables below as the primary context for generating the response.<br />
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.<br />
Each key point in the response should have the following element:<br />
- Description: A comprehensive description of the point.<br />
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.<br />
The response should be JSON formatted as follows:<br />
{{<br />
 "points": [<br />
 {{"description": "Description of point 1 [Data: Reports (report ids)]", "score": score_value}},<br />
 {{"description": "Description of point 2 [Data: Reports (report ids)]", "score": score_value}}<br />
 ]<br />
}}<br />
The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".<br />
Points supported by data should list the relevant reports as references as follows:<br />
"This is an example sentence supported by data references [Data: Reports (report ids)]"<br />
**Do not list more than 5 record ids in a single reference**. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.<br />
For example:<br />
"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (2, 7, 64, 46, 34, +more)]. He is also CEO of company X [Data: Reports (1, 3)]"<br />
where 1, 2, 3, 7, 34, 46, and 64 represent the id (not the index) of the relevant data report in the provided tables.<br />
Do not include information where the supporting evidence for it is not provided.<br />
---Data tables---<br />
{context_data}<br />
---Goal---<br />
Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.<br />
You should use the data provided in the data tables below as the primary context for generating the response.<br />
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.<br />
Each key point in the response should have the following element:<br />
- Description: A comprehensive description of the point.<br />
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.<br />
The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".<br />
Points supported by data should list the relevant reports as references as follows:<br />
"This is an example sentence supported by data references [Data: Reports (report ids)]"<br />
**Do not list more than 5 record ids in a single reference**. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.<br />
For example:<br />
"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (2, 7, 64, 46, 34, +more)]. He is also CEO of company X [Data: Reports (1, 3)]"<br />
where 1, 2, 3, 7, 34, 46, and 64 represent the id (not the index) of the relevant data report in the provided tables.<br />
Do not include information where the supporting evidence for it is not provided.<br />
The response should be JSON formatted as follows:<br />
{{<br />
 "points": [<br />
 {{"description": "Description of point 1 [Data: Reports (report ids)]", "score": score_value}},<br />
 {{"description": "Description of point 2 [Data: Reports (report ids)]", "score": score_value}}<br />
 ]<br />
}}<br />
</td>
</tr>
</table>

<table>
<tr valign="top">
<td>
</td>
<td>
<strong>GraphRAG in RG-RAG</strong><br />
</td>
</tr>
<tr valign="top">
<td>
Index prompt1<br />
</td>
<td>
== Goal<br/> Given a text document that is potentially relevant to this activity, first identify all necessary entities from the text to capture the information and ideas presented. Next, report all relationships among the identified entities.<br/> <br/> == Steps<br/> 1. Identify all entities. For each identified entity, extract the following information:<br/> - entity_name: Name of the entity, capitalized<br/> - entity_type: Suggest several labels or categories for the entity. The categories should not be specific, but should be as general as possible.<br/> - entity_description: A comprehensive description of the entity's attributes and activities<br/> Each entity should be XML formatted as follows:<br/> <br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;entity_name&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;entity_type&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;entity_description&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> <br/> 2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.<br/> For each pair of related entities, extract the following information:<br/> - source_entity: name of the source entity, as identified in step 1<br/> - target_entity: name of the target entity, as identified in step 1<br/> - relationship_description: explanation as to why you think the source entity and the target entity are related to each other<br/> - relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity<br/> Each relationship should be XML formatted as follows:<br/> <br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;source_entity&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;target_entity&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;relationship_description&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;relationship_strength&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> <br/> == Example 1:<br/> Text:<br/> The Verdantis's Central Institution is scheduled to meet on Monday and Thursday, with the institution planning to release its latest policy decision on Thursday at 1:30 p.m. PDT, followed by a press conference where Central Institution Chair Martin Smith will take questions. Investors expect the Market Strategy Committee to hold its benchmark interest rate steady in a range of 3.5%-3.75%.<br/> <br/> Output:<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;CENTRAL INSTITUTION&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;ORGANIZATION&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;The Central Institution is the Federal Reserve of Verdantis, which is setting interest rates on Monday and Thursday.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;MARTIN SMITH&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;PERSON&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Martin Smith is the chair of the Central Institution.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;MARKET STRATEGY COMMITTEE&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;ORGANIZATION&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;The Central Institution committee makes key decisions about interest rates and the growth of Verdantis's money supply.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;MARTIN SMITH&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;CENTRAL INSTITUTION&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Martin Smith is the Chair of the Central Institution and will answer questions at a press conference.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;9&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> <br/> == Example 2:<br/> Text:<br/> TechGlobal's (TG) stock skyrocketed in its opening day on the Global Exchange Thursday. But IPO experts warn that the semiconductor corporation's debut on the public markets isn't indicative of how other newly listed companies may perform.<br/> <br/> TechGlobal, a formerly public company, was taken private by Vision Holdings in 2014. The well-established chip designer says it powers 85% of premium smartphones.<br/> <br/> Output:<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;TECHGLOBAL&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;ORGANIZATION&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;TechGlobal is a stock now listed on the Global Exchange which powers 85% of premium smartphones.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;VISION HOLDINGS&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;ORGANIZATION&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Vision Holdings is a firm that previously owned TechGlobal.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;TECHGLOBAL&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;VISION HOLDINGS&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Vision Holdings formerly owned TechGlobal from 2014 until present.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;5&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> <br/> == Example 3:<br/> Text:<br/> Five Aurelians jailed for 8 years in Firuzabad and widely regarded as hostages are on their way home to Aurelia.<br/> <br/> The swap orchestrated by Quintara was finalized when $8bn of Firuzi funds were transferred to financial institutions in Krohaara, the capital of Quintara.<br/> <br/> The exchange initiated in Firuzabad's capital, Tiruzia, led to the four men and one woman, who are also Firuzi nationals, boarding a chartered flight to Krohaara.<br/> <br/> They were welcomed by senior Aurelian officials and are now on their way to Aurelia's capital, Cashion.<br/> <br/> The Aurelians include 39-year-old businessman Samuel Namara, who has been held in Tiruzia's Alhamia Prison, as well as journalist Durke Bataglani, 59, and environmentalist Meggie Tazbah, 53, who also holds Bratinas nationality.<br/> <br/> Output:<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;FIRUZABAD&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;GEO&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Firuzabad held Aurelians as hostages.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;AURELIA&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;GEO&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Country seeking to release hostages.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;QUINTARA&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;GEO&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Country that negotiated a swap of money in exchange for hostages.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;TIRUZIA&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;GEO&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Capital of Firuzabad where the Aurelians were being held.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;KROHAARA&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;GEO&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Capital city in Quintara.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;CASHION&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;GEO&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Capital city in Aurelia.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;SAMUEL NAMARA&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;PERSON&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Aurelian who spent time in Tiruzia's Alhamia Prison.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;ALHAMIA PRISON&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;GEO&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Prison in Tiruzia.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;DURKE BATAGLANI&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;PERSON&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Aurelian journalist who was held hostage.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;entity&gt;<br/>  &lt;entity_name&gt;MEGGIE TAZBAH&lt;/entity_name&gt;<br/>  &lt;entity_type&gt;PERSON&lt;/entity_type&gt;<br/>  &lt;entity_description&gt;Bratinas national and environmentalist who was held hostage.&lt;/entity_description&gt;<br/> &lt;/entity&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;FIRUZABAD&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;AURELIA&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Firuzabad negotiated a hostage exchange with Aurelia.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;2&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;QUINTARA&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;AURELIA&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Quintara brokered the hostage exchange between Firuzabad and Aurelia.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;2&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;QUINTARA&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;FIRUZABAD&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Quintara brokered the hostage exchange between Firuzabad and Aurelia.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;2&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;SAMUEL NAMARA&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;ALHAMIA PRISON&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Samuel Namara was a prisoner at Alhamia prison.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;8&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;SAMUEL NAMARA&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;MEGGIE TAZBAH&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Samuel Namara and Meggie Tazbah were exchanged in the same hostage release.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;2&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;SAMUEL NAMARA&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;DURKE BATAGLANI&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Samuel Namara and Durke Bataglani were exchanged in the same hostage release.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;2&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;MEGGIE TAZBAH&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;DURKE BATAGLANI&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Meggie Tazbah and Durke Bataglani were exchanged in the same hostage release.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;2&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;SAMUEL NAMARA&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;FIRUZABAD&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Samuel Namara was a hostage in Firuzabad.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;2&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;MEGGIE TAZBAH&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;FIRUZABAD&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Meggie Tazbah was a hostage in Firuzabad.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;2&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> &lt;relationship&gt;<br/>  &lt;source_entity&gt;DURKE BATAGLANI&lt;/source_entity&gt;<br/>  &lt;target_entity&gt;FIRUZABAD&lt;/target_entity&gt;<br/>  &lt;relationship_description&gt;Durke Bataglani was a hostage in Firuzabad.&lt;/relationship_description&gt;<br/>  &lt;relationship_strength&gt;2&lt;/relationship_strength&gt;<br/> &lt;/relationship&gt;<br/> <br/> == Real Data<br/> Text:<br/> <br/> {input_text}<br />
</td>
</tr>
<tr valign="top">
<td>
Index prompt2<br />
</td>
<td>
You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.<br/> Given an entity and a list of descriptions related to it, combine all the information into a single, comprehensive description. Include all relevant details from the provided descriptions.<br/> If any descriptions are contradictory, resolve the contradictions to provide a coherent summary.<br/> Ensure each piece of information is accurately represented and avoid combining separate details incorrectly. Verify each description independently to avoid incorrect merging.<br/> Don't make anything up in the summary.<br/> Ensure the summary is written in the third person and includes the entity name for full context.<br/> The response should only contain the summary content. Do not include any introductory phrases like "Here is a comprehensive summary" or notes such as "I have combined all relevant information".<br/> <br/> == Data<br/> Entity:<br/> {entity_name}<br/> <br/> Description List:<br/> {description_list}<br />
</td>
</tr>
<tr valign="top">
<td>
Index prompt3<br />
</td>
<td>
You are provided with the text below. Your task is to compile a comprehensive report aimed at equipping decision-makers with essential insights. An insight is a deep understanding derived from data analysis that uncovers patterns, explains underlying reasons, and highlights the significance of the data. Do not add any information that cannot be directly derived from the text. Do not use meta keywords such as "text", "net," "network," "entity," "relationship," or "insight" in your response.<br />
Report Requirements:<br />
Title: The report must have a concise title that reflects its contents. Include the names of key entities where applicable. Avoid generic titles such as &ldquo;Insight into...&rdquo; or similar phrases.<br />
Summary: Provide an executive summary of the insights. Present the summary in a clear and direct manner.<br />
Insights: List and explain the insights derived from the text. Provide a heading for each insight. Do not include the word "insight" in the headings or explanations.<br />
=== Text<br />
<pre>{input_text}</pre>
</td>
</tr>
<tr valign="top">
<td>
Query prompt1<br />
</td>
<td>
You are provided with a question and a piece of text below. Please determine whether the text is relevant to the question. Indicate your answer by putting yes or no within &lt;relevant&gt; &lt;/relevant&gt; tags. If the text is relevant, extract the relevant information in bullet points, placing the bullets within &lt;info&gt; &lt;/info&gt; tags. Add a blank line between each bullet. Do not mention the source of information or "the text" in your response. Put a heading for the relevant informaton. The heading should be in &lt;heading&gt;&lt;/heading&gt; tags and within &lt;info&gt; &lt;/info&gt; tags.<br/> <br/> &lt;question&gt;<br/> {question}<br/> &lt;/question&gt;<br/> <br/> &lt;text&gt;<br/> {context}<br/> &lt;/text&gt;<br />
</td>
</tr>
<tr valign="top">
<td>
Query prompt2<br />
</td>
<td>
You are provided with a question and some pieces of information below. Please provide a structured answer to the question based on the given information. Do not mention that your answer is based on these information. Provide as much detail in the answer as possible.<br/> <br/> &lt;question&gt;<br/> {question}<br/> &lt;/question&gt;<br/> <br/> {context}<br />
</td>
</tr>

</tbody>
</table>
