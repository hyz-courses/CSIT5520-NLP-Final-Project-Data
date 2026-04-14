# CSIT5520 NLP Final Project Data Proceessing

- HUANG Yanzhen
- LI Weijie
- LI Kaiwen

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

## Parse and Upload

Run:

```bash
python parse.py
```

This will pares all the files in the `/makrdowns` directory and upload all the output `.json` files.

## Regression Test

**Generate Questions**

Run:

```bash
python -m generate_questions
```

**Ask Questions**

Run:

```bash
python -m ask_questions
```

**Evaluate**

Run:

```bash
python -m summarize
```