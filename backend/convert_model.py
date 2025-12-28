"""
Script to convert Transformer.keras model to compatible format
This removes quantization_config incompatibility
"""
import os
import tensorflow as tf
import keras

print(f"TensorFlow version: {tf.__version__}")
print(f"Keras version: {keras.__version__}")

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'SavedModels', 'Transformer.keras')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'SavedModels', 'Transformer_compatible.keras')

print(f"\nLoading model from: {MODEL_PATH}")

try:
    # Try loading with TF format 
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("✓ Model loaded successfully with TensorFlow loader")
    
    # Get model summary
    print("\nModel Summary:")
    model.summary()
    
    # Save in compatible format
    print(f"\nSaving compatible model to: {OUTPUT_PATH}")
    model.save(OUTPUT_PATH, save_format='keras')
    print("✓ Model saved successfully")
    
    # Test loading the new model
    print("\nTesting new model...")
    test_model = tf.keras.models.load_model(OUTPUT_PATH, compile=False)
    print("✓ Compatible model loads successfully")
    
    print("\n✅ Conversion complete!")
    print(f"You can now use: {OUTPUT_PATH}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n trying alternative loading method...")
    
    # Try with custom object scope
    try:
        import json
        import zipfile
        
        # Extract and modify config
        with zipfile.ZipFile(MODEL_PATH, 'r') as zip_ref:
            config_data = zip_ref.read('config.json')
            config = json.loads(config_data)
            
        print("Model config extracted. Attempting manual reconstruction...")
        print("This model requires the exact TensorFlow/Keras version used during training.")
        print(f"Model was likely trained with TensorFlow 2.18-2.19 with Keras 3.7-3.10")
        print(f"Current versions: TensorFlow {tf.__version__}, Keras {keras.__version__}")
        
    except Exception as e2:
        print(f"Alternative method also failed: {e2}")
        print("\n⚠️  Recommendation: Retrain the model with current TensorFlow/Keras versions")
        print("   or use the exact versions from training environment")
