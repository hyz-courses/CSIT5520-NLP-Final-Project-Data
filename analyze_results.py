import json
from typing import List
from dotenv import load_dotenv
import pandas as pd
from files import ResultAnalyzer

load_dotenv("resources/.env")

FILE_PATH = "resources/question/milvus_summarized.jsonl"
DESTINATION_PATH = "resources/question/milvus_analyzed.jsonl"
LAST_ANALYZED = "resources/question/.last_analyzed"


if __name__ == "__main__":
    result_analyzer = ResultAnalyzer(FILE_PATH, DESTINATION_PATH, LAST_ANALYZED)
    result_analyzer.process_all()

    ndcg_mean_values_cn = pd.DataFrame([0, 0, 0, 0])
    ndcg_mean_values_en = pd.DataFrame([0, 0, 0, 0])

    with open(DESTINATION_PATH, "r") as f:
        i = 0        
        for line in f:
            i += 1
            data = json.loads(line)
            ndcg_values_cn: List[float] = data["ndcg_values_cn"]
            ndcg_values_en: List[float] = data["ndcg_values_en"]

            ndcg_mean_values_cn += pd.DataFrame(ndcg_values_cn)
            ndcg_mean_values_en += pd.DataFrame(ndcg_values_en)
        
        ndcg_mean_values_cn = ndcg_mean_values_cn / i
        ndcg_mean_values_en = ndcg_mean_values_en / i

    # 转换为列表
    ndcg_mean_values_cn_list = ndcg_mean_values_cn.values.flatten().tolist()
    ndcg_mean_values_en_list = ndcg_mean_values_en.values.flatten().tolist()
    
    print("Mean NDCG (Chinese):", ndcg_mean_values_cn_list)
    print("Mean NDCG (English):", ndcg_mean_values_en_list)


            