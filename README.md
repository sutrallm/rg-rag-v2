# RG-RAG

# Introduction

This is a small experiment with Raptor, Microsoft Graphrag (hereafter referred to as Graphrag), Llama 3.1, and Deepseek R1. Raptor essentially creates a hierarchy of summaries from a source document, while Graphrag gains insight through a graph representation of the same document. We integrate the Raptor and Graphrag methods and name the resulting system RG-Rag, as shown in the diagram below.

![RG-RAG-Workflow](https://github.com/sutrallm/rg-rag/blob/master/image/rg-rag-workflow-v1.png)

Deepseek is used for reasoning tasks such as graph construction, insight derivation, and query processing. We found that Deepseek R1 tends to over-reason for simple denoising and summarization tasks; therefore, we use Llama 3.1 for these purposes. Buddhist sutras are typically repetitive and contain a lot of dialogue. Since we are more interested in the underlying concepts, we added a denoising step to remove dialogue styles and repetitive sentences, which shortens the processing time for subsequent steps. Details of the modifications made to the original Raptor and Graphrag methods are provided in the following sections.

We aim to run the entire project locally on a single RTX4090, using the 8b versions of Llama 3.1 and Deepseek R1.

For our experiments, we used several Buddhist sutras (including the Diamond Sutra and the Saṃyutta Nikāya of the Pali Canon) as knowledge sources. These sutras were obtained from CBETA (https://www.cbeta.org/) and translated from Chinese to English using the online version of the Deepseek R1 API. The vector databases for these sutras can be found in this repository.

### Index

1.	The user provides multiple groups, each containing one or more TXT or PDF files. If a file is in PDF format, it is first converted to TXT.
2.	For each group, treat each file as a base chunk.
3.	Denoise each base chunk.
4.	Split the denoised text into points:
    - If there are blank lines, use a blank line `\n\n` as the delimiter.
    - If there are no blank lines, use `#` as the delimiter.
    - Each split text segment is considered a point, and the number of tokens for each point is calculated.
5.	Combine points into sub-chunks:
    - If it is not the last sub-chunk, each sub-chunk must contain at least 300 tokens and should not overlap.
    - Sub-chunks share the same chunk ID as the base chunk.
6.	Apply different algorithms:
    - **Raptor**: Generate summary chunks from sub-chunks using Raptor. Each summary chunk should be tagged with the base chunks it originates from.
    - **GraphRAG**: Extract entities and relationships from the sub-chunks using GraphRAG. Establish a correspondence between relationships and the base chunks, and create community reports where the relationships are tagged with their originating base chunks.
7.	Save the base chunks, Raptor's summary chunks, and GraphRAG's community reports in ChromaDB.
8.	Repeat steps 2–7 for each group.

### Query

1.	Search top k number of chunks based on the query question:
    - **Raptor** query: base chunk + summary chunks
    - **Graphrag** query: community reports
    - **Graphrag** + **Raptor**: community reports + summary chunks
    - Basic RAG: base chunk
2.	Process each chunk individually to extract the points relevant to the query.
3.	Consolidate all relevant points to generate the final answer.
4.	Tag the relevant chunks with the source group name and file name.

### Prompts

Please refer to [Prompts.md](Prompts.md).

### Comparison

Please refer to [Comparison.md](Comparison.md).

### Results

Please refer to [Results.md](Results.md).

### Translation

Please refer to [sutrallm/loop](https://github.com/sutrallm/loop) about how to translate Chinese sutras to English.

# Installation

Clone the repository:
```bash
git clone https://github.com/SutraAI/rg-rag.git
cd rg-rag
```

Create and activate a `conda` environment:
```bash
conda create -n rg-rag python=3.10
conda activate rg-rag
```

Install dependencies:
```bash
pip install --upgrade pip
pip install chromadb sentence_transformers scikit-learn umap-learn graphrag nltk
```

Install `pdftotext`:
```bash
sudo apt install build-essential libpoppler-cpp-dev pkg-config python3-dev
pip install pdftotext
```

Install `SGLang`:
```bash
pip install sgl-kernel --force-reinstall --no-deps
pip install "sglang[all]>=0.4.2.post2" --find-links https://flashinfer.ai/whl/cu124/torch2.5/flashinfer/
```

### Download models from HuggingFace
Download [meta-llama/Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/tree/main) 
and put them in `models/Llama-3.1-8B-Instruct/` folder.

Download [deepseek-ai/DeepSeek-R1-Distill-Llama-8B](https://huggingface.co/deepseek-ai/Deepseek-R1-Distill-Llama-8B/tree/main) and put them in `models/Deepseek-R1-Distill-Llama-8B/` folder.

### Prepare documents
Copy some documents into the `input_groups` folder:
```bash
$ ls -alh my_graphrag/input_groups/
total 12K
drwxrwxr-x  3 user2 user2 4.0K Jan 26 15:20 .
drwxrwxr-x 15 user2 user2 4.0K Jan 26 15:13 ..
drwxrwxr-x  2 user2 user2 4.0K Jan 26 15:20 diamond

$ ls -alh my_graphrag/input_groups/diamond/
total 40K
drwxrwxr-x 2 user2 user2 4.0K Jan 26 15:20 .
drwxrwxr-x 3 user2 user2 4.0K Jan 26 15:20 ..
-rw-r--r-- 1 user2 user2  29K Jan 26 15:19 diamond-en.txt
```

### Index
```bash
conda activate rg-rag
python index.py [options]
```
##### Options
| Argument           | Short | Type   | Default Value                   | Description                                                                                                                     |
|--------------------|-------|--------|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `--help`           | `-h`  |        |                                 | Show the help message of all options and exit.                                                                                  |
| `--db_path`        | `-p`  | `str`  | `./my_graphrag/vector_database` | Specify the database path. If the path already exists, check whether the document is in the db, if not, add to the db.          |
| `--raptor`         | `-r`  | `bool` | `True`                          | If True, run raptor index. If False, skip raptor index.                                                                         |
| `--graphrag`       | `-g`  | `bool` | `True`                          | If True, run graphrag index. If False, skip graphrag index.                                                                     |
| `--del_group`      | `-d`  | `int`  | `-1`                            | ID of the group to delete. If not provided, skip.                                                                               |
| `--del_option`     | `-o`  | `str`  | `all`                           | Options: ['all', 'graphrag', 'raptor']. Choose which part you want to delete in the group.                                      |
| `--export_prompts` |       | `bool` | `False`                         | If True, export the input and output text of all 3 index prompts to prompts folder. If False, skip exporting. Default is False. |
<details>
  <summary>Index the Diamond sutra</summary>

  ```
  $ python index.py --db_path ./my_graphrag/vector_db_diamond/
  
  🚀 Reading settings from /home/user2/rg-rag-02/my_graphrag/output/tmp_config/settings.yaml
  🚀 create_base_text_units
                                    id  ... n_tokens
  0   46537e893c14ae2e90018efca560b02f  ...      300
  1   0c6d1237424d5858a69b554ce4b0cb28  ...      300
  2   df28ae9610870345f62ce9897751fe3f  ...      121
  3   b0e5dadd3ff4483ce4d97f3fdbb82a38  ...      300
  4   54a89f340e7905b3663c8aa264c9bc3c  ...      300
  5   9c92731278f57dd628524ceb6b64a30b  ...      300
  6   d3769b2dc8bb800bcfea164265fd6353  ...      300
  7   10340e865bfce75239b2992b0c5a44ea  ...      300
  8   26c46f8070266944c29f76139a31d018  ...      300
  9   f73974e8dff7b296bbe7746c4661a0fc  ...      300
  10  38f8e3880b7a228945d44a068f6c0fcf  ...      300
  11  5c06814e27f34cf5abe365a429a531a4  ...      300
  12  bca6329d816ee1913a85a40dd7205aa8  ...      300
  13  0f113b68cd94d981f44da57e7f8dc253  ...      300
  14  2e6301f72dc7a7c0a69367e68751602f  ...      300
  15  db3ac6eca284ddfbfb7068a7da56a505  ...      300
  16  862980b81300473c47d1ad0f61b49469  ...      300
  17  780fb493f07946a741b4526b9bb42a20  ...      300
  18  c7b2180beb4b526d2c73fa005721cf76  ...      300
  19  31cf4ea605ebf44b5f6a4c96e1c8d644  ...      300
  20  949f147964ec2017a5b591de2264528e  ...      300
  21  be93d980546b9af0c87b14b20565ba85  ...      300
  22  d0d64db8e8ea5582dd2f03db84e52d31  ...      300
  23  5a1a4fd0d8fac99cd7afa35659b8bf29  ...      300
  24  1d86c14e76974deeb80751bd617308fb  ...      300
  25  1c65f13918a96d13d3d75d8f106d3196  ...      300
  26  483f9e4c6097de34ed65b71f0cb89ff0  ...      300
  27  720a05238ff4b85665cbc0f8f781d2ee  ...      300
  28  b34078be4f92ec3d9a984a068a878a46  ...      300
  29  0932d2e4414c41c098e3bdbe96d47ca6  ...      300
  30  3d98b1afd2e209a6301f31c9b497d3b4  ...      300
  31  304d5a3144cc066881b165ae658b05eb  ...      300
  32  8b1ada13ed9bad56010f5b0eb6db7500  ...      300
  33  a81ea2c3169cf85b359216af3ed911b7  ...      300
  34  87ddb2fe0952bee211b7934c047c3dc1  ...      300
  35  28df9a0fe28d1c5ab0f125d95a43a714  ...      300
  36  99ff8cbaff897ee5478df6c008dc871e  ...      251
  37  e6eacdac5fae829f1486ef2bdba5daff  ...       51

  [38 rows x 5 columns]
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
  2      2  <graphml xmlns="http://graphml.graphdrawing.or...
  🚀 create_final_entities
                                     id  ...                              description_embedding
  0    b45241d70f0e43fca764df95b2b81f77  ...  [-0.5144325494766235, 1.35825777053833, -3.503...
  1    4119fd06010c494caa07f439b333f4c5  ...  [0.2921435534954071, 1.5305653810501099, -3.20...
  2    d3835bf3dda84ead99deadbeac5d0d7d  ...  [0.07312427461147308, 1.9807318449020386, -3.3...
  3    077d2820ae1845bcbb1803379a3d1eae  ...  [-0.831592321395874, 1.4747486114501953, -3.20...
  4    3671ea0dd4e84c1a9b02c5ab2c8f4bac  ...  [0.2537393569946289, 1.6637612581253052, -3.35...
  ..                                ...  ...                                                ...
  125  ce54725672a74ebcabe6127577dacb2b  ...  [0.797076404094696, 0.660879373550415, -4.0441...
  126  ea2b28ca1a974ffab4517811dc1d1e5c  ...  [1.04007089138031, 1.6592302322387695, -3.6066...
  127  aff21f1da1654e7babdcf3fb0e4a75fc  ...  [-0.3070426285266876, 0.7706987857818604, -3.7...
  128  dc2cc9016e3f49dbac7232f05cce794d  ...  [0.8703882098197937, 0.5144550800323486, -4.22...
  129  6ea0cef05f694dcea455478f40674e45  ...  [1.0551612377166748, 1.498018503189087, -3.959...

  [130 rows x 8 columns]
  🚀 create_final_nodes
       level         title        type  ...                 top_level_node_id  x  y
  0        0  BODHISATTVAS       GROUP  ...  b45241d70f0e43fca764df95b2b81f77  0  0
  1        0       SUBHUTI      PERSON  ...  4119fd06010c494caa07f439b333f4c5  0  0
  2        0     TATHAGATA      PERSON  ...  d3835bf3dda84ead99deadbeac5d0d7d  0  0
  3        0    MHASATTVAS       GROUP  ...  077d2820ae1845bcbb1803379a3d1eae  0  0
  4        0       NIRVANA     CONCEPT  ...  3671ea0dd4e84c1a9b02c5ab2c8f4bac  0  0
  ..     ...           ...         ...  ...                               ... .. ..
  385      2     ILLUSIONS     CONCEPT  ...  ce54725672a74ebcabe6127577dacb2b  0  0
  386      2       BUBBLES     CONCEPT  ...  ea2b28ca1a974ffab4517811dc1d1e5c  0  0
  387      2        SADOWS     CONCEPT  ...  aff21f1da1654e7babdcf3fb0e4a75fc  0  0
  388      2           DEW  PHENOMENON  ...  dc2cc9016e3f49dbac7232f05cce794d  0  0
  389      2     LIGHTNING  PHENOMENON  ...  6ea0cef05f694dcea455478f40674e45  0  0

  [390 rows x 14 columns]
  🚀 create_final_communities
      id  ...                                      text_unit_ids
  0    4  ...                 [0c6d1237424d5858a69b554ce4b0cb28]
  1    0  ...  [0932d2e4414c41c098e3bdbe96d47ca6,0c6d1237424d...
  2    1  ...  [0c6d1237424d5858a69b554ce4b0cb28,9c92731278f5...
  3    3  ...  [949f147964ec2017a5b591de2264528e,9c92731278f5...
  4    5  ...                 
  5    2  ...  [99ff8cbaff897ee5478df6c008dc871e,d3769b2dc8bb...
  6    6  ...  [0932d2e4414c41c098e3bdbe96d47ca6,0c6d1237424d...
  7    9  ...  [0c6d1237424d5858a69b554ce4b0cb28,9c92731278f5...
  8   10  ...  [1c65f13918a96d13d3d75d8f106d3196,1d86c14e7697...
  9    7  ...  [483f9e4c6097de34ed65b71f0cb89ff0,54a89f340e79...
  10  13  ...  [949f147964ec2017a5b591de2264528e,9c92731278f5...
  11   8  ...  [0932d2e4414c41c098e3bdbe96d47ca6,1d86c14e7697...
  12  11  ...  [0932d2e4414c41c098e3bdbe96d47ca6,0f113b68cd94...
  13  12  ...  [31cf4ea605ebf44b5f6a4c96e1c8d644,5c06814e27f3...
  14  14  ...  [949f147964ec2017a5b591de2264528e,9c92731278f5...
  15  15  ...                 [10340e865bfce75239b2992b0c5a44ea]
  16  16  ...  [0f113b68cd94d981f44da57e7f8dc253,2e6301f72dc7...

  [17 rows x 6 columns]
  🚀 join_text_units_to_entity_ids
                         text_unit_ids  ...                                id
  0   0c6d1237424d5858a69b554ce4b0cb28  ...  0c6d1237424d5858a69b554ce4b0cb28
  1   0932d2e4414c41c098e3bdbe96d47ca6  ...  0932d2e4414c41c098e3bdbe96d47ca6
  2   0f113b68cd94d981f44da57e7f8dc253  ...  0f113b68cd94d981f44da57e7f8dc253
  3   10340e865bfce75239b2992b0c5a44ea  ...  10340e865bfce75239b2992b0c5a44ea
  4   1c65f13918a96d13d3d75d8f106d3196  ...  1c65f13918a96d13d3d75d8f106d3196
  5   1d86c14e76974deeb80751bd617308fb  ...  1d86c14e76974deeb80751bd617308fb
  6   28df9a0fe28d1c5ab0f125d95a43a714  ...  28df9a0fe28d1c5ab0f125d95a43a714
  7   2e6301f72dc7a7c0a69367e68751602f  ...  2e6301f72dc7a7c0a69367e68751602f
  8   304d5a3144cc066881b165ae658b05eb  ...  304d5a3144cc066881b165ae658b05eb
  9   31cf4ea605ebf44b5f6a4c96e1c8d644  ...  31cf4ea605ebf44b5f6a4c96e1c8d644
  10  3d98b1afd2e209a6301f31c9b497d3b4  ...  3d98b1afd2e209a6301f31c9b497d3b4
  11  483f9e4c6097de34ed65b71f0cb89ff0  ...  483f9e4c6097de34ed65b71f0cb89ff0
  12  54a89f340e7905b3663c8aa264c9bc3c  ...  54a89f340e7905b3663c8aa264c9bc3c
  13  5a1a4fd0d8fac99cd7afa35659b8bf29  ...  5a1a4fd0d8fac99cd7afa35659b8bf29
  14  5c06814e27f34cf5abe365a429a531a4  ...  5c06814e27f34cf5abe365a429a531a4
  15  720a05238ff4b85665cbc0f8f781d2ee  ...  720a05238ff4b85665cbc0f8f781d2ee
  16  862980b81300473c47d1ad0f61b49469  ...  862980b81300473c47d1ad0f61b49469
  17  87ddb2fe0952bee211b7934c047c3dc1  ...  87ddb2fe0952bee211b7934c047c3dc1
  18  8b1ada13ed9bad56010f5b0eb6db7500  ...  8b1ada13ed9bad56010f5b0eb6db7500
  19  949f147964ec2017a5b591de2264528e  ...  949f147964ec2017a5b591de2264528e
  20  99ff8cbaff897ee5478df6c008dc871e  ...  99ff8cbaff897ee5478df6c008dc871e
  21  9c92731278f57dd628524ceb6b64a30b  ...  9c92731278f57dd628524ceb6b64a30b
  22  a81ea2c3169cf85b359216af3ed911b7  ...  a81ea2c3169cf85b359216af3ed911b7
  23  b34078be4f92ec3d9a984a068a878a46  ...  b34078be4f92ec3d9a984a068a878a46
  24  bca6329d816ee1913a85a40dd7205aa8  ...  bca6329d816ee1913a85a40dd7205aa8
  25  c7b2180beb4b526d2c73fa005721cf76  ...  c7b2180beb4b526d2c73fa005721cf76
  26  d0d64db8e8ea5582dd2f03db84e52d31  ...  d0d64db8e8ea5582dd2f03db84e52d31
  27  d3769b2dc8bb800bcfea164265fd6353  ...  d3769b2dc8bb800bcfea164265fd6353
  28  df28ae9610870345f62ce9897751fe3f  ...  df28ae9610870345f62ce9897751fe3f
  29  f73974e8dff7b296bbe7746c4661a0fc  ...  f73974e8dff7b296bbe7746c4661a0fc

  [30 rows x 3 columns]
  🚀 create_final_relationships
             source      target  weight  ... source_degree target_degree rank
  0    BODHISATTVAS   TATHAGATA     7.0  ...             4            67   71
  1    BODHISATTVAS  MHASATTVAS    13.0  ...             4             4    8
  2    BODHISATTVAS     NIRVANA     1.0  ...             4             7   11
  3    BODHISATTVAS     SUBHUTI     1.0  ...             4            46   50
  4         SUBHUTI   TATHAGATA   284.0  ...            46            67  113
  ..            ...         ...     ...  ...           ...           ...  ...
  190        DREAMS      SADOWS     1.0  ...             3             3    6
  191     ILLUSIONS     BUBBLES     1.0  ...             3             3    6
  192     ILLUSIONS      SADOWS     1.0  ...             3             3    6
  193       BUBBLES      SADOWS     1.0  ...             3             3    6
  194           DEW   LIGHTNING     1.0  ...             1             1    2

  [195 rows x 10 columns]
  🚀 join_text_units_to_relationship_ids
                                    id                                   relationship_ids
  0   0c6d1237424d5858a69b554ce4b0cb28  [7ab5d53a872f4dfc98f3d386879f3c75, af1d0fec221...
  1   0f113b68cd94d981f44da57e7f8dc253  [cd130938a2844050be991af70baf5ee0, 422433aa458...
  2   10340e865bfce75239b2992b0c5a44ea  [cd130938a2844050be991af70baf5ee0, 18b839da898...
  3   1c65f13918a96d13d3d75d8f106d3196  [cd130938a2844050be991af70baf5ee0, 525f41ea202...
  4   1d86c14e76974deeb80751bd617308fb  [cd130938a2844050be991af70baf5ee0, 525f41ea202...
  5   28df9a0fe28d1c5ab0f125d95a43a714  [cd130938a2844050be991af70baf5ee0, 18b839da898...
  6   304d5a3144cc066881b165ae658b05eb  [cd130938a2844050be991af70baf5ee0, 496f17c2f74...
  7   3d98b1afd2e209a6301f31c9b497d3b4  [cd130938a2844050be991af70baf5ee0, 30c9641543c...
  8   483f9e4c6097de34ed65b71f0cb89ff0  [cd130938a2844050be991af70baf5ee0, 071a416efbe...
  9   5a1a4fd0d8fac99cd7afa35659b8bf29  [cd130938a2844050be991af70baf5ee0, 422433aa458...
  10  720a05238ff4b85665cbc0f8f781d2ee  [cd130938a2844050be991af70baf5ee0, 86505bca739...
  11  87ddb2fe0952bee211b7934c047c3dc1  [cd130938a2844050be991af70baf5ee0, 071a416efbe...
  12  99ff8cbaff897ee5478df6c008dc871e  [cd130938a2844050be991af70baf5ee0, 071a416efbe...
  13  9c92731278f57dd628524ceb6b64a30b  [cd130938a2844050be991af70baf5ee0, a671bf7fea2...
  14  a81ea2c3169cf85b359216af3ed911b7  [cd130938a2844050be991af70baf5ee0, 18b839da898...
  15  b34078be4f92ec3d9a984a068a878a46  [cd130938a2844050be991af70baf5ee0, 071a416efbe...
  16  c7b2180beb4b526d2c73fa005721cf76  [cd130938a2844050be991af70baf5ee0, 4d999d7744b...
  17  d0d64db8e8ea5582dd2f03db84e52d31  [cd130938a2844050be991af70baf5ee0, a671bf7fea2...
  18  f73974e8dff7b296bbe7746c4661a0fc  [cd130938a2844050be991af70baf5ee0, 071a416efbe...
  19  df28ae9610870345f62ce9897751fe3f  [a671bf7fea2f4514b6e96ba99127fafd, 525f41ea202...
  20  54a89f340e7905b3663c8aa264c9bc3c  [071a416efbec4f0886c19ac68f6d43cb, 6d8473ef3b1...
  21  0932d2e4414c41c098e3bdbe96d47ca6  [30c9641543c24773938bd8ec57ea98ab, 18b839da898...
  22  bca6329d816ee1913a85a40dd7205aa8  [30c9641543c24773938bd8ec57ea98ab, 422433aa458...
  23  d3769b2dc8bb800bcfea164265fd6353  [30c9641543c24773938bd8ec57ea98ab, 422433aa458...
  24  5c06814e27f34cf5abe365a429a531a4  [422433aa45804c7ebb973b2fafce5da6, 353d91abc68...
  25  949f147964ec2017a5b591de2264528e  [422433aa45804c7ebb973b2fafce5da6, 1af9faf341e...
  26  31cf4ea605ebf44b5f6a4c96e1c8d644  [4d999d7744b04a998475f8f8531589f0, 4465efb7f6e...
  🚀 create_final_community_reports
     community  ...                                    id
  0         14  ...  b3a44cc1-4762-42b5-84f9-957b8d7c2d57
  1         15  ...  cb2f0c3d-fd6c-4f77-9f02-846d200f6beb
  2         16  ...  8d5dac89-04c8-4d62-8679-33b6d1ccb083
  3         10  ...  b2fbd2e1-92e5-4f74-9a24-acff507c6ed1
  4         11  ...  bb3fc4cc-e840-44a1-8c36-f29b42d07c58
  5         12  ...  70e9333f-a32c-4afc-b974-58dcf39636c5
  6         13  ...  a7a6b8d9-b9ab-4414-8463-f12c3bca6c7a
  7          6  ...  b365a14e-bbb3-4202-bb87-57bb8dcc6741
  8          7  ...  81534223-a1e2-48f6-83ea-3179bbe73fe1
  9          8  ...  de8a2143-6c9e-4ef6-b96b-bf9c2075a0a1
  10         9  ...  898399f9-95c7-47b1-8851-4635e84c9862
  11         0  ...  dccfd1dd-3736-4104-8d1b-7f29ef5a15a7
  12         1  ...  d41ea067-4e3b-4d43-aa98-7b8ed3f03f16
  13         2  ...  132945a7-1c8f-44f3-b263-b6a1e8598e61
  14         3  ...  12b0855a-dbba-4e91-acd5-1d18ebf89635
  15         4  ...  a290fa3d-486f-41e7-867a-34f7e2f74d44
  16         5  ...  01f18773-306c-4ed3-a992-842e73151627

  [17 rows x 10 columns]
  🚀 create_final_text_units
                                    id  ...                                   relationship_ids
  0   0c6d1237424d5858a69b554ce4b0cb28  ...  [7ab5d53a872f4dfc98f3d386879f3c75, af1d0fec221...
  1   df28ae9610870345f62ce9897751fe3f  ...  [a671bf7fea2f4514b6e96ba99127fafd, 525f41ea202...
  2   54a89f340e7905b3663c8aa264c9bc3c  ...  [071a416efbec4f0886c19ac68f6d43cb, 6d8473ef3b1...
  3   9c92731278f57dd628524ceb6b64a30b  ...  [cd130938a2844050be991af70baf5ee0, a671bf7fea2...
  4   d3769b2dc8bb800bcfea164265fd6353  ...  [30c9641543c24773938bd8ec57ea98ab, 422433aa458...
  5   10340e865bfce75239b2992b0c5a44ea  ...  [cd130938a2844050be991af70baf5ee0, 18b839da898...
  6   f73974e8dff7b296bbe7746c4661a0fc  ...  [cd130938a2844050be991af70baf5ee0, 071a416efbe...
  7   5c06814e27f34cf5abe365a429a531a4  ...  [422433aa45804c7ebb973b2fafce5da6, 353d91abc68...
  8   bca6329d816ee1913a85a40dd7205aa8  ...  [30c9641543c24773938bd8ec57ea98ab, 422433aa458...
  9   0f113b68cd94d981f44da57e7f8dc253  ...  [cd130938a2844050be991af70baf5ee0, 422433aa458...
  10  c7b2180beb4b526d2c73fa005721cf76  ...  [cd130938a2844050be991af70baf5ee0, 4d999d7744b...
  11  31cf4ea605ebf44b5f6a4c96e1c8d644  ...  [4d999d7744b04a998475f8f8531589f0, 4465efb7f6e...
  12  949f147964ec2017a5b591de2264528e  ...  [422433aa45804c7ebb973b2fafce5da6, 1af9faf341e...
  13  d0d64db8e8ea5582dd2f03db84e52d31  ...  [cd130938a2844050be991af70baf5ee0, a671bf7fea2...
  14  5a1a4fd0d8fac99cd7afa35659b8bf29  ...  [cd130938a2844050be991af70baf5ee0, 422433aa458...
  15  1d86c14e76974deeb80751bd617308fb  ...  [cd130938a2844050be991af70baf5ee0, 525f41ea202...
  16  1c65f13918a96d13d3d75d8f106d3196  ...  [cd130938a2844050be991af70baf5ee0, 525f41ea202...
  17  483f9e4c6097de34ed65b71f0cb89ff0  ...  [cd130938a2844050be991af70baf5ee0, 071a416efbe...
  18  720a05238ff4b85665cbc0f8f781d2ee  ...  [cd130938a2844050be991af70baf5ee0, 86505bca739...
  19  b34078be4f92ec3d9a984a068a878a46  ...  [cd130938a2844050be991af70baf5ee0, 071a416efbe...
  20  0932d2e4414c41c098e3bdbe96d47ca6  ...  [30c9641543c24773938bd8ec57ea98ab, 18b839da898...
  21  3d98b1afd2e209a6301f31c9b497d3b4  ...  [cd130938a2844050be991af70baf5ee0, 30c9641543c...
  22  304d5a3144cc066881b165ae658b05eb  ...  [cd130938a2844050be991af70baf5ee0, 496f17c2f74...
  23  a81ea2c3169cf85b359216af3ed911b7  ...  [cd130938a2844050be991af70baf5ee0, 18b839da898...
  24  87ddb2fe0952bee211b7934c047c3dc1  ...  [cd130938a2844050be991af70baf5ee0, 071a416efbe...
  25  28df9a0fe28d1c5ab0f125d95a43a714  ...  [cd130938a2844050be991af70baf5ee0, 18b839da898...
  26  99ff8cbaff897ee5478df6c008dc871e  ...  [cd130938a2844050be991af70baf5ee0, 071a416efbe...
  27  2e6301f72dc7a7c0a69367e68751602f  ...                                               None
  28  862980b81300473c47d1ad0f61b49469  ...                                               None
  29  8b1ada13ed9bad56010f5b0eb6db7500  ...                                               None
  30  46537e893c14ae2e90018efca560b02f  ...                                               None
  31  b0e5dadd3ff4483ce4d97f3fdbb82a38  ...                                               None
  32  26c46f8070266944c29f76139a31d018  ...                                               None
  33  38f8e3880b7a228945d44a068f6c0fcf  ...                                               None
  34  db3ac6eca284ddfbfb7068a7da56a505  ...                                               None
  35  780fb493f07946a741b4526b9bb42a20  ...                                               None
  36  be93d980546b9af0c87b14b20565ba85  ...                                               None
  37  e6eacdac5fae829f1486ef2bdba5daff  ...                                               None

  [38 rows x 6 columns]
  🚀 create_base_documents
                                   id  ...           title
  0  b0f66a39076ef23be0308fe7b13b7aaa  ...  diamond-en.txt

  [1 rows x 4 columns]
  🚀 create_final_documents
                                   id  ...           title
  0  b0f66a39076ef23be0308fe7b13b7aaa  ...  diamond-en.txt

  [1 rows x 4 columns]
  ⠧ GraphRAG Indexer 
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
  Disconnection_distance = 2 has removed 0 edges.
  It has fully disconnected 2 vertices.
  You might consider using find_disconnected_points() to find and remove these points from your data.
  Use umap.utils.disconnected_vertices() to identify them.
    warn(
  graphrag run time: 1:02:45.151868
  raptor run time: 0:00:18.596147
  run time: 1:03:05.802866
  count of group: 1
  count of paper: 1
  count of chunk: 2
  count of relationship: 775
  count of community report: 17
  count of summary: 1
  ```
</details>

### Query
```bash
python query.py [options]
```
##### Options
| Argument              | Short | Type   | Default Value | Description                           |
|-----------------------|---|--------|----|---------------------------------------|
| `--help`              | `-h` |        |    | Show the help message of all options and exit. |
| `--question`          | `-q` | `str`  | `Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?` | Provide a question for query.         |
| `--db_path`           | `-p` | `str`  | `./my_graphrag/vector_database` | Specify the database path.            |
| `--list_group`        | `-l` | `bool` | `False` | If True, list group details. If False, execute the query. |
| `--group_id`          | `-i` | `int`  | `-1 (query all)` | Group ID to query. If not provided, query all. |
| `--query_option`      | `-o` | `int`  | `1` | 1. GraphRAG + Raptor: community report + summary; 2. Raptor: base + summary; 3. GraphRAG: community report; 4. Basic RAG: base |
| `--top_k`             | `-k` | `int`  | `20` | Top k number of chunks that query is based on. |
| `--export_reports`    |   | `bool` | `False` | If True, export the GraphRAG community reports or Raptor summaries. If False, do not export. Default is False. |
| `--export_type`       |   | `int`    | `1` | 1. GraphRAG community reports; 2. Raptor summaries                                      |
| `--export_group_name` |   | `str`    | `''` | You need to specify export_group_name or export_group_id. |
| `--export_group_id`   |   | `int`    | `-1` | You need to specify export_group_name or export_group_id. |
<details>
  <summary>Query the Diamond sutra</summary>

  ```
  $  python query.py --db_path ./my_graphrag/vector_db_diamond/ -q "what is the meaning of suffering?"

  GraphRAG + Raptor query ...
  Number of requested results 20 is greater than number of elements in index 1, updating n_results = 1
  Number of requested results 20 is greater than number of elements in index 17, updating n_results = 17
  --- final answer ---
  <question>
  what is the meaning of suffering?
  </question>

  <answer>
  **The Meaning of Suffering**

  Suffering is a complex and multifaceted concept that is deeply intertwined with the notion of self. According to Buddhist teachings, suffering arises from our attachment to the idea of a permanent and fixed self. This attachment creates a sense of separation and distinction between ourselves and others, leading to feelings of dissatisfaction, anxiety, and pain.

  The Tathagata emphasizes that clinging to the concept of self is an illusion that prevents us from understanding the true nature of reality. Non-attachment to the notion of self is essential for spiritual growth and enlightenment, as it allows us to transcend our limited perspectives and experience a deeper sense of interconnectedness with all phenomena.

  Suffering is also closely related to the idea of impermanence and the lack of inherent existence in all things. The Tathagata teaches that all phenomena are transient and lack enduring existence, which can lead to feelings of uncertainty and insecurity. However, this understanding can also be a catalyst for spiritual growth, as it encourages us to let go of our attachments and cultivate a sense of detachment.

  In Buddhist teachings, suffering is seen as a fundamental aspect of the human experience that arises from our ignorance of the true nature of reality. The ultimate goal of Bodhisattvas is to lead all sentient beings to Anuttara-samyak-sambodhi, the highest state of enlightenment, which implies liberation from suffering.

  The concept of non-attachment is essential for achieving enlightenment and promoting compassion for all sentient beings. This involves letting go of attachments to concepts such as self, person, being, or lifespan, and cultivating a sense of detachment that allows us to see things as they truly are.

  Suffering can also be understood in relation to the concept of Nirvana, which represents a state of being that is free from suffering, rebirth, and attachment. The attainment of Nirvana serves as a model for others to follow, emphasizing the potential for spiritual growth and enlightenment.

  Ultimately, the meaning of suffering is deeply connected to our understanding of the nature of reality and our place within it. By cultivating a deeper understanding of the impermanence and interconnectedness of all phenomena, we can begin to transcend our limited perspectives and experience a sense of liberation from suffering.

  **Key Aspects of Suffering**

  1. **Attachment to self**: Clinging to the idea of a permanent and fixed self creates a sense of separation and distinction between ourselves and others, leading to feelings of dissatisfaction, anxiety, and pain.
  2. **Impermanence**: The understanding that all phenomena are transient and lack enduring existence can lead to feelings of uncertainty and insecurity.
  3. **Non-attachment**: Letting go of attachments to concepts such as self, person, being, or lifespan is essential for achieving enlightenment and promoting compassion for all sentient beings.
  4. **Interconnectedness**: Recognizing the interconnectedness of all phenomena allows us to transcend our limited perspectives and experience a deeper sense of unity with all things.
  5. **Nirvana**: The attainment of Nirvana represents a state of being that is free from suffering, rebirth, and attachment.

  **Implications for Spiritual Growth**

  1. **Cultivating detachment**: Letting go of attachments to concepts such as self, person, being, or lifespan allows us to cultivate a sense of detachment that enables us to see things as they truly are.
  2. **Understanding impermanence**: Recognizing the impermanence of all phenomena encourages us to let go of our attachments and cultivate a sense of acceptance and equanimity.
  3. **Developing compassion**: Cultivating non-attachment and understanding the interconnectedness of all phenomena allows us to develop compassion for all sentient beings.
  4. **Achieving enlightenment**: The ultimate goal of Bodhisattvas is to lead all sentient beings to Anuttara-samyak-sambodhi, the highest state of enlightenment, which implies liberation from suffering.

  **Conclusion**

  Suffering is a complex and multifaceted concept that arises from our attachment to the idea of a permanent and fixed self. By cultivating non-attachment, understanding impermanence, and recognizing the interconnectedness of all phenomena, we can begin to transcend our limited perspectives and experience a sense of liberation from suffering. Ultimately, the meaning of suffering is deeply connected to our understanding of the nature of reality and our place within it.
  </answer>

  <reference>
  diamond: diamond-en
  </reference>

  --- final answer ---
  run time: 0:00:53.279285
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
