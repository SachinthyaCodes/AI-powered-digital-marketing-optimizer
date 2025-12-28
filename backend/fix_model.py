"""
Script to fix Keras model by removing quantization_config from JSON
"""
import zipfile
import json
import os
import shutil

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'SavedModels', 'Transformer.keras')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'SavedModels', 'Transformer_fixed.keras')
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'SavedModels', 'temp_model')

print("Extracting model files...")
os.makedirs(TEMP_DIR, exist_ok=True)

# Extract the model
with zipfile.ZipFile(MODEL_PATH, 'r') as zip_ref:
    zip_ref.extractall(TEMP_DIR)

# Read and fix config.json
config_path = os.path.join(TEMP_DIR, 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

print("Removing quantization_config from all layers...")

def remove_quantization_config(obj):
    """Recursively remove quantization_config from nested dict/list"""
    if isinstance(obj, dict):
        # Remove quantization_config if it exists
        if 'quantization_config' in obj:
            del obj['quantization_config']
        # Recurse into all values
        for value in obj.values():
            remove_quantization_config(value)
    elif isinstance(obj, list):
        # Recurse into list items
        for item in obj:
            remove_quantization_config(item)

remove_quantization_config(config)

# Save fixed config
print("Saving fixed config...")
with open(config_path, 'w') as f:
    json.dump(config, f)

# Create new zip file
print(f"Creating fixed model at: {OUTPUT_PATH}")
with zipfile.ZipFile(OUTPUT_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(TEMP_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, TEMP_DIR)
            zipf.write(file_path, arcname)

# Cleanup
print("Cleaning up...")
shutil.rmtree(TEMP_DIR)

print("✅ Fixed model created successfully!")
print(f"New model: {OUTPUT_PATH}")

# Test loading
print("\nTesting fixed model...")
import tensorflow as tf

try:
    model = tf.keras.models.load_model(OUTPUT_PATH, compile=False)
    print("✅ Model loads successfully!")
    print("\nModel Summary:")
    model.summary()
except Exception as e:
    print(f"❌ Error loading fixed model: {e}")
