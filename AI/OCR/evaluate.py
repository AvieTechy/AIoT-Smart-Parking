import json, csv, re, unicodedata, os

# -------- Config --------
RESULTS_FILE = "results/results.json"      # Plate Recognizer results
LABELS_FILE  = "dataset/test/labels.csv"   # CSV: filename, plate
OUTPUT_DIR   = "results"
# ------------------------

# Normalization helper
CONFUSION = {"O":"0","I":"1","S":"5","B":"8"}
def normalize_plate(s: str) -> str:
    if not s: return ""
    s = unicodedata.normalize("NFC", s).upper().strip()
    s = "".join(CONFUSION.get(ch, ch) for ch in s)
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s

# Load predictions
def load_predictions(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    preds = {}
    for item in data:
        fn = item.get("filename")
        res = (item.get("result") or {}).get("results") or []
        if res:
            top = res[0]
            preds[fn] = {"plate": top.get("plate",""), "confidence": float(top.get("score", 0.0))}
        else:
            preds[fn] = {"plate": "", "confidence": 0.0}
    return preds

# Load ground truth
def load_labels(path: str) -> dict:
    labels = {}
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            labels[row["filename"]] = row["plate"].strip()
    return labels

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    preds  = load_predictions(RESULTS_FILE)
    labels = load_labels(LABELS_FILE)

    total = correct = detected = 0
    logs = []

    for fn, gt in labels.items():
        if fn not in preds:
            continue
        total += 1
        pred_txt = preds[fn]["plate"]
        conf     = preds[fn]["confidence"]
        if pred_txt:
            detected += 1

        ok = normalize_plate(pred_txt) == normalize_plate(gt)
        if ok: correct += 1
        type_ = "correct" if ok else "wrong" if pred_txt else "miss"

        logs.append({
            "filename": fn,
            "true_plate": gt,
            "pred_plate": pred_txt,
            "confidence": conf,
            "type": type_
        })

    acc = correct / total if total else 0.0
    det = detected / total if total else 0.0

    # Print summary
    print("=== OCR Evaluation Summary ===")
    print(f"Total samples     : {total}")
    print(f"Detected plates   : {detected}")
    print(f"Accuracy (exact)  : {acc:.3f} ({acc*100:.1f}%)")
    print(f"Detection rate    : {det:.3f} ({det*100:.1f}%)")

    # Save summary
    summary_path = os.path.join(OUTPUT_DIR, "evaluation_results.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("=== OCR Evaluation Summary ===\n")
        f.write(f"Dataset size      : {total}\n")
        f.write(f"Detected plates   : {detected}\n")
        f.write(f"Accuracy (exact)  : {acc:.3f} ({acc*100:.1f}%)\n")
        f.write(f"Detection rate    : {det:.3f} ({det*100:.1f}%)\n")
    print(f"Saved summary to {summary_path}")

    # Save logs
    logs_path = os.path.join(OUTPUT_DIR, "evaluation_logs.csv")
    with open(logs_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename","true_plate","pred_plate","confidence","type"])
        writer.writeheader()
        writer.writerows(logs)
    print(f"Saved logs to {logs_path}")

if __name__ == "__main__":
    main()
