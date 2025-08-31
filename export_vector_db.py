import argparse
import os
import graphrag.my_graphrag.db as db
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Export DB path")
    parser.add_argument("db_path")
    args = parser.parse_args()
    db_path = args.db_path

    if not os.path.isdir(db_path):
        print(f'Database path "{db_path}" does not exist.')
        return None

    db.update_db_path(db_path)

    output_dir = os.path.join(db_path, f'export_{datetime.now().strftime("%Y%m%d-%H%M%S")}')
    os.mkdir(output_dir)

    # group
    group_dir = os.path.join(output_dir, 'group')
    os.mkdir(group_dir)
    for group in db.get_all_groups():
        with open(os.path.join(group_dir, f'{group["group_id"]}.txt'), 'w') as f:
            f.write(group["group_name"])
            f.flush()

    # paper
    paper_dir = os.path.join(output_dir, 'document')
    os.mkdir(paper_dir)
    for paper in db.get_all_papers():
        with open(os.path.join(paper_dir, f'{paper["paper_id"]}.txt'), 'w') as f:
            f.write(paper["paper_content"])
            f.flush()

    # chunk
    chunk_dir = os.path.join(output_dir, 'chunk')
    os.mkdir(chunk_dir)
    for chunk in db.get_all_chunks():
        with open(os.path.join(chunk_dir, f'{chunk["chunk_id"]}.txt'), 'w') as f:
            f.write(chunk["denoising_chunk"])
            f.flush()

    # relationship
    relationship_dir = os.path.join(output_dir, 'relationship')
    os.mkdir(relationship_dir)
    for relationship in db.get_all_relationships():
        with open(os.path.join(relationship_dir, f'{relationship["relationship_id"]}.txt'), 'w') as f:
            f.write(relationship["relationship_description"])
            f.flush()

    # community report
    community_report_dir = os.path.join(output_dir, 'graphrag_community_report')
    os.mkdir(community_report_dir)
    for community_report in db.get_all_community_reports():
        with open(os.path.join(community_report_dir, f'{community_report["report_id"]}.txt'), 'w') as f:
            f.write(community_report["report_content"])
            f.flush()

    # summary
    summary_dir = os.path.join(output_dir, 'raptor_summary')
    os.mkdir(summary_dir)
    for summary in db.get_all_summary_chunks():
        with open(os.path.join(summary_dir, f'{summary["summary_id"]}.txt'), 'w') as f:
            f.write(summary["summary_content"])
            f.flush()

        chunk_id_list = summary["chunk_id_list"]
        chunk_id_list.sort(key=lambda x: int(x), reverse=False)
        with open(os.path.join(summary_dir, 'hierarchy.txt'), 'a') as f:
            f.write(f'{summary["summary_id"]}: {"chunk" if summary["from_base_chunk"] else "summary"} {", ".join(map(str, chunk_id_list))}\n')
            f.flush()

    db.rm_db_tmp_file()
    print(f'Exported to "{output_dir}"')


if __name__ == "__main__":
    main()
