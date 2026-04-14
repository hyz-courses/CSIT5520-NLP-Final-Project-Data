from dotenv import load_dotenv
from files import QuestionGenerator

load_dotenv("resources/.env")

FILE_PATH = "resources/question/milvus_storage.jsonl"
DESTINATION_PATH = "resources/question/milvus_questions.jsonl"
LAST_VIEWED = "resources/question/.last_viewed"


if __name__ == "__main__":
    jsonl_reader = QuestionGenerator(FILE_PATH, DESTINATION_PATH, LAST_VIEWED)
    jsonl_reader.process_all()