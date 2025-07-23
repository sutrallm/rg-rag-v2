import random
import csv
import umap
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.mixture import GaussianMixture
import graphrag.my_graphrag.db as db
import graphrag.my_graphrag.cloud as model


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
        for sub_chunk in chunk['sub_chunks']:
            new_chunk_list.append(Chunk(text=sub_chunk, index=chunk['chunk_id'], children=[], group_id=chunk['group_id']))
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
        summary_text = model.get_response_from_sgl(PROMPT_SUMMARY1.format(text=context))

        # step 2: review summary text
        reviewed_summary_text = model.get_response_from_sgl(PROMPT_SUMMARY2.format(text=summary_text))

        # step 3: add heading
        heading = model.get_response_from_sgl(PROMPT_SUMMARY3.format(text=reviewed_summary_text))

        summary = f'<heading>{heading}<\heading>\n{reviewed_summary_text}'
        summary_chunks.append((summary, children_idx))

    return summary_chunks


def raptor_index(new_paper_id_list, log_path):
    summary_max_times = 5

    chunk_list = [chunk for chunk in db.get_all_chunks() if chunk['paper_id'] in new_paper_id_list]
    chunk_list = convert_chunk_list(chunk_list)

    chunk_dict = {}
    for chunk in chunk_list:
        group_id = chunk.group_id
        if group_id not in chunk_dict:
            chunk_dict[group_id] = []
        chunk_dict[group_id].append(chunk)

    group_list = db.get_all_groups()
    paper_list = db.get_all_papers()

    for group_id, group_chunk_list in chunk_dict.items():
        start_time_one_group = datetime.now()

        group_name = ''
        for group in group_list:
            if group['group_id'] == group_id:
                group_name = group['group_name']
                break

        paper_id_list = []
        paper_name_list = []
        for paper in paper_list:
            if paper['paper_id'] in new_paper_id_list and paper['group_id'] == group_id:
                paper_id_list.append(paper['paper_id'])
                paper_name_list.append(paper['paper_name'])

        with open(log_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(['Start time', start_time_one_group.strftime('%Y-%m-%d-%H-%M-%S')])
            writer.writerow(['Group ID', group_id])
            writer.writerow(['Group name', group_name])
            writer.writerow(['Document IDs', str(paper_id_list)])
            writer.writerow(['Document names', str(paper_name_list)])
            writer.writerow(['Index type', 'Raptor'])
            f.flush()

        chunks = group_chunk_list
        for i in range(summary_max_times):
            summary_chunks = gen_summary_chunks(chunks)

            from_base_chunk = i == 0
            root_summary = len(summary_chunks) == 1 or i == summary_max_times - 1

            chunks = []
            for summary, children_idx in summary_chunks:
                children_idx = list(set(children_idx))
                summary_id = db.save_new_summary(summary, children_idx, from_base_chunk, root_summary, group_id)
                chunks.append(Chunk(summary, summary_id, children_idx, group_id, from_base_chunk, root_summary))

            if root_summary:
                break

        end_time_one_group = datetime.now()
        with open(log_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(['Run time', end_time_one_group - start_time_one_group])
            writer.writerow(['End time', end_time_one_group.strftime('%Y-%m-%d-%H-%M-%S')])
            f.flush()
