import re
import random
import ollama
import umap
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.mixture import GaussianMixture
from graphrag.my_graphrag.db import get_all_chunks, save_new_summary, query_raptor_chunks
from graphrag.my_graphrag.conf import TEXT_TEMPLATE


OLLAMA_MODEL_NAME = 'llama3.1:8b-instruct-q8_0'
EMBEDDING_MODEL_NAME = 'sentence-transformers/multi-qa-mpnet-base-cos-v1'
EMBEDDING_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)

RANDOM_SEED = 224
random.seed(RANDOM_SEED)


PROMPT_SUMMARY1 = '''Summarize the following text in bullet points without any reference to tables or figures. The summary needs to be self-contained. Don't mention that it is a summary. Put a blank line between the bullets.

<text>
{text}
</text>
'''


PROMPT_SUMMARY2 = '''Please refine the following text to eliminate any redundant or repetitive descriptions. Ensure the result is concise, clear, and free of unnecessary details while preserving key points. Organize the information in bullet points, with a blank line between each. Present the output in a logical order, prioritizing clarity and brevity. Output only the refined text without any introductory remarks. Do not mention "Here is the refined text" in your response.
<text>
{text}
</text>
'''


PROMPT_SUMMARY3 = '''Please provide a concise and descriptive heading that captures the core theme of the following text. Output only the heading text.

<text>
{text}
</text>
'''


PROMPT_QUERY_STEP1 = '''You are provided with a question and a piece of text below. Please determine whether the text is relevant to the question. Indicate your answer by putting yes or no within <relevant> </relevant> tags. If the text is relevant, extract the relevant information in bullet points, placing the bullets within <info> </info> tags. Add a blank line between each bullet. Do not mention the source of information or "the text" in your response. Put a heading for the relevant informaton. The heading should be in <heading></heading> tags and within <info> </info> tags.

<question>
{question}
</question>

<text>
{context}
</text>
'''


PROMPT_QUERY_STEP2 = '''You are provided with a question and some pieces of information below. Please provide a structured answer to the question based on the given information. Do not mention that your answer is based on these information. Provide as much detail in the answer as possible.

<question>
{question}
</question>

{context}
'''


class Chunk(object):
    def __init__(self, text, index, children, group_id, from_base_chunk=False, root_summary=False):
        self.text = text
        self.index = index
        self.children = children
        self.group_id = group_id
        self.from_base_chunk = from_base_chunk
        self.root_summary = root_summary


def convert_chunk_list(chunk_list):
    # input format: from db import get_all_chunks
    # [{'chunk_id': , 'chunk_content': , 'group_id': }]
    new_chunk_list = []
    for chunk in chunk_list:
        new_chunk_list.append(Chunk(text=chunk['chunk_content'], index=chunk['chunk_id'], children=[], group_id=chunk['group_id']))
    return new_chunk_list


def reduce_embeddings(embeddings):
    n_neighbors = 15  # default value
    dim = 10  # set to 2 or 3 normally, raptor uses 10
    metric = 'cosine'  # value in raptor
    reduced_embeddings = umap.UMAP(
        n_neighbors=n_neighbors, n_components=dim, metric=metric, random_state=RANDOM_SEED
    ).fit_transform(embeddings)

    return reduced_embeddings


def get_optimal_clusters(
    embeddings: np.ndarray, max_clusters: int = 50, random_state: int = RANDOM_SEED
) -> int:
    max_clusters = min(max_clusters, len(embeddings))
    n_clusters = np.arange(1, max_clusters)
    bics = []
    for n in n_clusters:
        gm = GaussianMixture(n_components=n, random_state=RANDOM_SEED)
        gm.fit(embeddings)
        bics.append(gm.bic(embeddings))
    optimal_clusters = n_clusters[np.argmin(bics)]
    return optimal_clusters


def GMM_cluster(embeddings: np.ndarray, threshold: float, random_state: int = 0):
    n_clusters = get_optimal_clusters(embeddings)
    gm = GaussianMixture(n_components=n_clusters, random_state=RANDOM_SEED)
    gm.fit(embeddings)
    probs = gm.predict_proba(embeddings)
    labels = [np.where(prob > threshold)[0] for prob in probs]
    return labels, n_clusters


def split_chunks_into_clusters(chunks):
    try:
        embeddings = np.array([EMBEDDING_MODEL.encode(chunk.text) for chunk in chunks])
        reduced_embeddings = reduce_embeddings(embeddings)

        clusters, n_clusters = GMM_cluster(reduced_embeddings, threshold=0.1)

        clusters_list = []
        for i in range(n_clusters):
            indices = [j for j, cluster in enumerate(clusters) if i in cluster]
            clusters_list.append(indices)

    except:
        clusters_list = [list(range(len(chunks)))]

    return clusters_list


def gen_summary_chunks(chunks):
    clusters_list = split_chunks_into_clusters(chunks)

    summary_chunks = []
    for indices in clusters_list:
        context = ''
        children_idx = []
        for idx in indices:
            child_chunk = chunks[idx]
            context += child_chunk.text + '\n\n'
            children_idx.append(child_chunk.index)

        # step 1: generate summary text
        response1 = ollama.chat(
            model=OLLAMA_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    'content': PROMPT_SUMMARY1.format(text=context)
                },
            ],
            options={
                'temperature': 0,
                'num_predict': 4096,  # 240704 David: ask the llm to limit the summary size to 4096
                'num_ctx': 32000,
            }
        )

        summary_text = response1['message']['content']

        # step 2: review summary text
        response2 = ollama.chat(
            model=OLLAMA_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    'content': PROMPT_SUMMARY2.format(text=summary_text)
                },
            ],
            options={
                'temperature': 0,
                'num_predict': 4096,  # 240704 David: ask the llm to limit the summary size to 4096
                'num_ctx': 32000,
            }
        )

        reviewed_summary_text = response2['message']['content']

        # step 3: add heading
        response3 = ollama.chat(
            model=OLLAMA_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    'content': PROMPT_SUMMARY3.format(text=reviewed_summary_text)
                },
            ],
            options={
                'temperature': 0,
                'num_predict': 4096,  # 240704 David: ask the llm to limit the summary size to 4096
                'num_ctx': 32000,
            }
        )

        heading = response3['message']['content']

        summary = f'<heading>{heading}<\heading>\n{reviewed_summary_text}'
        summary_chunks.append((summary, children_idx))

    return summary_chunks


def raptor_index(new_paper_id_list):
    summary_max_times = 5

    chunk_list = [chunk for chunk in get_all_chunks() if chunk['paper_id'] in new_paper_id_list]
    chunk_list = convert_chunk_list(chunk_list)

    chunk_dict = {}
    for chunk in chunk_list:
        group_id = chunk.group_id
        if group_id not in chunk_dict:
            chunk_dict[group_id] = []
        chunk_dict[group_id].append(chunk)

    for group_id, group_chunk_list in chunk_dict.items():
        chunks = group_chunk_list
        for i in range(summary_max_times):
            summary_chunks = gen_summary_chunks(chunks)

            from_base_chunk = i == 0
            root_summary = len(summary_chunks) == 1 or i == summary_max_times - 1

            chunks = []
            for summary, children_idx in summary_chunks:
                summary_id = save_new_summary(summary, children_idx, from_base_chunk, root_summary, group_id)
                chunks.append(Chunk(summary, summary_id, children_idx, group_id, from_base_chunk, root_summary))

            if root_summary:
                break


def query_step1(question, chunk_list):
    relevant_id_list = []
    info_list = []
    for chunk in chunk_list:
        # chunk: {'id': , 'text': } defined in db query_raptor_chunks
        prompt_step1 = PROMPT_QUERY_STEP1.format(question=question, context=chunk['text'])

        response_step1 = ollama.chat(
            model=OLLAMA_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt_step1
                },
            ],
            options={
                'temperature': 0,
                'num_ctx': 32000,
            }
        )
        answer_step1 = response_step1['message']['content']

        result_content = re.search(r'<info>(.*?)</info>', answer_step1, re.DOTALL)
        # ignore relevant, just get <info>
        relevant_info = result_content.group(1).strip() if result_content else ''

        is_relevant = relevant_info != ''
        if is_relevant:
            info_list.append(relevant_info)
            relevant_id_list.append(chunk['id'])

    return info_list, relevant_id_list


def get_ref_id_and_text(chunk_list, chunk_type):
    ref_id_template = 'group id {group_id}: {chunk_type} chunk ids {chunk_ids}'
    group_chunk_dict = {}
    for chunk in chunk_list:
        chunk_id = str(chunk['id'])
        group_id = str(chunk['group_id'])
        if group_id not in group_chunk_dict:
            group_chunk_dict[group_id] = []
        group_chunk_dict[group_id].append(chunk_id)

    group_id_list = list(group_chunk_dict.keys())
    group_id_list.sort(key=lambda x: int(x), reverse=False)

    ref_id_list = []
    ref_text_list = []
    for group_id in group_id_list:
        chunk_id_list = group_chunk_dict[group_id]
        chunk_id_list = list(set(chunk_id_list))
        chunk_id_list.sort(key=lambda x: int(x), reverse=False)
        ref_id_list.append(ref_id_template.format(group_id=group_id, chunk_ids=', '.join(chunk_id_list), chunk_type=chunk_type))

        for chunk_id in chunk_id_list:
            for chunk in chunk_list:
                if str(chunk['id']) == str(chunk_id):
                    ref_text_list.append(TEXT_TEMPLATE.format(title=chunk_type + '_chunk', id=chunk_id, text=chunk['text']))
                    break

    # ref_id, ref_text
    return '\n'.join(ref_id_list), '\n\n'.join(ref_text_list)


def raptor_query(question, query_group_id=-1):
    base_chunk_list, summary_chunk_list = query_raptor_chunks(question, top_k=10, group_id=query_group_id)

    # step 1
    info_list_base_chunk, relevant_id_list_base_chunk = query_step1(question, base_chunk_list)
    info_list_summary_chunk, relevant_id_list_summary_chunk = query_step1(question, summary_chunk_list)
    info_list = info_list_base_chunk + info_list_summary_chunk

    # step 2
    context_step2 = '\n\n'.join(['<info>\n%s\n</info>' % info for info in info_list])
    prompt_step2 = PROMPT_QUERY_STEP2.format(question=question, context=context_step2)

    response_step2 = ollama.chat(
        model=OLLAMA_MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt_step2
            },
        ],
        options={
            'temperature': 0,
            'num_ctx': 32000,
        }
    )
    answer_step2 = response_step2['message']['content']

    ref_id_base, ref_text_base = get_ref_id_and_text(base_chunk_list, 'base')
    ref_id_summary, ref_text_summary = get_ref_id_and_text(summary_chunk_list, 'summary')

    ref_id_list = []
    if ref_id_base:
        ref_id_list.append(ref_id_base)
    if ref_id_summary:
        ref_id_list.append(ref_id_summary)
    ref_id = '\n'.join(ref_id_list)

    ref_text_list = []
    if ref_text_base:
        ref_text_list.append(ref_text_base)
    if ref_text_summary:
        ref_text_list.append(ref_text_summary)
    ref_text = '\n\n'.join(ref_text_list)

    # answer, ref_id, ref_text
    return answer_step2, ref_id, ref_text

