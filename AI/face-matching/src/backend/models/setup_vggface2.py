#!/usr/bin/env python3
"""
Quick setup script for VGGFace2 model
"""
import os
import requests
from pathlib import Path

def create_model_info():
    """Create model info and download instructions"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    info_file = models_dir / "download_instructions.md"

    content = """# VGGFace2 Model Download Instructions

## Option 1: VGGFace2 Pre-trained Weights (Recommended)

### From Oxford VGG Group:
1. Visit: https://www.robots.ox.ac.uk/~albanie/pytorch-models.html
2. Download: `resnet50_ft_weight.pkl` (VGGFace2 ResNet-50)
3. Place in `models/` directory

### From GitHub Releases:
```bash
# Download VGGFace2 ResNet50 weights
wget https://github.com/ox-vgg/vgg_face2/releases/download/v1.0/resnet50_ft_weight.pkl -P models/

# Alternative: VGG Face weights
wget https://www.robots.ox.ac.uk/~albanie/models/pytorch-mcn/vgg_face_dag.pth -P models/
```

## Option 2: InsightFace Models (Alternative)

```bash
# Download InsightFace Buffalo_L model
mkdir -p models/buffalo_l
cd models/buffalo_l
wget https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip
unzip buffalo_l.zip
cd ../..
```

## Option 3: Face Recognition Library (Easiest)

```bash
pip install face-recognition
# No additional downloads needed
```

## Option 4: Mock Model (For Testing)

No downloads needed - the system will automatically use a mock model for testing.

## Current Model Detection Priority:

1. VGGFace2 PyTorch weights (if `models/vggface2_weights.pth` exists)
2. VGGFace2 pickle weights (if `models/resnet50_ft_weight.pkl` exists)
3. VGG Face weights (if `models/vgg_face_dag.pth` exists)
4. InsightFace Buffalo_L (if `models/buffalo_l/` exists)
5. face_recognition library (if installed)
6. OpenCV face recognition (basic)
7. Mock model (for testing)

## Testing Model Loading:

```bash
python -c "from models.vggface2 import VGGFace2Model; import asyncio; model = VGGFace2Model(); asyncio.run(model.load_model()); print('Model loaded:', model.is_loaded())"
```
"""

    with open(info_file, "w") as f:
        f.write(content)

    print(f"Model download instructions created: {info_file}")

def check_existing_models():
    """Check what models are already available"""
    models_dir = Path("models")

    print("🔍 Checking for existing models...")

    model_files = [
        ("vggface2_weights.pth", "VGGFace2 PyTorch weights"),
        ("resnet50_ft_weight.pkl", "VGGFace2 ResNet50 weights"),
        ("vgg_face_dag.pth", "VGG Face weights"),
        ("buffalo_l/", "InsightFace Buffalo_L")
    ]

    found_models = []

    for filename, description in model_files:
        filepath = models_dir / filename
        if filepath.exists():
            found_models.append((filename, description))
            print(f"Found: {description}")
        else:
            print(f"Missing: {description}")

    # Check for face_recognition
    try:
        import face_recognition
        print("Found: face_recognition library")
        found_models.append(("face_recognition", "face_recognition library"))
    except ImportError:
        print("Missing: face_recognition library")

    if found_models:
        print(f"\nFound {len(found_models)} available model(s)")
        return True
    else:
        print("\nNo models found. The system will use mock model for testing.")
        return False

def download_simple_weights():
    """Download simple VGGFace weights for testing"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    print("Attempting to download basic VGGFace weights...")

    # Try to download VGG Face weights (smaller, more reliable)
    url = "https://www.robots.ox.ac.uk/~albanie/models/pytorch-mcn/vgg_face_dag.pth"
    destination = models_dir / "vgg_face_dag.pth"

    try:
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            print(f"Downloading from: {url}")

            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Downloaded: {destination}")
            return True
        else:
            print(f"URL not accessible: {response.status_code}")
            return False

    except Exception as e:
        print(f"Download failed: {e}")
        return False

if __name__ == "__main__":
    print("VGGFace2 Setup")
    print("=" * 30)

    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    # Create download instructions
    create_model_info()

    # Check existing models
    has_models = check_existing_models()

    if not has_models:
        print("\nWould you like to:")
        print("1. Try automatic download (VGG Face weights)")
        print("2. Install face_recognition library")
        print("3. Continue with mock model (for testing)")

        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            if download_simple_weights():
                print("Model downloaded successfully!")
            else:
                print("Download failed. Please try manual download.")
        elif choice == "2":
            print("Installing face_recognition...")
            os.system("pip install face-recognition")
        else:
            print("Continuing with mock model...")

    print("\nNext steps:")
    print("1. Check models/download_instructions.md for manual download options")
    print("2. Test model loading: python test_model.py")
    print("3. Start the API: python main.py")

    # Create a simple test script
    test_script = """#!/usr/bin/env python3
import asyncio
from models.vggface2 import VGGFace2Model

async def test_model():
    print("Testing VGGFace2 model...")
    model = VGGFace2Model(model_type="auto")
    await model.load_model()
    print(f"Model loaded: {model.is_loaded()}")
    print(f"Model type: {model.model_type}")
    print(f"Embedding size: {model.embedding_size}")

if __name__ == "__main__":
    asyncio.run(test_model())
"""

    with open("test_model.py", "w") as f:
        f.write(test_script)

    print("4. Model test script created: test_model.py")
    print("\nSetup completed!")
