import os
import time
import re
import json
import copy
from typing import Dict, List
import requests
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from openai import OpenAI

from tqdm import tqdm
from dotenv import load_dotenv


load_dotenv("./resources/.env")


class FSDirectoryProcessor(ABC):
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


class FileLineProcessor(ABC):
    def __init__(self, source_file: str, des_file: str, count_file: str):
        self.source_file = source_file
        self.count_file = count_file
        self.des_file = des_file

    @abstractmethod
    def process_one(self, line: str, line_num: int):
        ...

    def process_all(self):
        with open(self.count_file, "r") as last_viewed_f:
            try:
                last_viewed_num = int(last_viewed_f.read().strip())
                print(f"Last stopped at: {last_viewed_num}")
            except ValueError:
                last_viewed_num = 0

        with open(self.des_file, "w", encoding="utf-8") as des_f:
            with open(self.count_file, "w") as last_viewed_f:
                with open(self.source_file, "r") as f:
                    i = 0
                    for line in f:
                        if i <= last_viewed_num:
                            i += 1
                            continue

                        last_viewed_f.seek(0)
                        last_viewed_f.truncate()
                        last_viewed_f.write(f"{i}\n")
                        last_viewed_f.flush()

                        res = self.process_one(line, i)
                        des_f.write(json.dumps(res, ensure_ascii=False) + "\n")
                        print(f"{i}: Written line. ")

                        if i % 5 == 0:
                            des_f.flush()
                            print(f"Flushing into file...")
                            time.sleep(0.25)

                        i += 1

                    f.close()


class MarkdownParser(FSDirectoryProcessor):

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


class JsonUploader(FSDirectoryProcessor):

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


class QuestionGenerator(FileLineProcessor):

    def __init__(self, source_dir: str, des_dir: str, last_viewd: str):
        super().__init__(source_dir, des_dir, last_viewd)
        self.ALICLOUD_BASE_URL = os.getenv("ALICLOUD_BASE_URL")

        self.QWEN_QUESTION_GENERATION_MODEL = os.getenv(
            "QWEN_QUESTION_GENERATION_MODEL")
        self.QWEN_API_KEY = os.getenv("QWEN_API_KEY")
        self.ALICLOUD_BASE_URL = os.getenv("ALICLOUD_BASE_URL")

        self.openai_client = OpenAI(
            api_key=self.QWEN_API_KEY, base_url=self.ALICLOUD_BASE_URL)

        self.prompt_cn = "请根据以下文本，生成10个问题。每个问题应尽量口语化，不应超过20字。不要提供额外的文字内容。文本如下：\n<sample>\n{text}\n</sample>\n /nothink"
        self.prompt_en = "Please generate 10 questions based on the following text in English. Each question should be phrased in a oral speaking style, and should contain no more than 30 words. Do not provide any extra texts (such as greetings, etc.). Context is as follows:\n<sample>\n{text}\n</sample>\n /nothink"

    def ask_question_on_one_text(self, text: str) -> str:
        result = self.openai_client.chat.completions.create(
            model=str(self.QWEN_QUESTION_GENERATION_MODEL),
            messages=[
                {"role": "user", "content": text}
            ],
            max_tokens=512,
            temperature=0.7,
        )
        questions = result.choices[0].message.content
        if not questions:
            return "None"
        return questions

    def process_one(self, line: str, line_num: int):
        data = json.loads(line)
        id: int = data["id"]
        text: str = data["text"]

        record = {
            "id": id,
            "questions_cn": None,
            "questions_en": None
        }

        if len(text) < 15:
            return record

        record["questions_cn"] = self.ask_question_on_one_text(
            self.prompt_cn.format(text=text))
        record["questions_en"] = self.ask_question_on_one_text(
            self.prompt_en.format(text=text))

        return record


class QuestionAsker(FileLineProcessor):

    def __init__(self, source_dir: str, des_dir: str, last_viewd: str):
        super().__init__(source_dir, des_dir, last_viewd)
        self.DIFY_API_KEY = str(os.getenv("DIFY_API_KEY"))
        self.DIFY_API_URL = str(os.getenv("DIFY_API_URL"))
        self.HEADERS = {
            "Authorization": f"Bearer {self.DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        self.available_languages = ["cn", "en"]

    def ask_one_batch_questions(self, questions: List[str], line_num: int):
        received_chunks_by_question = []
        similarities_by_question = []
        for question in tqdm(questions, desc=f"Line {line_num}"):
            question = question.strip()
            data = {
                "inputs": {"question": question},
                "response_mode": "blocking",
                "user": "abc-123"
            }

            _response = requests.post(
                url=self.DIFY_API_URL, headers=self.HEADERS, json=data)
            response = json.loads(_response.content)

            # {distance: float, id: int}
            result_list: List[Dict[str, float | int]
                              ] = eval(response["data"]["outputs"]["id"])

            retrieved_chunks = [result["id"] for result in result_list]
            similarities = [result["distance"] for result in result_list]

            received_chunks_by_question.append(retrieved_chunks)
            similarities_by_question.append(similarities)
        return received_chunks_by_question, similarities_by_question

    def process_one(self, line: str, line_num: int) -> dict:

        data = json.loads(line)
        target_id: int = data["id"]

        record = ({
            "target_id": target_id,
        } | {f"chunks_by_question_{lang}": [] for lang in self.available_languages} |
            {f"similarities_by_question_{lang}": [] for lang in self.available_languages})

        for lang in self.available_languages:
            question_key = f"questions_{lang}"

            if question_key not in data or data[question_key] is None:
                continue

            questions: str = data[f"questions_{lang}"]
            question_list: List[str] = questions.split("\n")

            chunks_by_question, sim_by_question = self.ask_one_batch_questions(
                question_list, line_num=line_num)

            record[f"chunks_by_question_{lang}"] = chunks_by_question
            record[f"similarities_by_question_{lang}"] = sim_by_question

        return record


class ResultSummarizer(FileLineProcessor):
    def __init__(self, source_dir: str, des_dir: str, last_viewd: str):
        super().__init__(source_dir, des_dir, last_viewd)

        self.map = {}
        self.available_langugages = ["cn", "en"]

    def process_one(self, line: str, line_num: int) -> dict:
        data = json.loads(line)
        target_id: int = data["target_id"]

        if target_id not in self.map:
            self.map[target_id] = {
                "hit_at": [],
                "total_num": []
            }

        for lang in self.available_langugages:
            chunks_by_question_key = f"chunks_by_question_{lang}"
            similarities_by_question_key = f"similarities_by_question_{lang}"

            if chunks_by_question_key not in data or data[chunks_by_question_key] is None or not isinstance(data[chunks_by_question_key], list):
                continue

            for chunks, similarities in zip(data[chunks_by_question_key], data[similarities_by_question_key]):
                chunks: List[int]
                similarities: List[float]

                hit_at = chunks.index(target_id) if target_id in chunks else -1
                self.map[target_id]["hit_at"].append(hit_at)
                self.map[target_id]["total_num"].append(len(chunks))

        return {}
