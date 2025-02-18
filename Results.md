# Results
We have 2 databases, one for `n0006` and one for `t0235`.

## Machine configuration
<table>
<tbody>
<tr valign="top">
<td>
Machine
</td>
<td>
dnn4
</td>
</tr>
<tr valign="top">
<td>
CPU
</td>
<td>
Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz
</td>
</tr>
<tr valign="top">
<td>
Memory
</td>
<td>
32GB
</td>
</tr>
<tr valign="top">
<td>
GPU
</td>
<td>
NVIDIA GeForce RTX 4090
</td>
</tr>
<tr valign="top">
<td>
GPU memory
</td>
<td>
24GB
</td>
</tr>
</tbody>
</table>

## Run time

<h3>Index</h3>
<table>
<tbody>
<tr valign="top">
<td>
Group name
</td>
<td>
Start time
</td>
<td>
GraphRAG run time
</td>
<td>
Raptor run time
</td>
</tr>
<tr valign="top">
<td>
t0235
</td>
<td>
2025-02-13-14-24-51
</td>
<td>
0:05:29
</td>
<td>
0:00:14
</td>
</tr>
<tr valign="top">
<td>
n0006
</td>
<td>
2025-02-13-15-28-00
</td>
<td>
15:08:31
</td>
<td>
0:13:42
</td>
</tr>
</tbody>
</table>
<h3>Query</h3>
<table>
<tbody>
<tr valign="top">
<td>
Group name
</td>
<td>
GraphRAG + Raptor query
</td>
<td>
Raptor query
</td>
<td>
GraphRAG query
</td>
<td>
Basic RAG query
</td>
</tr>
<tr valign="top">
<td>
t0235
</td>
<td>
0:01:43
</td>
<td>
0:00:55
</td>
<td>
0:00:56
</td>
<td>
0:00:47
</td>
</tr>
<tr valign="top">
<td>
n0006
</td>
<td>
0:04:23
</td>
<td>
0:03:48
</td>
<td>
0:03:31
</td>
<td>
0:03:18
</td>
</tr>
</tbody>
</table>

## t0235

<h3>File and folder location</h3>
<table>
<tbody>
<tr valign="top">
<td>
Description
</td>
<td>
Location
</td>
</tr>
<tr valign="top">
<td>
Vector database
</td>
<td>
 
`/home/user2/rg-rag-02/my_graphrag/vector_db_t0235_20250213`
</td>
</tr>
<tr valign="top">
<td>
Output folder
</td>
<td>
 
`/home/user2/rg-rag-02/output/vector_db_t0235_20250213`
</td>
</tr>
<tr valign="top">
<td>
Index log file
</td>
<td>
  
`/home/user2/rg-rag-02/output/vector_db_t0235_20250213/index_log_2025-02-13-14-21-07.csv`
</td>
</tr>
<tr valign="top">
<td>
Index prompts folder
</td>
<td>

`/home/user2/rg-rag-02/output/vector_db_t0235_20250213/prompts`
</td>
</tr>
<tr valign="top">
<td>
Graphrag output folder
</td>
<td>

`/home/user2/rg-rag-02/output/vector_db_t0235_20250213/graphrag_output`
</td>
</tr>
</tbody>
</table>
<h3>Index command line</h3>

```
python index.py -p my_graphrag/vector_db_t0235_20250213/ --export_prompts True
```

<h3>Query</h3>
<h4>GraphRAG + Raptor query</h4>

```
python query.py -p "./my_graphrag/vector_db_t0235_20240213" -q "Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?" -o 1
```

```
<question>
Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?
</question>
<answer>
Buddhists indeed require knowledge and scholarship to effectively practice their faith, particularly for advanced spiritual goals. Here's a structured summary of the reasoning:
1. **Wisdom and Compassion**: The pursuit of Nirvana necessitates the cultivation of wisdom and compassion, which are integral to understanding the teachings and applying them in daily life.
2. **Merit and Virtuous Actions**: While merit is accumulated through virtuous actions, understanding how these actions contribute to spiritual progress requires knowledge of the teachings and ethical frameworks.
3. **Interconnectedness of Worlds**: The complexity of existence underscores the need for guidance and understanding, suggesting that knowledge helps navigate these complexities effectively.
4. **Tathagata's Teachings**: The teachings of the Buddha emphasize understanding the true nature of reality, which demands intellectual engagement and scholarly pursuit to grasp the principles needed for enlightenment.
5. **The Dharma as Guidance**: The universal truth (Dharma) serves as a guide, highlighting the necessity of knowledge and wisdom to follow its precepts and achieve enlightenment.
6. **Bodhisattva Path**: Bodhisattvas exemplify the importance of wisdom and knowledge, as their path involves deeply internalizing and applying the teachings without attachment to physical or mental phenomena.
7. **Advanced Texts and Critical Analysis**: The Prajnaparamita Sutra and other texts challenge conventional thinking, necessitating scholarly approaches and critical analysis to understand the dynamic nature of existence.
8. **Adaptability and Flexibility**: The teachings promote adaptability, suggesting that knowledge and flexibility in understanding are essential for practice, allowing for a deeper engagement with spiritual principles.
In conclusion, while Buddhists are encouraged to engage in virtuous actions and generate merit, achieving a meaningful practice requires a deeper understanding of the teachings, which is facilitated by knowledge and scholarly pursuit. This understanding is crucial for progressing along the path to enlightenment and embodying the principles of a Bodhisattva.
</answer>
<reference>
t0235: t0235
</reference>
```

<h4>Raptor query</h4>

```
python query.py -p "./my_graphrag/vector_db_t0235_20240213" -q "Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?" -o 2
```

```
<question>
Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?
</question>
<answer>
Buddhists indeed require knowledge and scholarship as integral components of their practice. While external acts of generosity and upholding teachings contribute to merit, the path to liberation necessitates a profound internal understanding. This understanding is achieved through the study of Buddhist texts like the Prajnaparamita Sutra, which emphasizes textual knowledge as crucial for accessing deeper truths. The process of seeking Anuttara-samyak-sambodhi involves transcending attachment, akin to understanding illusions, which often necessitates a knowledge of Buddhist concepts. The sutra's merit surpasses almsgiving, underscoring the value of study. Additionally, while external practices are valued, the ultimate realization and internal understanding are vital for liberation. Thus, knowledge and scholarship play a pivotal role in both individual spiritual growth and the collective benefit of others.
</answer>
<reference>
t0235: t0235
</reference>
```

<h4>GraphRAG query</h4>

```
python query.py -p "./my_graphrag/vector_db_t0235_20240213" -q "Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?" -o 3
```

```
<question>
Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?
</question>
<answer>
Buddhism places a significant emphasis on compassion, wisdom, and the accumulation of merit as key components for spiritual growth and achieving enlightenment. While these elements are crucial, the practice of Buddhism does not explicitly require extensive formal knowledge or scholarship. Instead, the focus is on personal actions, intentions, and the application of universal principles in daily life. The teachings of the Buddha, such as the Four Noble Truths and the Eightfold Path, are important, but they are more about understanding and application rather than deep academic study. The path to enlightenment is exemplified by bodhisattvas, who embody compassion and wisdom through their actions rather than their knowledge. Therefore, while knowledge can be beneficial, the primary emphasis is on compassion, wisdom, and virtuous deeds, making Buddhist practice accessible to anyone regardless of their academic background.
</answer>
<reference>
t0235: t0235
</reference>
```

<h4>Basic RAG query</h4>

```
python query.py -p "./my_graphrag/vector_db_t0235_20240213" -q "Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?" -o 4
```

```
<question>
Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?
</question>
<answer>
Buddhists indeed require knowledge and scholarship to practice their faith effectively. Central to Buddhism is the Four Noble Truths, which provide a foundational understanding of suffering, its origin, cessation, and the path to cessation. Without comprehension of these truths, practice remains superficial. The Dharma, the teachings of the Buddha, must be understood deeply, not just accepted on faith alone. This understanding fosters wisdom (prajna), which involves discernment and clarity, essential for viewing reality accurately.
Scholarship and knowledge are crucial for cultivating a pure mind, enabling one to transcend attachment to views and concepts. While not everyone may grasp these teachings easily, the emphasis is on using knowledge as a tool for growth rather than an end in itself. Mental purity is vital, ensuring that the insights gained lead to true enlightenment. Thus, while belief is part of Buddhism, it is enriched by intellectual engagement and wisdom, guiding practitioners toward genuine realization.
</answer>
<reference>
t0235: t0235
</reference>
```

## n0006

<h3>File and folder location</h3>
<table>
<tbody>
<tr valign="top">
<td>
Description
</td>
<td>
Location
</td>
</tr>
<tr valign="top">
<td>
Vector database
</td>
<td>

`/home/user2/rg-rag-02/my_graphrag/vector_db_n0006_20250213`
</td>
</tr>
<tr valign="top">
<td>
Output folder
</td>
<td>

`/home/user2/rg-rag-02/output/vector_db_n0006_20250213`
</td>
</tr>
<tr valign="top">
<td>
Index log file
</td>
<td>
 
`/home/user2/rg-rag-02/output/vector_db_n0006_20250213/index_log_2025-02-13-14-54-02.csv`
</td>
</tr>
<tr valign="top">
<td>
Index prompts folder
</td>
<td>

`/home/user2/rg-rag-02/output/vector_db_n0006_20250213/prompts`
</td>
</tr>
<tr valign="top">
<td>
Graphrag output folder
</td>
<td>

`/home/user2/rg-rag-02/output/vector_db_n0006_20250213/graphrag_output`
</td>
</tr>
</tbody>
</table>

<h3>Index command line</h3>

```
python index.py -p my_graphrag/vector_db_n0006_20250213/ --export_prompts True
```

<h3>Query</h3>
<h4>GraphRAG + Raptor query</h4>

```
python query.py -p my_graphrag/vector_db_n0006_20250213/ -q "Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?" -o 1
```

```
<question>
Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?
</question>
<answer>
**Do Buddhists Need Knowledge and Scholarship to Practice Buddhism?**
Buddhists indeed require knowledge and understanding, though the approach and extent may vary between monks and laypeople. Here's a structured breakdown:
1. **Monks and Knowledge**: Monks, as spiritual leaders, are expected to have an in-depth understanding of Buddhist teachings, requiring scholarly study and knowledge to effectively guide others. Their role involves preserving and transmitting the Dhamma, which necessitates deep knowledge.
2. **Laypeople and Understanding**: Laypeople gain understanding through practice, meditation, and engagement with the teachings. While formal scholarship isn't emphasized for laypeople, they must grasp the core principles, including the Four Noble Truths, to follow the path towards liberation.
3. **The Noble Eightfold Path**: Right Understanding, part of the path, requires comprehension of reality and the cause of suffering, highlighting the role of knowledge in spiritual growth. Laypeople's understanding is cultivated through practice rather than formal study.
4. **The Sangha's Role**: The monastic community plays a crucial role in preserving the Dhamma, underscoring the importance of knowledge for the continuity of Buddhist teachings.
5. **Emphasis on Practice**: While knowledge is essential, the focus for laypeople is more on ethical conduct, meditation, and virtues rather than formal education. The practice of Buddhism is centred around application through these methods.
In summary, knowledge and understanding are crucial for all Buddhists, with monks needing scholarly depth and laypeople developing their understanding through practice and engagement with Buddhist principles.
</answer>
<reference>
n0006: N0006_001-01, N0006_001-02, N0006_001-04, N0006_001-05, N0006_001-06, N0006_001-08, N0006_002-01, N0006_002-02, N0006_002-03, N0006_003-01, N0006_003-02, N0006_003-03, N0006_004-01, N0006_004-03, N0006_005-01, N0006_006-01, N0006_006-02, N0006_007-01, N0006_007-02, N0006_008-01, N0006_009-01, N0006_010-01, N0006_011-01, N0006_011-02, N0006_011-03, N0006_012-01, N0006_012-02, N0006_012-03, N0006_012-04, N0006_012-05, N0006_012-06, N0006_012-07, N0006_012-09, N0006_014-02, N0006_015-01, N0006_015-02, N0006_016-01, N0006_017-02, N0006_017-03, N0006_017-04, N0006_018-02, N0006_019-01, N0006_019-02, N0006_020-01, N0006_021-01, N0006_022-02, N0006_022-03, N0006_022-05, N0006_022-06, N0006_022-08, N0006_022-12, N0006_022-13, N0006_023-01, N0006_023-03, N0006_024-02, N0006_025-01, N0006_026-01, N0006_029-01, N0006_030-01, N0006_031-01, N0006_032-01, N0006_035-01, N0006_035-03, N0006_035-07, N0006_035-08, N0006_035-10, N0006_035-11, N0006_035-13, N0006_035-14, N0006_035-19, N0006_036-01, N0006_036-02, N0006_037-01, N0006_037-02, N0006_037-03, N0006_038-01, N0006_039-01, N0006_040-01, N0006_041-01, N0006_042-01, N0006_043-01, N0006_043-02, N0006_044-01, N0006_045-02, N0006_045-04, N0006_045-06, N0006_045-08, N0006_046-01, N0006_046-02, N0006_046-03, N0006_046-04, N0006_046-05, N0006_046-06, N0006_046-07, N0006_046-09, N0006_046-13, N0006_046-14, N0006_047-01, N0006_047-02, N0006_047-04, N0006_047-05, N0006_047-06, N0006_047-07, N0006_048-01, N0006_048-02, N0006_048-05, N0006_048-06, N0006_048-07, N0006_048-08, N0006_048-12, N0006_048-13, N0006_048-14, N0006_048-15, N0006_048-17, N0006_049-01, N0006_049-02, N0006_049-04, N0006_050-04, N0006_050-05, N0006_050-06, N0006_051-01, N0006_051-02, N0006_051-04, N0006_051-05, N0006_051-06, N0006_051-08, N0006_052-02, N0006_053-01, N0006_054-01, N0006_054-02, N0006_055-01, N0006_055-02, N0006_055-03, N0006_055-04, N0006_055-05, N0006_055-06, N0006_056-01, N0006_056-02, N0006_056-03, N0006_056-04, N0006_056-05, N0006_056-07, N0006_056-08, N0006_056-09, N0006_056-10
</reference>
```

<h4>Raptor query</h4>

```
python query.py -p my_graphrag/vector_db_n0006_20250213/ -q "Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?" -o 2
```

```
<question>
Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?
</question>
<answer>
**Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?**
**Answer:**
Yes, Buddhists require knowledge and scholarship to effectively practice Buddhism. The practice of Buddhism is deeply intertwined with understanding the complex philosophical concepts such as dependent origination, impermanence, and not-self. These concepts are essential for achieving liberation. The Four Noble Truths, which form the foundation of Buddhist teachings, require a combination of knowledge and wisdom to be comprehended and applied in daily life.
The Noble Eightfold Path, a core aspect of Buddhist practice, includes elements like right view, which involve understanding suffering, its origin, and the path to its cessation. This understanding necessitates cognitive effort and knowledge. While the Dhamma can be applied in the present moment, a grasp of its principles and teachings is crucial for meaningful application.
The five faculties-faith, energy, mindfulness, concentration, and wisdom-are essential for spiritual growth. Wisdom, in particular, is listed as one of the seven factors of enlightenment, developed through practices like meditation and virtue. Without knowledge and understanding, one cannot fully engage with the teachings and achieve liberation.
Though the emphasis is on inner wisdom and practices like meditation, the role of knowledge and scholarship in studying and internalizing the Dhamma is acknowledged. Without this, followers cannot fully grasp the teachings and apply them effectively in their spiritual journey. Thus, while the path involves immediate application, the foundation of such application is built on a deep understanding and study of Buddhist principles.
</answer>
<reference>
n0006: N0006_001-01, N0006_001-02, N0006_001-03, N0006_001-04, N0006_001-05, N0006_001-06, N0006_001-07, N0006_001-08, N0006_002-01, N0006_002-02, N0006_002-03, N0006_003-01, N0006_003-02, N0006_003-03, N0006_004-01, N0006_004-02, N0006_004-03, N0006_005-01, N0006_006-01, N0006_006-02, N0006_007-01, N0006_007-02, N0006_008-01, N0006_009-01, N0006_010-01, N0006_011-01, N0006_011-02, N0006_011-03, N0006_012-01, N0006_012-02, N0006_012-03, N0006_012-04, N0006_012-05, N0006_012-06, N0006_012-07, N0006_012-08, N0006_012-09, N0006_013-01, N0006_014-01, N0006_014-02, N0006_014-03, N0006_014-04, N0006_015-01, N0006_015-02, N0006_016-01, N0006_017-01, N0006_017-02, N0006_017-03, N0006_017-04, N0006_018-01, N0006_018-02, N0006_019-01, N0006_019-02, N0006_020-01, N0006_021-01, N0006_022-01, N0006_022-02, N0006_022-03, N0006_022-04, N0006_022-05, N0006_022-06, N0006_022-07, N0006_022-08, N0006_022-09, N0006_022-10, N0006_022-11, N0006_022-12, N0006_022-13, N0006_022-14, N0006_022-15, N0006_023-01, N0006_023-02, N0006_023-03, N0006_023-04, N0006_024-01, N0006_024-02, N0006_025-01, N0006_026-01, N0006_027-01, N0006_028-01, N0006_029-01, N0006_030-01, N0006_031-01, N0006_032-01, N0006_033-01, N0006_034-01, N0006_035-01, N0006_035-02, N0006_035-03, N0006_035-04, N0006_035-05, N0006_035-06, N0006_035-07, N0006_035-08, N0006_035-09, N0006_035-10, N0006_035-11, N0006_035-12, N0006_035-13, N0006_035-14, N0006_035-15, N0006_035-16, N0006_035-17, N0006_035-18, N0006_035-19, N0006_036-01, N0006_036-02, N0006_036-03, N0006_037-01, N0006_037-02, N0006_037-03, N0006_038-01, N0006_039-01, N0006_040-01, N0006_041-01, N0006_042-01, N0006_043-01, N0006_043-02, N0006_044-01, N0006_045-01, N0006_045-02, N0006_045-03, N0006_045-04, N0006_045-05, N0006_045-06, N0006_045-07, N0006_045-08, N0006_046-01, N0006_046-02, N0006_046-03, N0006_046-04, N0006_046-05, N0006_046-06, N0006_046-07, N0006_046-08, N0006_046-09, N0006_046-10, N0006_046-11, N0006_046-12, N0006_046-13, N0006_046-14, N0006_046-15, N0006_046-16, N0006_046-17, N0006_046-18, N0006_047-01, N0006_047-02, N0006_047-03, N0006_047-04, N0006_047-05, N0006_047-06, N0006_047-07, N0006_047-08, N0006_047-09, N0006_047-10, N0006_048-01, N0006_048-02, N0006_048-03, N0006_048-04, N0006_048-05, N0006_048-06, N0006_048-07, N0006_048-08, N0006_048-09, N0006_048-10, N0006_048-11, N0006_048-12, N0006_048-13, N0006_048-14, N0006_048-15, N0006_048-16, N0006_048-17, N0006_049-01, N0006_049-02, N0006_049-03, N0006_049-04, N0006_049-05, N0006_050-01, N0006_050-02, N0006_050-03, N0006_050-04, N0006_050-05, N0006_050-06, N0006_050-07, N0006_050-08, N0006_050-09, N0006_050-10, N0006_051-01, N0006_051-02, N0006_051-03, N0006_051-04, N0006_051-05, N0006_051-06, N0006_051-07, N0006_051-08, N0006_052-01, N0006_052-02, N0006_053-01, N0006_053-02, N0006_053-03, N0006_053-04, N0006_053-05, N0006_054-01, N0006_054-02, N0006_055-01, N0006_055-02, N0006_055-03, N0006_055-04, N0006_055-05, N0006_055-06, N0006_055-07, N0006_056-01, N0006_056-02, N0006_056-03, N0006_056-04, N0006_056-05, N0006_056-06, N0006_056-07, N0006_056-08, N0006_056-09, N0006_056-10
</reference>
```

<h4>GraphRAG query</h4>

```
python query.py -p my_graphrag/vector_db_n0006_20250213/ -q "Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?" -o 3
```

```
<question>
Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?
</question>
<answer>
**Do Buddhists Require Knowledge and Scholarship to Practice Buddhism?**
Buddhists indeed place a significant emphasis on knowledge and understanding as essential components of their spiritual journey. While the extent to which individuals engage with formal scholarship may vary-between monastics and laypeople-knowledge and wisdom are crucial for different aspects of Buddhist practice.
1. **Monastic Role**: For monks and nuns, knowledge is vital. The five faculties, including knowledge, are described as essential for monks. The Noble Eightfold Path's right view requires understanding, and overcoming defilements involves transcending ignorance. Monastics use their accumulated knowledge to guide and inspire laypeople, indicating that knowledge is integral to their role in the community.
2. **Lay Practitioners**: While lay Buddhists may focus more on meditation and ethical conduct, they still benefit from knowledge. The Four Factors of Stream-Entry, including wisdom and understanding, are necessary for all practitioners. Lay followers possess wisdom that contributes to overcoming suffering, highlighting the value of knowledge in their practice.
3. **Central Role of the Sangha**: The monastic community (Sangha) is central to Buddhist practice. They preserve and transmit the Dhamma, relying on their knowledge to support lay practitioners. This underscores the importance of both spiritual discipline and scholarly knowledge within the Buddhist community.
4. **Enlightenment Factors**: Achieving Arahantship, a high spiritual state, requires the practice of enlightenment factors, including knowledge. The cultivation of wisdom and insight is described as essential for understanding the nature of phenomena and the Dhamma, implying a role for knowledge in spiritual growth.
In conclusion, while the need for formal scholarship may vary among Buddhists, knowledge and understanding are undeniably crucial for both monastics and laypeople. They facilitate the overcoming of ignorance, guide ethical decisions, and are essential for achieving liberation. Thus, knowledge is not just beneficial but necessary for all Buddhists in their journey toward enlightenment.
</answer>
<reference>
n0006: N0006_001-01, N0006_001-04, N0006_001-05, N0006_001-06, N0006_002-01, N0006_002-02, N0006_002-03, N0006_003-01, N0006_003-02, N0006_003-03, N0006_004-01, N0006_004-03, N0006_005-01, N0006_006-01, N0006_006-02, N0006_007-01, N0006_007-02, N0006_008-01, N0006_009-01, N0006_010-01, N0006_011-01, N0006_011-02, N0006_012-01, N0006_012-02, N0006_012-03, N0006_012-04, N0006_012-05, N0006_012-06, N0006_012-07, N0006_012-09, N0006_014-02, N0006_015-01, N0006_015-02, N0006_016-01, N0006_017-03, N0006_018-02, N0006_019-01, N0006_019-02, N0006_020-01, N0006_021-01, N0006_022-02, N0006_022-03, N0006_022-05, N0006_022-06, N0006_022-08, N0006_022-12, N0006_022-13, N0006_023-01, N0006_023-03, N0006_024-02, N0006_025-01, N0006_026-01, N0006_031-01, N0006_035-01, N0006_035-03, N0006_035-07, N0006_035-08, N0006_035-10, N0006_035-11, N0006_035-13, N0006_035-14, N0006_035-19, N0006_036-01, N0006_036-02, N0006_038-01, N0006_039-01, N0006_040-01, N0006_041-01, N0006_042-01, N0006_043-01, N0006_043-02, N0006_044-01, N0006_045-02, N0006_045-04, N0006_045-06, N0006_045-08, N0006_046-01, N0006_046-02, N0006_046-03, N0006_046-04, N0006_046-05, N0006_046-06, N0006_046-07, N0006_046-09, N0006_046-13, N0006_046-14, N0006_047-01, N0006_047-02, N0006_047-04, N0006_047-05, N0006_047-06, N0006_047-07, N0006_048-01, N0006_048-02, N0006_048-05, N0006_048-06, N0006_048-07, N0006_048-08, N0006_048-12, N0006_048-13, N0006_048-14, N0006_048-15, N0006_048-17, N0006_049-01, N0006_049-02, N0006_049-04, N0006_050-04, N0006_050-05, N0006_050-06, N0006_051-01, N0006_051-02, N0006_051-04, N0006_051-05, N0006_051-06, N0006_051-08, N0006_052-02, N0006_053-01, N0006_054-01, N0006_054-02, N0006_055-01, N0006_055-02, N0006_055-03, N0006_055-04, N0006_055-05, N0006_055-06, N0006_056-01, N0006_056-04, N0006_056-05
</reference>
```

<h4>Basic RAG query</h4>

```
python query.py -p my_graphrag/vector_db_n0006_20250213/ -q "Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?" -o 4
```

```
<question>
Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?
</question>
<answer>
Buddhists indeed value knowledge and understanding as integral components of their practice, though the emphasis is more on application and internal development rather than formal scholarship. Here's a structured overview:
1. **Importance of Knowledge and Understanding**:
 - Knowledge of the Dhamma, including the nature of existence, aging, and death, is crucial for spiritual progress. Understanding these concepts, often gained through study and seeking teachers, is essential for practitioners.
2. **Faculties and Stream-Entry Factors**:
 - The four factors of stream-entry, such as unwavering confidence in the Dhamma, highlight the necessity of deep knowledge and wisdom. Intellectual engagement with the teachings is emphasized for spiritual growth.
3. **The Role of Wisdom**:
 - Wisdom, as part of the Noble Eightfold Path, is vital. Right Understanding is a key factor, requiring comprehension of the nature of things. While not confined to formal study, it necessitates a profound understanding for transformative insights.
4. **Practical Application Over Formal Study**:
 - Although knowledge is important, the focus is on lived practices like meditation and ethical conduct. The text underscores the importance of internal development and practical application rather than mere academic knowledge.
5. **Enlightenment Factors**:
 - The seven enlightenment factors, including wisdom, stress the need for insight and understanding. These are achieved through a combination of study, reflection, and meditative practices.
In conclusion, while Buddhists don't require formal scholarly knowledge, they do need a deep, intellectual engagement with Buddhist teachings, fostered through study, reflection, and seeking guidance, which are integral to their spiritual journey.
</answer>
<reference>
n0006: N0006_012-01, N0006_012-08, N0006_012-09, N0006_013-01, N0006_015-02, N0006_035-14, N0006_043-01, N0006_045-06, N0006_046-01, N0006_048-01, N0006_048-06, N0006_051-03, N0006_055-04, N0006_055-05, N0006_055-06, N0006_056-04
</reference>
```
