import os
import time
import re
import json
import copy
import requests
from datetime import datetime, timezone
from pathlib import Path
from abc import ABC, abstractmethod

from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv("./resources/.env")


class FileProcessor(ABC):
    def __init__(self, file_ext: str, source_dir: str, des_dir: str):
        if not file_ext.startswith("."):
            raise ValueError("File extension should start with a dot.")
        self.file_ext = file_ext
        self.source_dir = source_dir
        self.des_dir = des_dir

    @abstractmethod
    def process_one(self, file_name: str):
        ...

    def process_all(self):
        for file_name in os.listdir(self.source_dir):
            if file_name.endswith(self.file_ext):
                self.process_one(Path(file_name).stem)


class MarkdownParser(FileProcessor):

    def __init__(self, source_dir: str, des_dir: str):
        super().__init__(".md", source_dir, des_dir)

    def process_one(self, file_name: str):
        source_file_path = os.path.join(
            self.source_dir, f"{file_name}{self.file_ext}")
        des_file_path = os.path.join(self.des_dir, f"{file_name}.json")

        with open(source_file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        default_buffer = {
            "original_filename": f"{file_name}{self.file_ext}",
            "title1": None,
            "title2": None,
            "text": "",
            "upload_time": datetime.now().isoformat()
        }

        outputs = []
        buffer = copy.deepcopy(default_buffer)
        text_buffer = []

        def save_buffer():
            nonlocal text_buffer
            if not text_buffer:
                return
            buffer["text"] = "\n".join(text_buffer)
            outputs.append(copy.deepcopy(buffer))
            text_buffer = []

        for line in lines:
            if re.match(r"^#\s[^#]", line):
                # First layer title
                save_buffer()
                buffer["title1"] = line[1:].strip()
                buffer["title2"] = None
            elif re.match(r"^##\s[^#]", line):
                # Second layer title
                save_buffer()
                buffer["title2"] = line[2:].strip()
            else:
                # Regular text
                text_buffer.append(line)

        save_buffer()

        with open(des_file_path, "w", encoding="utf-8") as f:
            json.dump(outputs, f, ensure_ascii=False, indent=4)


class JsonUploader(FileProcessor):

    def __init__(self, source_dir: str, des_dir: str):
        super().__init__(".json", source_dir, des_dir)

    def process_one(self, file_name: str):
        source_file_path = os.path.join(
            self.source_dir, f"{file_name}{self.file_ext}")
        
        with open(source_file_path, "r", encoding="utf-8") as f:
            chunk_list = json.load(f)
            f.close()

        for sub_chunklist in tqdm(
            [chunk_list[i:i+10] for i in range(0, len(chunk_list), 10)],
                desc=f"File: {file_name}{self.file_ext}"):
            # print(sub_chunklist)
            response = requests.post(
                url="https://api.docsearch.love/chunk",
                json={
                    "chunks": sub_chunklist
                },
                headers={
                    "X-API-Key": os.getenv("DOCSEARCH_API_KEY")
                })
            tqdm.write(response.text)
            tqdm.write("Cooldown 2.5 secs...")
            time.sleep(2.5)

if __name__ == "__main__":
    file_processor = MarkdownParser(
        source_dir="resources/markdowns",
        des_dir="resources/jsons")
    file_processor.process_all()

    # Process the generated JSON files
    uploader = JsonUploader(source_dir="resources/jsons", des_dir="resources/uploaded")
    uploader.process_all()
