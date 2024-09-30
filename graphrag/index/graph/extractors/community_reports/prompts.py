# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License
"""A file containing prompts definition."""

# COMMUNITY_REPORT_PROMPT = """
# You are an AI assistant that helps a human analyst to perform general information discovery. Information discovery is the process of identifying and assessing relevant information associated with certain entities (e.g., organizations and individuals) within a network.
#
# # Goal
# Write a comprehensive report of a community, given a list of entities that belong to the community as well as their relationships and optional associated claims. The report will be used to inform decision-makers about information associated with the community and their potential impact. The content of this report includes an overview of the community's key entities, their legal compliance, technical capabilities, reputation, and noteworthy claims.
#
# # Report Structure
#
# The report should include the following sections:
#
# - TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
# - SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
# - IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
# - RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
# - DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.
#
# Return output as a well-formed JSON-formatted string with the following format:
#     {{
#         "title": <report_title>,
#         "summary": <executive_summary>,
#         "rating": <impact_severity_rating>,
#         "rating_explanation": <rating_explanation>,
#         "findings": [
#             {{
#                 "summary":<insight_1_summary>,
#                 "explanation": <insight_1_explanation>
#             }},
#             {{
#                 "summary":<insight_2_summary>,
#                 "explanation": <insight_2_explanation>
#             }}
#         ]
#     }}
#
# # Grounding Rules
#
# Points supported by data should list their data references as follows:
#
# "This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."
#
# Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.
#
# For example:
# "Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."
#
# where 1, 5, 7, 23, 2, 34, 46, and 64 represent the id (not the index) of the relevant data record.
#
# Do not include information where the supporting evidence for it is not provided.
#
#
# # Example Input
# -----------
# Text:
#
# Entities
#
# id,entity,description
# 5,VERDANT OASIS PLAZA,Verdant Oasis Plaza is the location of the Unity March
# 6,HARMONY ASSEMBLY,Harmony Assembly is an organization that is holding a march at Verdant Oasis Plaza
#
# Relationships
#
# id,source,target,description
# 37,VERDANT OASIS PLAZA,UNITY MARCH,Verdant Oasis Plaza is the location of the Unity March
# 38,VERDANT OASIS PLAZA,HARMONY ASSEMBLY,Harmony Assembly is holding a march at Verdant Oasis Plaza
# 39,VERDANT OASIS PLAZA,UNITY MARCH,The Unity March is taking place at Verdant Oasis Plaza
# 40,VERDANT OASIS PLAZA,TRIBUNE SPOTLIGHT,Tribune Spotlight is reporting on the Unity march taking place at Verdant Oasis Plaza
# 41,VERDANT OASIS PLAZA,BAILEY ASADI,Bailey Asadi is speaking at Verdant Oasis Plaza about the march
# 43,HARMONY ASSEMBLY,UNITY MARCH,Harmony Assembly is organizing the Unity March
#
# Output:
# {{
#     "title": "Verdant Oasis Plaza and Unity March",
#     "summary": "The community revolves around the Verdant Oasis Plaza, which is the location of the Unity March. The plaza has relationships with the Harmony Assembly, Unity March, and Tribune Spotlight, all of which are associated with the march event.",
#     "rating": 5.0,
#     "rating_explanation": "The impact severity rating is moderate due to the potential for unrest or conflict during the Unity March.",
#     "findings": [
#         {{
#             "summary": "Verdant Oasis Plaza as the central location",
#             "explanation": "Verdant Oasis Plaza is the central entity in this community, serving as the location for the Unity March. This plaza is the common link between all other entities, suggesting its significance in the community. The plaza's association with the march could potentially lead to issues such as public disorder or conflict, depending on the nature of the march and the reactions it provokes. [Data: Entities (5), Relationships (37, 38, 39, 40, 41,+more)]"
#         }},
#         {{
#             "summary": "Harmony Assembly's role in the community",
#             "explanation": "Harmony Assembly is another key entity in this community, being the organizer of the march at Verdant Oasis Plaza. The nature of Harmony Assembly and its march could be a potential source of threat, depending on their objectives and the reactions they provoke. The relationship between Harmony Assembly and the plaza is crucial in understanding the dynamics of this community. [Data: Entities(6), Relationships (38, 43)]"
#         }},
#         {{
#             "summary": "Unity March as a significant event",
#             "explanation": "The Unity March is a significant event taking place at Verdant Oasis Plaza. This event is a key factor in the community's dynamics and could be a potential source of threat, depending on the nature of the march and the reactions it provokes. The relationship between the march and the plaza is crucial in understanding the dynamics of this community. [Data: Relationships (39)]"
#         }},
#         {{
#             "summary": "Role of Tribune Spotlight",
#             "explanation": "Tribune Spotlight is reporting on the Unity March taking place in Verdant Oasis Plaza. This suggests that the event has attracted media attention, which could amplify its impact on the community. The role of Tribune Spotlight could be significant in shaping public perception of the event and the entities involved. [Data: Relationships (40)]"
#         }}
#     ]
# }}
#
#
# # Real Data
#
# Use the following text for your answer. Do not make anything up in your answer.
#
# Text:
# {input_text}
#
# The report should include the following sections:
#
# - TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
# - SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
# - IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
# - RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
# - DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.
#
# Return output as a well-formed JSON-formatted string with the following format:
#     {{
#         "title": <report_title>,
#         "summary": <executive_summary>,
#         "rating": <impact_severity_rating>,
#         "rating_explanation": <rating_explanation>,
#         "findings": [
#             {{
#                 "summary":<insight_1_summary>,
#                 "explanation": <insight_1_explanation>
#             }},
#             {{
#                 "summary":<insight_2_summary>,
#                 "explanation": <insight_2_explanation>
#             }}
#         ]
#     }}
#
# # Grounding Rules
#
# Points supported by data should list their data references as follows:
#
# "This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."
#
# Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.
#
# For example:
# "Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."
#
# where 1, 5, 7, 23, 2, 34, 46, and 64 represent the id (not the index) of the relevant data record.
#
# Do not include information where the supporting evidence for it is not provided.
#
# Output:"""

# 240805 new prompt
COMMUNITY_REPORT_PROMPT = '''
You are given an entity net that includes a list of entities and their relationships. As an AI assistant, your task is to help a human analyst extract information from this net. This involves identifying and evaluating data related to various entities, which may be tangible or conceptual, along with their interactions. You will compile a comprehensive report on this entity net, aimed at equipping decision-makers with essential insights into the net’s structure, characteristics, and capabilities. An insight is a deep understanding derived from data analysis that uncovers patterns, elucidates underlying reasons, and emphasizes the significance of the data. Avoid explicitly mentioning meta keywords like "net", "network", "entity", "relationship" and "insight" in your response.

Report Requirements:

Title: The report should have a concise title reflecting the contents of the report. Include names of key entities where possible. You must not put a generic title like “insight into ...”.

Summary: Provide an executive summary that outlines the overall structure of the entity net, the interrelations among its entities, and significant related information.

Impact Severity Rating: Assign a float score between 0-10 indicating the net’s impact severity, where the impact reflects the significance of the entity net.

Rating Explanation: Offer a brief sentence explaining the rationale behind the assigned impact severity rating.

Detailed Findings: List and explain 5-10 major insights about the entity net. Each insight should start with a brief summary followed by a detailed explanation.

Output Format:

Produce the report in XML format with the following structure:

<title>Your Report Title</title>
<summary>Executive summary of the net.</summary>
<rating>Impact severity score.</rating>
<rating_explanation>Explanation for the impact severity score.</rating_explanation>
<findings>
    <insight>
        <insight_summary>Summary of Insight 1</insight_summary>
        <insight_explanation>Detailed explanation of Insight 1.</insight_explanation>
    </insight>
    ...
</findings>


== Example Input and Output

Entities:

<id>5</id><entity>VERDANT OASIS PLAZA</entity><description>Verdant Oasis Plaza is the location of the Unity March</description>

<id>6</id><entity>HARMONY ASSEMBLY</entity><description>Harmony Assembly is an organization that is holding a march at Verdant Oasis Plaza</description>

Relationships:

<id>37</id><source>VERDANT OASIS PLAZA</source><target>UNITY MARCH</target><description>Verdant Oasis Plaza is the location of the Unity March</description>

<id>38</id><source>VERDANT OASIS PLAZA</source><target>HARMONY ASSEMBLY</target><description>Harmony Assembly is holding a march at Verdant Oasis Plaza</description>

<id>39</id><source>VERDANT OASIS PLAZA</source><target>UNITY MARCH</target><description>The Unity March is taking place at Verdant Oasis Plaza</description>

<id>40</id><source>VERDANT OASIS PLAZA</source><target>TRIBUNE SPOTLIGHT</target><description>Tribune Spotlight is reporting on the Unity march taking place at Verdant Oasis Plaza</description>

<id>41</id><source>VERDANT OASIS PLAZA</source><target>BAILEY ASADI</target><description>Bailey Asadi is speaking at Verdant Oasis Plaza about the march</description>

<id>43</id><source>HARMONY ASSEMBLY</source><target>UNITY MARCH</target><description>Harmony Assembly is organizing the Unity March</description>

Output:

<title>Unity March at Verdant Oasis Plaza: Organized by Harmony Assembly with Media Spotlight from Tribune, Featuring Bailey Asadi</title>

<summary>Harmony Assembly and Tribune Spotlight are key entities engaged in organizing and reporting the Unity March at Verdant Oasis Plaza, with notable speakers such as Bailey Asadi.</summary>

<rating>7.5</rating>

<rating_explanation>The impact severity rating reflects the significant public and media engagement anticipated due to the Unity March, involving multiple organizations and individuals.</rating_explanation>

<findings>
    <insight>
        <insight_summary>Central Role of Verdant Oasis Plaza</insight_summary>
        <insight_explanation>Verdant Oasis Plaza serves as the pivotal location for the Unity March, linking multiple entities including Harmony Assembly, Tribune Spotlight, and speaker Bailey Asadi. Its central role enhances its visibility and importance in community events.</insight_explanation>
    </insight>
    <insight>
        <insight_summary>Harmony Assembly's Organizational Involvement</insight_summary>
        <insight_explanation>Harmony Assembly is the main organizer of the Unity March, demonstrating its active role in community mobilization and event management, which may influence local community actions and perceptions.</insight_explanation>
    </insight>
    <insight>
        <insight_summary>Media Coverage by Tribune Spotlight</insight_summary>
        <insight_explanation>Tribune Spotlight's engagement in reporting the event underscores the march's significance and the media's role in shaping public narratives around such community events.</insight_explanation>
    </insight>
    <insight>
        <insight_summary>Influence of Speaker Bailey Asadi</insight_summary>
        <insight_explanation>Bailey Asadi's participation as a speaker potentially elevates the profile of the Unity March, adding a layer of advocacy and public engagement that can resonate with broader audiences.</insight_explanation>
    </insight>
    <insight>
        <insight_summary>Multiple References to Unity March</insight_summary>
        <insight_explanation>The repetition of references to the Unity March across different entities highlights its importance as a central event in community cohesion and public demonstration, indicating widespread support or recognition.</insight_explanation>
    </insight>
</findings>


== Real Data:

{input_text}
'''

COMMUNITY_REPORT_PROMPT2 = '''
You are given an entity net that includes a list of entities and their relationships. As an AI assistant, your task is to help a human analyst extract information from this net. This involves identifying and evaluating data related to various entities, which may be tangible or conceptual, along with their interactions. You will compile a comprehensive report on this entity net, aimed at equipping decision-makers with essential insights into the net’s structure, characteristics, and capabilities. An insight is a deep understanding derived from data analysis that uncovers patterns, elucidates underlying reasons, and emphasizes the significance of the data. Avoid explicitly mentioning meta keywords like "net", "network", "entity", "relationship" and "insight" in your response.

Report Requirements:

Title: The report should have a concise title reflecting the contents of the report. Include names of key entities where possible. You must not put a generic title like “insight into ...”.

Summary: Provide an executive summary that outlines the overall structure of the entity net, the interrelations among its entities, and significant related information.

Impact Severity Rating: Assign a float score between 0-10 indicating the net’s impact severity, where the impact reflects the significance of the entity net.

Rating Explanation: Offer a brief sentence explaining the rationale behind the assigned impact severity rating.

Detailed Findings: List and explain 5-10 major insights about the entity net. Each insight should start with a brief summary followed by a detailed explanation.

Output Format:

Produce the report in XML format with the following structure:

<title>Your Report Title</title>
<summary>Executive summary of the net.</summary>
<rating>Impact severity score.</rating>
<rating_explanation>Explanation for the impact severity score.</rating_explanation>
<findings>
    <insight>
        <insight_summary>Summary of Insight 1</insight_summary>
        <insight_explanation>Detailed explanation of Insight 1.</insight_explanation>
    </insight>
    ...
</findings>


== Important Reminder

You must output the response in xml format as described above.


== Example Input and Output

Entities:

<id>5</id><entity>VERDANT OASIS PLAZA</entity><description>Verdant Oasis Plaza is the location of the Unity March</description>

<id>6</id><entity>HARMONY ASSEMBLY</entity><description>Harmony Assembly is an organization that is holding a march at Verdant Oasis Plaza</description>

Relationships:

<id>37</id><source>VERDANT OASIS PLAZA</source><target>UNITY MARCH</target><description>Verdant Oasis Plaza is the location of the Unity March</description>

<id>38</id><source>VERDANT OASIS PLAZA</source><target>HARMONY ASSEMBLY</target><description>Harmony Assembly is holding a march at Verdant Oasis Plaza</description>

<id>39</id><source>VERDANT OASIS PLAZA</source><target>UNITY MARCH</target><description>The Unity March is taking place at Verdant Oasis Plaza</description>

<id>40</id><source>VERDANT OASIS PLAZA</source><target>TRIBUNE SPOTLIGHT</target><description>Tribune Spotlight is reporting on the Unity march taking place at Verdant Oasis Plaza</description>

<id>41</id><source>VERDANT OASIS PLAZA</source><target>BAILEY ASADI</target><description>Bailey Asadi is speaking at Verdant Oasis Plaza about the march</description>

<id>43</id><source>HARMONY ASSEMBLY</source><target>UNITY MARCH</target><description>Harmony Assembly is organizing the Unity March</description>

Output:

<title>Unity March at Verdant Oasis Plaza: Organized by Harmony Assembly with Media Spotlight from Tribune, Featuring Bailey Asadi</title>

<summary>Harmony Assembly and Tribune Spotlight are key entities engaged in organizing and reporting the Unity March at Verdant Oasis Plaza, with notable speakers such as Bailey Asadi.</summary>

<rating>7.5</rating>

<rating_explanation>The impact severity rating reflects the significant public and media engagement anticipated due to the Unity March, involving multiple organizations and individuals.</rating_explanation>

<findings>
    <insight>
        <insight_summary>Central Role of Verdant Oasis Plaza</insight_summary>
        <insight_explanation>Verdant Oasis Plaza serves as the pivotal location for the Unity March, linking multiple entities including Harmony Assembly, Tribune Spotlight, and speaker Bailey Asadi. Its central role enhances its visibility and importance in community events.</insight_explanation>
    </insight>
    <insight>
        <insight_summary>Harmony Assembly's Organizational Involvement</insight_summary>
        <insight_explanation>Harmony Assembly is the main organizer of the Unity March, demonstrating its active role in community mobilization and event management, which may influence local community actions and perceptions.</insight_explanation>
    </insight>
    <insight>
        <insight_summary>Media Coverage by Tribune Spotlight</insight_summary>
        <insight_explanation>Tribune Spotlight's engagement in reporting the event underscores the march's significance and the media's role in shaping public narratives around such community events.</insight_explanation>
    </insight>
    <insight>
        <insight_summary>Influence of Speaker Bailey Asadi</insight_summary>
        <insight_explanation>Bailey Asadi's participation as a speaker potentially elevates the profile of the Unity March, adding a layer of advocacy and public engagement that can resonate with broader audiences.</insight_explanation>
    </insight>
    <insight>
        <insight_summary>Multiple References to Unity March</insight_summary>
        <insight_explanation>The repetition of references to the Unity March across different entities highlights its importance as a central event in community cohesion and public demonstration, indicating widespread support or recognition.</insight_explanation>
    </insight>
</findings>


== Real Data:

{input_text}
'''

