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

from files import MarkdownParser, JsonUploader

load_dotenv("./resources/.env")

if __name__ == "__main__":
    file_processor = MarkdownParser(
        source_dir="resources/markdowns",
        des_dir="resources/jsons")
    file_processor.process_all()

    # Process the generated JSON files
    uploader = JsonUploader(source_dir="resources/jsons", des_dir="resources/uploaded")
    uploader.process_all()
