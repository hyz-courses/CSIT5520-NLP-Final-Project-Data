import os
import time
import json
from openai import OpenAI
from dotenv import load_dotenv
from files import QuestionGenerator

load_dotenv("resources/.env")

FILE_PATH = "resources/question/milvus_storage.jsonl"
DESTINATION_PATH = "resources/question/milvus_questions.jsonl"
LAST_VIEWED = "resources/question/.last_viewed"


if __name__ == "__main__":
    # ask_question_on_all_texts()
    # ask_question_on_one_text(prompt_cn.format(text="小明有3元钱，他吃东西花掉了2元，请问他还剩几元？"))

    jsonl_reader = QuestionGenerator(FILE_PATH, DESTINATION_PATH, LAST_VIEWED)
    jsonl_reader.process_all()