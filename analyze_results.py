import json
from dotenv import load_dotenv
from files import ResultAnalyzer

load_dotenv("resources/.env")

FILE_PATH = "resources/question/milvus_summarized.jsonl"
DESTINATION_PATH = "resources/question/milvus_analyzed.jsonl"
LAST_ANALYZED = "resources/question/.last_analyzed"


if __name__ == "__main__":
    result_analyzer = ResultAnalyzer(FILE_PATH, DESTINATION_PATH, LAST_ANALYZED)
    result_analyzer.process_all()

    ndcg_mean_values_cn = [0.0, 0.0, 0.0, 0.0]
    ndcg_mean_values_en = [0.0, 0.0, 0.0, 0.0]

    with open(DESTINATION_PATH, "r") as f:
        i = 0        
        for line in f:
            i += 1
            data = json.loads(line)
            ndcg_values_cn = data["ndcg_values_cn"]
            ndcg_values_en = data["ndcg_values_en"]

            if len(ndcg_values_cn) == 0 or len(ndcg_values_en) == 0:
                continue

            for idx in range(4):
                ndcg_mean_values_cn[idx] += ndcg_values_cn[idx]
                ndcg_mean_values_en[idx] += ndcg_values_en[idx]

        if i > 0:
            ndcg_mean_values_cn = [x / i for x in ndcg_mean_values_cn]
            ndcg_mean_values_en = [x / i for x in ndcg_mean_values_en]

    with open("resources/question/ndcg_mean.json", "w") as f:
        json.dump({"ndcg_mean_values_cn": ndcg_mean_values_cn, "ndcg_mean_values_en": ndcg_mean_values_en}, f, indent=4)

    print("Mean NDCG (Chinese):", ndcg_mean_values_cn)
    print("Mean NDCG (English):", ndcg_mean_values_en)

            