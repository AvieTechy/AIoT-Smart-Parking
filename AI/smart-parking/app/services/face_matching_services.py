from deepface import DeepFace

def check_matching(img1_path: str, img2_path: str):
    # Compare two images
    result = DeepFace.verify(img1_path=img1_path,
                            img2_path=img2_path,
                            model_name="VGG-Face")

    if result["verified"]:
        return True
    else:
        return False
# Alias cho đúng import trong router
checking_matching = check_matching
