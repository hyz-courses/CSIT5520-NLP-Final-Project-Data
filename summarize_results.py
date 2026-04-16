from dotenv import load_dotenv
from files import ResultSummarizer

load_dotenv("resources/.env")

FILE_PATH = "resources/question/milvus_answers.jsonl"
DESTINATION_PATH = "resources/question/milvus_summarized.jsonl"
LAST_SUMMARIZED = "resources/question/.last_summarized"

if __name__ == "__main__":
    result_summarizer = ResultSummarizer(FILE_PATH, DESTINATION_PATH, LAST_SUMMARIZED)
    result_summarizer.process_all()