from dotenv import load_dotenv
from files import MarkdownParser, JsonUploader

load_dotenv("./resources/.env")

if __name__ == "__main__":
    # file_processor = MarkdownParser(
    #     source_dir="resources/markdowns",
    #     des_dir="resources/jsons")
    # file_processor.process_all()

    # Process the generated JSON files
    uploader = JsonUploader(
        source_dir="resources/jsons", 
        des_dir="resources/uploaded")
    uploader.process_all()
