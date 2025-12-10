"""
Piper Voice Model Downloader
Automatically downloads Piper TTS voice models for the navigation system
"""

import os
import urllib.request
import sys

# Available voice models
VOICE_MODELS = {
    "1": {
        "name": "en_US-lessac-medium (Female, Clear) [RECOMMENDED]",
        "files": [
            "en_US-lessac-medium.onnx",
            "en_US-lessac-medium.onnx.json"
        ],
        "size": "~30MB"
    },
    "2": {
        "name": "en_US-ryan-medium (Male, Warm)",
        "files": [
            "en_US-ryan-medium.onnx",
            "en_US-ryan-medium.onnx.json"
        ],
        "size": "~30MB"
    },
    "3": {
        "name": "en_GB-alan-medium (British Male)",
        "files": [
            "en_GB-alan-medium.onnx",
            "en_GB-alan-medium.onnx.json"
        ],
        "size": "~30MB"
    },
    "4": {
        "name": "en_GB-jenny_dioco-medium (British Female)",
        "files": [
            "en_GB-jenny_dioco-medium.onnx",
            "en_GB-jenny_dioco-medium.onnx.json"
        ],
        "size": "~30MB"
    }
}

BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
MODELS_DIR = "piper_models"


def download_file(url, destination):
    """
    Download a file with progress indicator

    Args:
        url: URL to download from
        destination: Local file path to save to
    """
    print(f"Downloading: {os.path.basename(destination)}")

    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r  Progress: {percent}%")
        sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, destination, progress_hook)
        print()  # New line after progress
        return True
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        return False


def main():
    """Main downloader function"""
    print("=" * 60)
    print("  PIPER TTS VOICE MODEL DOWNLOADER")
    print("  Blind Navigation Assistance System")
    print("=" * 60)
    print()

    # Show available models
    print("Available voice models:")
    print()
    for key, model in VOICE_MODELS.items():
        print(f"  [{key}] {model['name']}")
        print(f"      Size: {model['size']}")
        print()

    # Get user choice
    choice = input("Select a model to download (1-4) [default: 1]: ").strip()

    if not choice:
        choice = "1"

    if choice not in VOICE_MODELS:
        print("❌ Invalid choice. Exiting.")
        return

    selected_model = VOICE_MODELS[choice]

    print()
    print(f"Selected: {selected_model['name']}")
    print()

    # Create models directory if it doesn't exist
    if not os.path.exists(MODELS_DIR):
        print(f"Creating directory: {MODELS_DIR}")
        os.makedirs(MODELS_DIR)

    # Download files
    print("Starting download...")
    print()

    success = True
    for filename in selected_model['files']:
        url = BASE_URL + filename
        destination = os.path.join(MODELS_DIR, filename)

        # Skip if file already exists
        if os.path.exists(destination):
            print(f"✓ {filename} already exists, skipping")
            continue

        if not download_file(url, destination):
            success = False
            break

    print()

    if success:
        print("=" * 60)
        print("  ✅ DOWNLOAD COMPLETE!")
        print("=" * 60)
        print()
        print("Files saved to:", MODELS_DIR)
        print()
        print("Next steps:")
        print("  1. Update config.py with the model path:")
        print(f"     PIPER_MODEL_PATH = './{MODELS_DIR}/{selected_model['files'][0]}'")
        print("  2. Run: python main.py")
        print("  3. Click 'Test Audio' to verify")
        print()
    else:
        print("=" * 60)
        print("  ❌ DOWNLOAD FAILED")
        print("=" * 60)
        print()
        print("Please check your internet connection and try again.")
        print("Or download manually from:")
        print("  https://github.com/rhasspy/piper/releases/tag/v1.2.0")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDownload cancelled.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()