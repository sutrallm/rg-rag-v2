# Query option
QUERY_RAPTOR = 'raptor'  # use raptor query, summary chunk + base chunk
QUERY_GRAPHRAG = 'graphrag'  # use graphrag query, community report
QUERY_RAPTOR_GRAPHRAG = 'raptor + graphrag'  # use graphrag query, community report + raptor summary chunks

QUERY_OPTION = QUERY_RAPTOR_GRAPHRAG  # should be one of the above options

# Final answer option
FINAL_ANSWER_WITH_DETAILS = False  # if True, export chunk text; if False, export id only

TEXT_TEMPLATE = '''<{title}>
<id>{id}</id>
<text>
{text}
</text>
</{title}>'''

