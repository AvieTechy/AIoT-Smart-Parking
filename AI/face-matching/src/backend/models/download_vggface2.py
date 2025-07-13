#!/usr/bin/env python3
"""
Script to download and setup VGGFace2 model weights
"""
import os
import requests
import torch
import gdown
from pathlib import Path
import hashlib

def download_file(url, destination, expected_hash=None):
    """Download file with progress and hash verification"""
    print(f"Downloading {url}")
    print(f"Destination: {destination}")

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    # Download file
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0

    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}%", end='', flush=True)

    print(f"\nDownload completed: {destination}")

    # Verify hash if provided
    if expected_hash:
        file_hash = hashlib.md5(open(destination, 'rb').read()).hexdigest()
        if file_hash != expected_hash:
            print(f"Warning: Hash mismatch. Expected: {expected_hash}, Got: {file_hash}")
        else:
            print("Hash verification passed")

def download_vggface2_weights():
    """Download VGGFace2 model weights"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    print("VGGFace2 Model Download Setup")
    print("=" * 40)

    # VGGFace2 ResNet50 weights from various sources
    model_options = {
        "1": {
            "name": "VGGFace2 ResNet50 (ArcFace)",
            "url": "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip",
            "filename": "buffalo_l.zip",
            "description": "InsightFace Buffalo_L model (includes VGGFace2 trained weights)"
        },
        "2": {
            "name": "VGGFace2 ResNet50 (Original)",
            "url": "https://www.robots.ox.ac.uk/~albanie/models/pytorch-mcn/vgg_face_dag.pth",
            "filename": "vgg_face_dag.pth",
            "description": "Original VGGFace PyTorch weights"
        },
        "3": {
            "name": "Manual Setup",
            "description": "I'll provide manual setup instructions"
        }
    }

    print("Available VGGFace2 models:")
    for key, model in model_options.items():
        print(f"{key}. {model['name']}")
        print(f"   {model['description']}")
        print()

    choice = input("Choose model (1-3): ").strip()

    if choice == "1":
        # Download InsightFace Buffalo_L
        destination = models_dir / model_options[choice]["filename"]
        try:
            download_file(model_options[choice]["url"], str(destination))
            print("InsightFace model downloaded successfully!")
            print("Note: You'll need to extract the zip file and use the .onnx model files")
        except Exception as e:
            print(f"Download failed: {e}")
            print("Please try manual setup or different option")

    elif choice == "2":
        # Download original VGGFace
        destination = models_dir / model_options[choice]["filename"]
        try:
            download_file(model_options[choice]["url"], str(destination))
            print("VGGFace model downloaded successfully!")
        except Exception as e:
            print(f"Download failed: {e}")
            print("Please try manual setup")

    elif choice == "3":
        print("\nManual Setup Instructions:")
        print("=" * 40)
        print("1. Download VGGFace2 weights from one of these sources:")
        print("   - https://github.com/ox-vgg/vgg_face2")
        print("   - https://github.com/deepinsight/insightface")
        print("   - https://www.robots.ox.ac.uk/~albanie/pytorch-models.html")
        print()
        print("2. Place the model file in the 'models/' directory")
        print("3. Update the model path in models/vggface.py")
        print()
        print("Recommended model files:")
        print("- resnet50_ft_weight.pkl (VGGFace2)")
        print("- buffalo_l.zip (InsightFace)")
        print("- vgg_face_dag.pth (Original VGGFace)")

    else:
        print("Invalid choice")
        return

    # Create a model info file
    info_file = models_dir / "model_info.txt"
    with open(info_file, "w") as f:
        f.write(f"VGGFace2 Model Setup\n")
        f.write(f"Selected option: {choice}\n")
        f.write(f"Model: {model_options.get(choice, {}).get('name', 'Manual')}\n")
        f.write(f"Downloaded at: {os.getcwd()}\n")

    print(f"\nModel info saved to: {info_file}")

def setup_alternative_model():
    """Setup alternative face recognition model if VGGFace2 is not available"""
    print("\nAlternative: Using FaceNet/ArcFace with Hugging Face")
    print("=" * 50)

    try:
        # Try to install face_recognition as backup
        import subprocess
        print("Installing alternative face recognition library...")
        subprocess.check_call(["pip", "install", "face-recognition"])
        print("✅ face-recognition installed successfully!")

        print("\nNote: This uses a different face recognition model")
        print("You may need to update the VGGFace model class to use this instead")

    except Exception as e:
        print(f"Failed to install face-recognition: {e}")
        print("\nAlternative options:")
        print("1. Use OpenCV face recognition")
        print("2. Use sklearn with basic features")
        print("3. Mock the face recognition for testing")

if __name__ == "__main__":
    print("VGGFace2 Setup Script")
    print("=" * 30)

    # Check if models directory exists
    if not os.path.exists("models"):
        os.makedirs("models")
        print("Created models directory")

    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("Please run this script from the app directory (where main.py is located)")
        exit(1)

    try:
        download_vggface2_weights()
    except KeyboardInterrupt:
        print("\nDownload cancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTrying alternative setup...")
        setup_alternative_model()

    print("\nSetup completed!")
    print("\nNext steps:")
    print("1. Update models/vggface.py with the correct model path")
    print("2. Test the model loading with: python -c 'from models.vggface import VGGFaceModel; model = VGGFaceModel()'")
    print("3. Run the main application: python main.py")
