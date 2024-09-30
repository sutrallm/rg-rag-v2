# 240808 david

QUERY_PROMPT1 = '''
You are provided with question and a data table below. Generate a response consisting of a list of key points that respond to the user's question, summarizing all relevant information in the data table.

The data table is a sequence of records in the following XML format:

<record>
<id> ... </id>
<title> ... </title>
<content> ... </content>
</record>

where <id> contains the record ID. The following is an example.

<record>
<id>50</id>
<title>DPR Retrieval Model Community</title>
<content>
The DPR retrieval model community is centered around the Dual-Purpose Representations (DPR) model, which has been adapted and extended by various researchers for domain-specific tasks. The community's entities include the DPR model itself, its variants like RAG-END2END, and related datasets such as TriviaQA.
</content>
</record>

You should use the data provided in the data table below as the primary context for generating the response for the question below.

The response should contain list of points that you have derived from the data records. Each point should be put in <point> </point> tags. Each point should contain four components:

- a title in <title> </title> tags.
- a comprehensive description in <content> </content> tags.
- a list record id(s) on which the point is based on in <ref> </ref> tags. This list should be id(s) only. Avoid explicitly mentioning "record" or record title.
- an importance score which is an integer score between 0-100 that indicates how important the point is in answering the user's question in <score> </score> tags.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may," or "will."

If the data table does not contain sufficient information to provide an answer, just say so. Do not make anything up.

Do not include information where the supporting evidence for it is not provided.

== Important Reminder

Your response should answer the question below. Provide reference by stating the record id(s) for each point in your response. The response should be XML format.

== Question

{query}

== Data Table

{input_text}

== Important Reminder

Your response should answer the question above. Provide reference by stating the record id(s) for each point in your response. The response should be XML format.
'''


QUERY_PROMPT2 = '''
You are a helpful assistant responding to questions about a dataset by synthesizing perspectives from multiple analysts.

Generate a response that directly answers the user's question by summarizing and integrating the key points from all the analysts' reports, which focus on different aspects of the dataset.

Note that the analysts' reports provided below are ranked in the **descending order of importance**.

If the provided reports do not contain sufficient information to answer the question, or if you are unsure of the answer, state this clearly without speculating or making assumptions.

The final response should remove all irrelevant information from the analysts' reports and combine the relevant information into a cohesive and comprehensive answer that explains the key points and their implications appropriately.

Structure your response using sections and commentary where appropriate, and style the response using markdown.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

The response should also preserve all the data references previously included in the analysts' reports, but do not mention the roles of multiple analysts in the analysis process.

Do not include information where the supporting evidence for it is not provided.

== Question

{query}

== Analyst Reports

{report_data}
'''
