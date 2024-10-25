# RG-RAG

### Setup environment
```bash
conda create -n rg-rag python=3.10
conda activate rg-rag
pip install pdftotext
pip install chromadb sentence_transformers scikit-learn umap-learn graphrag nltk
pip install ollama
```

### Prepare models
```bash
ollama pull llama3.1:8b-instruct-q8_0
ollama pull nomic-embed-text
```
Create a new 32K `ollama-8b-q8-32k-model` file:
```
FROM llama3.1:8b-instruct-q8_0
PARAMETER num_ctx 32000
```
Create a new Ollama model from above model file:
```bash
ollama create llama3.1-32k-q8 -f ollama-8b-q8-32k-model
```
Check installed models:
```base
ollama list
```

### Prepare documents
Copy some documents into the `input_groups` folder:
```bash
$ ls -al my_graphrag/input_groups/
total 12
drwxrwxr-x 3 ohho ohho 4096 Sep 30 10:44 .
drwxrwxr-x 7 ohho ohho 4096 Sep 30 10:42 ..
drwxrwxr-x 2 ohho ohho 4096 Sep 30 10:44 heart

$ ls -al my_graphrag/input_groups/heart/
total 12
drwxrwxr-x 2 ohho ohho 4096 Sep 30 10:44 .
drwxrwxr-x 3 ohho ohho 4096 Sep 30 10:44 ..
-rw-r--r-- 1 ohho ohho 1492 Sep 30 10:44 the-heart-sutra.txt
```

### Index
```bash
conda activate rg-rag
python index.py [options]
```
##### Options
| Argument            | Short | Type     | Default Value                   | Description                               |
|---------------------|-------|----------|---------------------------------|-------------------------------------------|
| `--help`            | `-h`  |          |                                 | Show the help message of all options and exit. |
| `--db_path`         | `-p`  | `str`    | `./my_graphrag/vector_database` | Specify the database path. If the path already exists, check whether the document is in the db, if not, add to the db. |
| `--raptor`          | `-r`  | `bool`   | `True`                          | If True, run raptor index. If False, skip raptor index. |
| `--graphrag`        | `-g`  | `bool`   | `True`                          | If True, run graphrag index. If False, skip graphrag index. |
| `--chunking`        | `-c`  | `bool`   | `True`                          | If True, use our chunking method to chunk each file in the group. If False, consider each file in the group is a chunk. |
<details>
  <summary>Typical output...</summary>

  ```
  $ python index.py
  🚀 Reading settings from /home/ohho/codes/david/rg-rag-sutra/my_graphrag/output/tmp_config/settings.yaml
  🚀 create_base_text_units
                                   id  ... n_tokens
  0  ac67bbf50ea59187cea5947b4e482e79  ...      300
  1  0650fd69f66ac0d668f05d218942ac62  ...      201
  2  7d902ccc1d6328cdf06ab78c6a43b5f8  ...        1
  
  [3 rows x 5 columns]
  🚀 create_base_extracted_entities
                                          entity_graph
  0  <graphml xmlns="http://graphml.graphdrawing.or...
  🚀 create_summarized_entities
                                          entity_graph
  0  <graphml xmlns="http://graphml.graphdrawing.or...
  🚀 create_base_entity_graph
     level                                    clustered_graph
  0      0  <graphml xmlns="http://graphml.graphdrawing.or...
  1      1  <graphml xmlns="http://graphml.graphdrawing.or...
  🚀 create_final_entities
                                    id  ...                              description_embedding
  0   b45241d70f0e43fca764df95b2b81f77  ...  [0.9320005774497986, 1.397796392440796, -3.174...
  1   4119fd06010c494caa07f439b333f4c5  ...  [0.24602527916431427, 1.054911494255066, -2.92...
  2   d3835bf3dda84ead99deadbeac5d0d7d  ...  [0.41057634353637695, 1.5639721155166626, -3.4...
  3   077d2820ae1845bcbb1803379a3d1eae  ...  [-0.05211891978979111, 1.8968952894210815, -3....
  4   3671ea0dd4e84c1a9b02c5ab2c8f4bac  ...  [0.20558682084083557, 1.4166734218597412, -3.1...
  ..                               ...  ...                                                ...
  72  fa3c4204421c48609e52c8de2da4c654  ...  [-0.23991772532463074, 1.334349274635315, -3.4...
  73  53af055f068244d0ac861b2e89376495  ...  [-0.057600777596235275, 0.6985769271850586, -3...
  74  c03ab3ce8cb74ad2a03b94723bfab3c7  ...  [-0.2641189694404602, 1.2557107210159302, -3.4...
  75  ed6d2eee9d7b4f5db466b1f6404d31cc  ...  [0.3077894151210785, 0.9161084294319153, -4.18...
  76  fc01e9baa80e417c9206f941bb279407  ...  [-0.8715166449546814, 1.3191969394683838, -3.7...
  
  [77 rows x 8 columns]
  🚀 create_final_nodes
       level                      title          type  ...                 top_level_node_id  x  y
  0        0  BODHISATTVA OF COMPASSION        PERSON  ...  b45241d70f0e43fca764df95b2b81f77  0  0
  1        0              PRAJNA WISDOM       CONCEPT  ...  4119fd06010c494caa07f439b333f4c5  0  0
  2        0                    NIRVANA       CONCEPT  ...  d3835bf3dda84ead99deadbeac5d0d7d  0  0
  3        0                BODHISATTVA        PERSON  ...  077d2820ae1845bcbb1803379a3d1eae  0  0
  4        0                      SUTRA          TEXT  ...  3671ea0dd4e84c1a9b02c5ab2c8f4bac  0  0
  ..     ...                        ...           ...  ...                               ... .. ..
  149      1           PRESS_CONFERENCE         EVENT  ...  fa3c4204421c48609e52c8de2da4c654  0  0
  150      1               RELEASE_DATE  EVENT_DETAIL  ...  53af055f068244d0ac861b2e89376495  0  0
  151      1               RELEASE_TIME  EVENT_DETAIL  ...  c03ab3ce8cb74ad2a03b94723bfab3c7  0  0
  152      1               EVENT_DETAIL  EVENT_DETAIL  ...  ed6d2eee9d7b4f5db466b1f6404d31cc  0  0
  153      1                    SERVICE       SERVICE  ...  fc01e9baa80e417c9206f941bb279407  0  0
  
  [154 rows x 15 columns]
  🚀 create_final_communities
    id        title  ...                                   relationship_ids                       text_unit_ids
  0  1  Community 1  ...  [6ea81acaf232485e94fff638e03336e1, d136b08d586...  [7d902ccc1d6328cdf06ab78c6a43b5f8]
  1  0  Community 0  ...  [af1d0fec22114a3398b8016f5225f9ed, b07a7f08836...  [7d902ccc1d6328cdf06ab78c6a43b5f8]
  2  3  Community 3  ...  [353d91abc68648639d65a549e59b5cf3, 7ce637e4f35...  [7d902ccc1d6328cdf06ab78c6a43b5f8]
  3  2  Community 2  ...  [9a6f414210e14841a5b0e661aedc898d, 30c9641543c...  [7d902ccc1d6328cdf06ab78c6a43b5f8]
  4  7  Community 7  ...  [6ea81acaf232485e94fff638e03336e1, d136b08d586...  [7d902ccc1d6328cdf06ab78c6a43b5f8]
  5  5  Community 5  ...  [af1d0fec22114a3398b8016f5225f9ed, b07a7f08836...  [7d902ccc1d6328cdf06ab78c6a43b5f8]
  6  8  Community 8  ...  [eeef6ae5c464400c8755900b4f1ac37a, cccfa151fed...  [7d902ccc1d6328cdf06ab78c6a43b5f8]
  7  6  Community 6  ...  [422433aa45804c7ebb973b2fafce5da6, 86505bca739...  [7d902ccc1d6328cdf06ab78c6a43b5f8]
  8  4  Community 4  ...  [1af9faf341e14a5bbf4ddc9080e8dc0b, 8870cf2b5df...  [7d902ccc1d6328cdf06ab78c6a43b5f8]
  
  [9 rows x 6 columns]
  🚀 join_text_units_to_entity_ids
                        text_unit_ids                                         entity_ids                                id
  0  ac67bbf50ea59187cea5947b4e482e79  [b45241d70f0e43fca764df95b2b81f77, 4119fd06010...  ac67bbf50ea59187cea5947b4e482e79
  1  0650fd69f66ac0d668f05d218942ac62  [4119fd06010c494caa07f439b333f4c5, d3835bf3dda...  0650fd69f66ac0d668f05d218942ac62
  2  7d902ccc1d6328cdf06ab78c6a43b5f8  [147c038aef3e4422acbbc5f7938c4ab8, b7702b90c7f...  7d902ccc1d6328cdf06ab78c6a43b5f8
  🚀 create_final_relationships
                         source                  target  weight  ... source_degree target_degree rank
  0   BODHISATTVA OF COMPASSION           PRAJNA WISDOM     4.0  ...             3             7   10
  1   BODHISATTVA OF COMPASSION                 NIRVANA     5.0  ...             3            12   15
  2   BODHISATTVA OF COMPASSION                   SUTRA     7.0  ...             3             3    6
  3               PRAJNA WISDOM                 NIRVANA    11.0  ...             7            12   19
  4               PRAJNA WISDOM             BODHISATTVA     4.0  ...             7             8   15
  ..                        ...                     ...     ...  ...           ...           ...  ...
  68                    YOUTUBE  VIDEO_SHARING_PLATFORM     1.0  ...             2             1    3
  69                   FACEBOOK            SOCIAL_MEDIA     1.0  ...             4             1    5
  70                   FACEBOOK                PLATFORM     2.0  ...             4             1    5
  71                   FACEBOOK                 SERVICE     1.0  ...             4             1    5
  72                    RELEASE                   EVENT     1.0  ...             2             1    3
  
  [73 rows x 10 columns]
  🚀 join_text_units_to_relationship_ids
                                   id                                   relationship_ids
  0  ac67bbf50ea59187cea5947b4e482e79  [56d0e5ebe79e4814bd1463cf6ca21394, 7c49f2710e8...
  1  0650fd69f66ac0d668f05d218942ac62  [0adb2d9941f34ef7b2f7743cc6225844, 6b02373137f...
  2  7d902ccc1d6328cdf06ab78c6a43b5f8  [6ea81acaf232485e94fff638e03336e1, d136b08d586...
  🚀 create_final_community_reports
    community  ...                                    id
  0         4  ...  1e8045b0-3147-47c4-b208-e9f3f65aed25
  1         5  ...  8e0481a8-b320-4484-a1cc-60cd7fee8c71
  2         6  ...  2cc69642-bc13-4e64-8866-32c3f24fa4a8
  3         7  ...  0c32904b-383b-4395-a38b-ca7ab5be48ef
  4         8  ...  6f422588-9d9e-4574-90bd-6c549a304d27
  5         0  ...  ea480c97-d7c2-4be0-9d8a-0752c03227d7
  6         1  ...  c4034add-8149-4ddb-a669-ae9a8cd79ace
  7         2  ...  618bd89f-282e-43b4-8777-2f9411f55514
  8         3  ...  30bc8c70-c20c-4d6a-9f5f-28baf50ca481
  
  [9 rows x 10 columns]
  🚀 create_final_text_units
                                   id  ...                                   relationship_ids
  0  ac67bbf50ea59187cea5947b4e482e79  ...  [56d0e5ebe79e4814bd1463cf6ca21394, 7c49f2710e8...
  1  0650fd69f66ac0d668f05d218942ac62  ...  [0adb2d9941f34ef7b2f7743cc6225844, 6b02373137f...
  2  7d902ccc1d6328cdf06ab78c6a43b5f8  ...  [6ea81acaf232485e94fff638e03336e1, d136b08d586...
  
  [3 rows x 6 columns]
  🚀 create_base_documents
                                   id  ...                title
  0  41326c50c373b31d1a8d23b8ae48151a  ...  the-heart-sutra.txt
  
  [1 rows x 4 columns]
  🚀 create_final_documents
                                   id  ...                title
  0  41326c50c373b31d1a8d23b8ae48151a  ...  the-heart-sutra.txt
  
  [1 rows x 4 columns]
  ⠇ GraphRAG Indexer 
  ├── Loading Input (text) - 1 files loaded (0 filtered) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00 0:00:00
  ├── create_base_text_units
  ├── create_base_extracted_entities
  ├── create_summarized_entities
  ├── create_base_entity_graph
  ├── create_final_entities
  ├── create_final_nodes
  ├── create_final_communities
  ├── join_text_units_to_entity_ids
  ├── create_final_relationships
  ├── join_text_units_to_relationship_ids
  ├── create_final_community_reports
  ├── create_final_text_units
  ├── create_base_documents
  └── create_final_documents
  🚀 All workflows completed successfully.
  graphrag run time: 0:09:45.906138
  raptor run time: 0:00:03.178684
  run time: 0:09:49.084822
  count of group: 1
  count of paper: 1
  count of chunk: 1
  count of relationship: 234
  count of community report: 9
  count of summary: 1
  ```
</details>

### Query
```bash
python query.py [options]
```
##### Options
| Argument      | Short | Type   | Default Value                                                 | Description                                                               |
|---------------|-------|--------|---------------------------------------------------------------|---------------------------------------------------------------------------|
| `--help`      | `-h`  |        |                                                               | Show the help message of all options and exit.                            |
| `--question`  | `-q`  | `str`  | `What improvement techniques have people implemented on RAG?` | Provide a question for query.                                             |
| `--db_path`   | `-p`  | `str`  | `./my_graphrag/vector_database`                               | Specify the database path.                                                |
| `--list_group`| `-l`  | `bool` | `False`                                                       | If True, list group details. If False, execute the query.                 |
| `--group_id`  | `-g`  | `int`  | `-1 (query all)`                                              | Group ID to query. If not provided, query all.                            |
<details>
  <summary>Typical output...</summary>

  ```
  $ python query.py -q "what's the meaning of suffering?"
  [nltk_data] Downloading package punkt to /home/user2/nltk_data...
  [nltk_data]   Package punkt is already up-to-date!
  --- final answer ---
  <question>
  what's the meaning of suffering?
  </question>
  
  <answer>
  **Summary of Analyst Reports**
  
  The analysts' reports provide various perspectives on the concept of "suffering". However, it is essential to note that none of the reports directly address the question of what suffering means. The top-ranked report indicates that there is no information about suffering in the data table.
  
  **Key Points from Analyst Reports**
  
  1. **Suffering as a void concept**: Suffering may be seen as an empty or void concept, similar to wisdom and attainment (Score: 60).
  2. **Suffering alleviated by Prajna wisdom and dharani mantra**: The great dharani mantra can alleviate all pain, implying that suffering can be alleviated through the use of this mantra (Score: 50).
  3. **Suffering as a lack of Prajna wisdom**: Suffering is associated with the absence of Prajna wisdom, which is necessary for reaching the clearest state of Nirvana (Score: 70).
  4. **Suffering as a result of ignorance and delusion**: Suffering is described as a consequence of ignorance, which leads to delusion (Score: 80).
  5. **Suffering ultimately empty of inherent existence**: All phenomena, including suffering, are void of inherent existence (Score: 90).
  
  **Implications**
  
  While the analysts' reports provide various perspectives on suffering, it is essential to note that none of them directly answer the question of what suffering means. However, we can infer that suffering may be seen as:
  
  * A void concept
  * Alleviated by Prajna wisdom and the dharani mantra
  * Associated with the absence of Prajna wisdom
  * A consequence of ignorance and delusion
  * Ultimately empty of inherent existence
  
  **Conclusion**
  
  The analysts' reports provide a range of perspectives on suffering, but none directly address the question. However, we can synthesize the key points to understand that suffering may be seen as an empty or void concept, alleviated by Prajna wisdom and the dharani mantra, associated with the absence of Prajna wisdom, a consequence of ignorance and delusion, and ultimately empty of inherent existence.
  
  **Recommendation**
  
  To answer the question more directly, further analysis or additional data may be necessary to provide a clear understanding of what suffering means.
  </answer>
  
  <reference_id>
  paper id 1: chunk ids 1
  paper id 1: summary ids 1
  </reference_id>
  
  --- final answer ---
  run time 0:00:15.993182
  ```
</details>

### Tmux
As the indexing process may take a long time and break a remote session, it's recommended use `tmux`:
```bash
tmux
conda activate rg-rag
python index.py
```
Press `ctrl+b` and `d` to detach:
```bash
[detached (from session 0)]
```
List `tmux` sessions:
```bash
tmux ls
0: 1 windows (created Mon Sep 30 15:57:59 2024)
```
Attach the detached session:
```bash
tmux attach -t 0
```
