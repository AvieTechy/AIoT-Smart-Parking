import os
import requests
import json
import csv
from glob import glob


# === CONFIG ===
IMAGE_DIR = "./dataset/test/images"
API_URL = "http://localhost:8080/v1/plate-reader/"
CSV_OUTPUT = "inference_results.csv"
JSON_OUTPUT = "inference_results.json"

def call_alpr(image_path):
    with open(image_path, 'rb') as img:
        response = requests.post(API_URL, files={'upload': img})
        return response.json()

def main():
    image_paths = sorted(glob(os.path.join(IMAGE_DIR, "*.*")))
    print(f"Found {len(image_paths)} images in: {IMAGE_DIR}")

    all_results = []

    with open(CSV_OUTPUT, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["filename", "predicted_plate", "score", "num_candidates"])

        for img_path in image_paths:
            filename = os.path.basename(img_path)
            try:
                result = call_alpr(img_path)
                all_results.append({
                    "filename": filename,
                    "result": result
                })

                # Lấy plate đầu tiên (nếu có)
                if result.get("results"):
                    plate = result["results"][0]["plate"]
                    score = result["results"][0]["score"]
                    num_cand = len(result["results"][0]["candidates"])
                else:
                    plate = ""
                    score = 0
                    num_cand = 0

                csv_writer.writerow([filename, plate, score, num_cand])
                print(f"[✓] {filename}: {plate} (score: {score})")
            except Exception as e:
                print(f"[X] Failed to process {filename}: {e}")
                csv_writer.writerow([filename, "", 0, 0])

    # Save full JSON for debugging or inspection
    with open(JSON_OUTPUT, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅ Inference completed.")
    print(f"📄 Results saved to: {CSV_OUTPUT}")
    print(f"📄 Raw JSON saved to: {JSON_OUTPUT}")

if __name__ == "__main__":
    main()
