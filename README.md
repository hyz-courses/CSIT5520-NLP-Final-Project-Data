# CSIT5520 NLP Final Project Data Proceessing

- HUANG Yanzhen
- LI Weijie
- LI Kaiwen

## Introduction

We built a RAG pipeline, encorporating FastAPI as backend server, Dify as pipeline backbone and Milvus as vector database.

This repository is used for data processing and demo. The repository of the FastAPI server can be found at:

https://github.com/hyz-courses/CSIT5520-NLP-Final-Project

### Resources

**Models**

| Usage | Variant | Remarks |
|-------|---------|---------|
| Text Embedding Model | [Qwen text-embedding-v4](https://huggingface.co/Qwen/Qwen3-Embedding-4B) | d=1024 |
| Question Generation Model | [Qwen3.5-plus](https://huggingface.co/Qwen/Qwen-plus) | |
| Answering Model | [Qwen3.5-plus](https://huggingface.co/Qwen/Qwen-plus) |

**Data**

We obtained data from [MSSS WeChat Public Account](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAwNjAxNTYxNw==&action=getalbum&album_id=3879314961398415378&scene=126&sessionid=1776356381749#wechat_redirect), most of which are in Chinese (Simplified). Data are processed by us to fit the pipeline (see [Parse and Upload](#parse-and-upload)).

All the related data are stored in the [demo](demo/) folder. It is a static snapshot of the [resources](resources/) folder for your quick reference. 

| Subfolder | Description |
|-|-|
| [demo/markdowns](demo/markdowns) | Source article data in `.md` format. | 
| [demo/jsons](demo/jsons) | Chunk-format of source article data ready to upload. |
| [demo/pipelines](demo/pipelines/) | `.yaml` format snapshot of two pipelines: The general question answering pipeline and the retrieval test pipeline. |
| [demo/question](demo/question) | All the related files during [retrieval test](#retrieval-test). |


### Retrieval Test Result

We performed [retrieval test](#retrieval-test) on our milvus data. The **final** results are follows.

| Question Language| NDCG@1 | NDCG@5 | NDCG@10 | NDCG@20 |
| --- | --- | --- | --- | --- |
| Chinese | 0.46565 | 0.60494 | 0.63176 | 0.64865 |
| English | 0.55206 | 0.68110 | 0.70284 | 0.71637 |


## Setup

Please add a `.env` file into the `/resources` directory and add a `DOCSEARCH_API_KEY` variable the author give to you.

```ini
# resources/.env

# To use LLM apis from Alibaba
ALICLOUD_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY="your-qwen-api-key"
QWEN_QUESTION_GENERATION_MODEL=qwen-plus

# Communicate with Dify
DIFY_API_URL=https://dify.docsearch.love/v1/workflows/run
DIFY_API_KEY="your-dify-api-key"

# To upload chunk to our server
DOCSEARCH_API_KEY="your-docsearch-api-key"
```

Install related packages:

```bash
pip install -r requirements.txt
```

## Quick Start

Run this command to chat with the pipeline.

```bash
streamlit run app.py
```

## Parse and Upload

Run:

```bash
python parse.py
```

This will pares all the files in the `/makrdowns` directory and upload all the output `.json` files.

## Retrieval Test

Data process pipelines:

| Stage | File Name | Remarks |
|------|--------|----------|
| 1 | [milvus_storage.jsonl](demo/question/milvus_storage.jsonl) | Original Milvus Database Storage |
| 2 | [milvus_questions.jsonl](demo/question/milvus_questions.jsonl) | Generated Questions |
| 3 | [milvus_answers.jsonl](demo/question/milvus_answers.jsonl) | Retrieved Answer Chunks |
| 4 | [milvus_summarized.jsonl](demo/question/milvus_summarized.jsonl) | Summarized Answer Hitting |
| 5 | [milvus_analyzed.jsonl](demo/question/milvus_analyzed.jsonl) | NDCG for each question |
| 6 | [ndcg_mean.json](demo/question/ndcg_mean.json) | Final mean NDCG |

**Generate Questions (1 → 2)**

Given each chunk stored in the Milvus database, we generate 10 questions in both Chinese and English.

_Run:_

```bash
python -m generate_questions
```

**Ask Questions (2 → 3)**

For each chunk, we asked the 20 generated questions to the Milvus database, retrieving top 20 answer chunks for each language. Idealy, a chunk's answer chunk should have itself in the first answer, IDCG = 1.

These chunks are uniquely identified by chunk hash instead of chunk ID.

_Run:_

```bash
python -m ask_questions
```

**Evaluate (3 → 4)**

Check for each chunk, for all 20 questions, whether the answer chunk is in the first 20 answer chunks, and exactly at which position it ranks ("hit at").

_Run:_

```bash
python -m summarize_results
```

**Analyze (4 → 5 & 6)**

Finally, calculate NDCG at 1, 5, 10, and 20 for each chunk, and calculate the mean NDCG for all chunks.

_Run:_

```bash
python -m analyze_results
```

