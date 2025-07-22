import csv
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def convert_bbox_to_yolo(img_w, img_h, xmin, ymin, xmax, ymax):
    cx = (xmin + xmax) / 2 / img_w
    cy = (ymin + ymax) / 2 / img_h
    w = (xmax - xmin) / img_w
    h = (ymax - ymin) / img_h
    return [cx, cy, w, h]

def get_test_image_names(img_dir):
    return set(f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')))

def build_image_mapping(img_dir):
    """
    Build a mapping from base filename (e.g., img_000.jpg) to actual test image filename (e.g., img_000_jpg.rf.<hash>.jpg)
    """
    mapping = {}
    for fname in os.listdir(img_dir):
        if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            if '.rf.' in fname:
                base = fname.split('_jpg.rf')[0] + '.jpg'
            else:
                base = fname
            mapping[base] = fname
    return mapping

def normalize_inference_csv(
    csv_path="./inference.csv",
    output_path="./inference_yolo.json",
    img_dir="./dataset/test/images"
):
    image_mapping = build_image_mapping(img_dir)
    result = {}

    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            base_fname = row["filename"]
            if base_fname not in image_mapping:
                continue
            fname = image_mapping[base_fname]
            detected = int(row["detected"])
            bboxes = row["bboxes"].strip()

            img_path = os.path.join(img_dir, fname)
            try:
                with Image.open(img_path) as im:
                    img_w, img_h = im.size
            except Exception:
                img_w, img_h = 1, 1

            yolo_bboxes = []
            if detected == 1 and bboxes:
                coords = list(map(int, bboxes.split(",")))
                for i in range(0, len(coords), 4):
                    if i + 4 <= len(coords):
                        xmin, ymin, xmax, ymax = coords[i:i+4]
                        yolo_bboxes.append(convert_bbox_to_yolo(img_w, img_h, xmin, ymin, xmax, ymax))

            result[fname] = yolo_bboxes

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"✅ Đã chuẩn hóa bbox cho {len(result)} ảnh test và lưu vào: {output_path}")

def evaluate_detection(
    csv_path="./inference.csv",
    label_dir="./dataset/test/labels",
    img_dir="./dataset/test/images"
):
    image_mapping = build_image_mapping(img_dir)
    TP, FP, FN, TN = 0, 0, 0, 0

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            base_fname = row['filename']
            if base_fname not in image_mapping:
                continue
            fname = image_mapping[base_fname]
            detected = int(row['detected'])

            label_prefix = fname.rsplit('.', 1)[0]
            label_files = [f for f in os.listdir(label_dir) if f.startswith(label_prefix)]

            has_gt = False
            for lf in label_files:
                label_path = os.path.join(label_dir, lf)
                with open(label_path, 'r') as f:
                    if f.read().strip():
                        has_gt = True
                        break

            if detected == 1 and has_gt:
                TP += 1
            elif detected == 1 and not has_gt:
                FP += 1
            elif detected == 0 and has_gt:
                FN += 1
            elif detected == 0 and not has_gt:
                TN += 1

    precision = TP / (TP + FP) if (TP + FP) else 0.0
    recall = TP / (TP + FN) if (TP + FN) else 0.0

    print(f"🎯 Precision: {precision:.4f}")
    print(f"🎯 Recall:    {recall:.4f}")
    print(f"TP: {TP}, FP: {FP}, FN: {FN}, TN: {TN}")
    return precision, recall, TP, FP, FN, TN

def plot_confusion_matrix(tp, fp, fn, tn, labels=["Positive", "Negative"]):
    cm = np.array([[tp, fp],
                   [fn, tn]])

    fig, ax = plt.subplots()
    im = ax.imshow(cm, cmap="Blues")

    ax.set_xticks(np.arange(2))
    ax.set_xticklabels(labels)
    ax.set_yticks(np.arange(2))
    ax.set_yticklabels(labels)
    ax.set_xlabel("Ground Truth")
    ax.set_ylabel("Prediction")

    # Hiển thị số trong từng ô
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]}", ha="center", va="center", color="black", fontsize=12)

    plt.title("Confusion Matrix")
    plt.colorbar(im)
    plt.tight_layout()
    plt.show()

    # Save confusion matrix as image
    fig.savefig("confusion_matrix.png")


# === MAIN EXECUTION ===
if __name__ == "__main__":
    csv_path = "./inference.csv"
    label_dir = "./dataset/test/labels"
    img_dir = "./dataset/test/images"
    output_json = "./inference_yolo.json"

    normalize_inference_csv(csv_path, output_json, img_dir)
    precision, recall, TP, FP, FN, TN = evaluate_detection(csv_path, label_dir, img_dir)
    plot_confusion_matrix(TP, FP, FN, TN, labels=["Positive", "Negative"])
