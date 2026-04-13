import os
import json
import requests
from typing import List, Dict
from dotenv import load_dotenv
from files import QuestionAsker

load_dotenv("resources/.env")

FILE_PATH = "resources/question_generation/milvus_questions.jsonl"
DESTINATION_PATH = "resources/question_generation/milvus_answers.jsonl"
LAST_ASKED = "resources/question_generation/.last_asked"

if __name__ == "__main__":
    question_asker = QuestionAsker(FILE_PATH, DESTINATION_PATH, LAST_ASKED)
    question_asker.process_all()