import os
import re
import json
import traceback
import chromadb
from pathlib import Path

FILE_DIR = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.absolute()
DATABASE_PATH = os.path.join(FILE_DIR, './my_graphrag/vector_database')
COLLECTION_GROUP = 'group'
COLLECTION_PAPER = 'paper'
COLLECTION_CHUNK = 'chunk'
COLLECTION_RELATIONSHIP = 'relationship'
COLLECTION_COMMUNITY_REPORT = 'community_report'
COLLECTION_SUMMARY = 'summary'


def save_new_item(collection_name: str, documents: str, metadatas: dict):
    client = chromadb.PersistentClient(path=DATABASE_PATH)
    collection = client.get_or_create_collection(name=collection_name)

    all_data = collection.get()

    last_ids = 0
    for ids in all_data['ids']:
        last_ids = max(last_ids, int(ids))

    new_ids = last_ids + 1
    collection.add(
        documents=[
            documents
        ],
        metadatas=[
            metadatas
        ],
        ids=[
            str(new_ids)
        ]
    )

    return new_ids


def get_id(collection_name: str, query_content: str):
    client = chromadb.PersistentClient(path=DATABASE_PATH)
    collection = client.get_collection(name=collection_name)

    results = collection.query(
        query_texts=[query_content],
        n_results=1
    )

    return results['ids'][0][0]


def save_new_group(group_name):
    # group
    # ids: group id
    # documents: group_name
    # metadatas: group_name

    group_id = save_new_item(
        COLLECTION_GROUP,
        group_name,
        {
            'group_name': group_name,
        }
    )

    return group_id


def save_new_paper(paper_content, paper_name, group_id):
    # paper
    # ids: paper id
    # documents: paper_name
    # metadatas: paper_name, group_id

    paper_id = save_new_item(
        COLLECTION_PAPER,
        paper_content,
        {
            'paper_name': paper_name,
            'group_id': group_id,
        }
    )

    return paper_id


def save_new_chunk(chunk, paper_content):
    # chunk
    # ids: chunk id
    # documents: chunk_content
    # metadatas: paper_id

    paper_id = get_id(COLLECTION_PAPER, paper_content)

    chunk_id = save_new_item(
        COLLECTION_CHUNK,
        chunk,
        {
            'paper_id': paper_id,
        }
    )

    return chunk_id


def save_new_relationship(chunk, source_entity_name, target_entity_name, relationship_description, relationship_strength):
    # relationship
    # ids: relationship id
    # documents: relationship_description
    # metadatas: source entity name, target entity name, relationship description, relationship strength, chunk id

    chunk_id = get_id(COLLECTION_CHUNK, chunk)

    relationship_id = save_new_item(
        COLLECTION_RELATIONSHIP,
        relationship_description,
        {
            'source_entity_name': source_entity_name,
            'target_entity_name': target_entity_name,
            'relationship_description': relationship_description,
            'relationship_strength': relationship_strength,
            'chunk_id': chunk_id,
        }
    )

    return relationship_id


def save_new_community_report(index_prompt3_input_text, community_report_text, title, summary, rating, rating_explanation, findings):
    # community report
    # ids: community report id
    # documents: community report text
    # metadatas: relationship ids, title, summary, rating, rating explanation, findings (<insight> <insight_summary> ... </insight_summary> <insight_explanation> ... </insight_explanation> </insight>)

    descriptions = re.findall(r'</target><description>(.*?)</description>', index_prompt3_input_text, re.DOTALL)
    chunk_id_list = []

    if descriptions:
        client = chromadb.PersistentClient(path=DATABASE_PATH)
        collection = client.get_collection(name=COLLECTION_RELATIONSHIP)

        for des in descriptions:
            results = collection.query(
                query_texts=[des],
                n_results=1
            )

            chunk_id_list.append(results['metadatas'][0][0]['chunk_id'])

        chunk_id_list = list(set(chunk_id_list))

    report_id = save_new_item(
        COLLECTION_COMMUNITY_REPORT,
        community_report_text,
        {
            'chunk_id_list': json.dumps(chunk_id_list),
            'title': title,
            'summary': summary,
            'rating': rating,
            'rating_explanation': rating_explanation,
            'findings': findings,
        }
    )

    return report_id


def save_new_summary(summary_text, chunk_id_list, from_base_chunk, root_summary, paper_id):
    # summary chunk
    # ids: summary chunk id
    # documents: summary text
    # metadatas: chunk_id_list
    summary_id = save_new_item(
        COLLECTION_SUMMARY,
        summary_text,
        {
            'chunk_id_list': json.dumps(chunk_id_list),
            'from_base_chunk': from_base_chunk,
            'root_summary': root_summary,
            'paper_id': paper_id,
        }
    )

    return summary_id


def get_all_community_reports():
    report_list = []
    try:
        client = chromadb.PersistentClient(path=DATABASE_PATH)
        collection = client.get_collection(name=COLLECTION_COMMUNITY_REPORT)

        all_data = collection.get()
        for i in range(len(all_data['ids'])):
            report_list.append(
                {
                    'report_id': all_data['ids'][i],
                    'report_content': all_data['documents'][i],
                    'report_title': all_data['metadatas'][i]['title'],
                    'chunk_id_list': json.loads(all_data['metadatas'][i]['chunk_id_list'])
                }
            )

        report_list.sort(key=lambda x: int(x['report_id']), reverse=False)
    except Exception as e:
        print(e)
        traceback.print_exc()

    return report_list


def get_all_chunks():
    chunk_list = []
    try:
        client = chromadb.PersistentClient(path=DATABASE_PATH)
        collection = client.get_collection(name=COLLECTION_CHUNK)

        all_data = collection.get()
        for i in range(len(all_data['ids'])):
            chunk_list.append(
                {
                    'chunk_id': all_data['ids'][i],
                    'chunk_content': all_data['documents'][i],
                    'paper_id': all_data['metadatas'][i]['paper_id'],
                }
            )

        chunk_list.sort(key=lambda x: int(x['chunk_id']), reverse=False)
    except Exception as e:
        print(e)
        traceback.print_exc()

    return chunk_list


def get_all_summary_chunks():
    summary_list = []
    try:
        client = chromadb.PersistentClient(path=DATABASE_PATH)
        collection = client.get_collection(name=COLLECTION_SUMMARY)

        all_data = collection.get()
        for i in range(len(all_data['ids'])):
            summary_list.append(
                {
                    'summary_id': all_data['ids'][i],
                    'summary_content': all_data['documents'][i],
                    'chunk_id_list': json.loads(all_data['metadatas'][i]['chunk_id_list']),
                    'from_base_chunk': all_data['metadatas'][i]['from_base_chunk'],
                    'root_summary': all_data['metadatas'][i]['root_summary'],
                    'paper_id': all_data['metadatas'][i]['paper_id'],
                }
            )

        summary_list.sort(key=lambda x: int(x['summary_id']), reverse=False)
    except Exception as e:
        print(e)
        traceback.print_exc()

    return summary_list


def get_all_papers():
    paper_list = []
    try:
        client = chromadb.PersistentClient(path=DATABASE_PATH)
        collection = client.get_collection(name=COLLECTION_PAPER)

        all_data = collection.get()
        for i in range(len(all_data['ids'])):
            paper_list.append(
                {
                    'paper_id': all_data['ids'][i],
                    'paper_content': all_data['documents'][i],
                    'paper_name': all_data['metadatas'][i]['paper_name'],
                    'group_id': all_data['metadatas'][i]['group_id'],
                }
            )

        paper_list.sort(key=lambda x: int(x['paper_id']), reverse=False)
    except Exception as e:
        print(e)
        traceback.print_exc()

    return paper_list


def get_paper_id_of_chunk(chunk_id):
    try:
        client = chromadb.PersistentClient(path=DATABASE_PATH)
        collection = client.get_collection(name=COLLECTION_CHUNK)

        results = collection.get(
            ids=[str(chunk_id)]
        )

        paper_id = results['metadatas'][0]['paper_id']
    except Exception as e:
        print(e)
        traceback.print_exc()

    return paper_id


def count_all_collection():
    client = chromadb.PersistentClient(path=DATABASE_PATH)

    # group
    group_count = 0
    try:
        collection = client.get_collection(name=COLLECTION_GROUP)
        all_data = collection.get()
        group_count = len(all_data['ids'])
    except Exception as e:
        print(e)
        traceback.print_exc()
    print('count of group:', group_count)

    # paper
    paper_count = 0
    try:
        collection = client.get_collection(name=COLLECTION_PAPER)
        all_data = collection.get()
        paper_count = len(all_data['ids'])
    except Exception as e:
        print(e)
        traceback.print_exc()
    print('count of paper:', paper_count)

    # chunk
    chunk_count = 0
    try:
        collection = client.get_collection(name=COLLECTION_CHUNK)
        all_data = collection.get()
        chunk_count = len(all_data['ids'])
    except Exception as e:
        print(e)
        traceback.print_exc()
    print('count of chunk:', chunk_count)

    # relationship
    relationship_count = 0
    try:
        collection = client.get_collection(name=COLLECTION_RELATIONSHIP)
        all_data = collection.get()
        relationship_count = len(all_data['ids'])
    except Exception as e:
        print(e)
        traceback.print_exc()
    print('count of relationship:', relationship_count)

    # community report
    report_count = 0
    try:
        collection = client.get_collection(name=COLLECTION_COMMUNITY_REPORT)
        all_data = collection.get()
        report_count = len(all_data['ids'])
    except Exception as e:
        print(e)
        traceback.print_exc()
    print('count of community report:', report_count)

    # summary
    summary_count = 0
    try:
        collection = client.get_collection(name=COLLECTION_SUMMARY)
        all_data = collection.get()
        summary_count = len(all_data['ids'])
    except Exception as e:
        print(e)
        traceback.print_exc()
    print('count of summary:', summary_count)


def get_text(collection_name: str, ids: str):
    try:
        client = chromadb.PersistentClient(path=DATABASE_PATH)
        collection = client.get_collection(name=collection_name)

        results = collection.get(
            ids=[ids]
        )

        text = results['documents'][0]
    except Exception as e:
        print(e)
        traceback.print_exc()
        text = ''

    return text


def get_chunk(chunk_id):
    return get_text(COLLECTION_CHUNK, str(chunk_id))


def get_summary(summary_id):
    return get_text(COLLECTION_SUMMARY, str(summary_id))


def get_paper(paper_id):
    return get_text(COLLECTION_PAPER, str(paper_id))


def query_chunks(query_text, collection_list, top_k=10):
    client = chromadb.PersistentClient(path=DATABASE_PATH)
    result_list = []
    for collection_name in collection_list:
        collection = client.get_collection(name=collection_name)

        results = collection.query(
            query_texts=[query_text],
            n_results=top_k
        )

        for i in range(len(results['ids'][0])):
            result_list.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'distance': results['distances'][0][i],
                'metadatas': results['metadatas'][0][i],
                'collection_name': collection_name,
            })

    result_list.sort(key=lambda x: x['distance'], reverse=False)

    return result_list[:top_k]


def query_raptor_chunks(query_text, top_k=10):
    chunk_list = query_chunks(query_text, [COLLECTION_SUMMARY, COLLECTION_CHUNK], top_k)

    base_chunk_list = []
    summary_chunk_list = []
    for chunk in chunk_list:
        new_chunk = {
            'id': chunk['id'],
            'text': chunk['text'],
            'paper_id': chunk['metadatas']['paper_id'],
        }
        if chunk['collection_name'] == COLLECTION_SUMMARY:
            summary_chunk_list.append(new_chunk)
        else:
            base_chunk_list.append(new_chunk)

    return base_chunk_list, summary_chunk_list

