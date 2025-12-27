"""
Proper SinLlama Modal Service for MarketMatic
Based on the correct setup pattern from notebook using PEFT adapter approach
"""

import modal
from typing import Dict, Any, Optional
import json
import time

# Define Modal image with proper dependencies for SinLlama PEFT setup
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "torch==2.3.0",
        "transformers>=4.56.0", 
        "accelerate>=1.10.0",
        "peft>=0.10.0",
        "bitsandbytes>=0.43.0",
        "huggingface-hub>=0.25.0",
        "sentencepiece",
        "protobuf==5.27.3",
        "numpy",
        "requests",
        "fastapi",
        "pydantic"
    ])
    # Remove model downloads from build - will do at runtime
)

app = modal.App("marketmatic-sinllama-proper")

@app.cls(
    image=image,
    gpu="A10G",  # A10G supports bfloat16 as per notebook
    memory=65536,  # 64GB RAM
    cpu=8,  # 8 CPU cores
    timeout=300,  # 5 minutes
    min_containers=1
)
class SinLlamaProperService:
    """Proper SinLlama service using PEFT adapter approach from notebook"""
    
    @modal.enter()
    def setup_model(self):
        print("🔥 Setting up SinLlama with proper PEFT approach...")
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import PeftModel
        from huggingface_hub import login
        
        # Authenticate with HuggingFace
        HF_TOKEN = "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"
        login(token=HF_TOKEN)
        print("🔑 Authenticated with HuggingFace")
        
        # Model IDs from notebook
        self.BASE_MODEL_ID = "meta-llama/Meta-Llama-3-8B"
        self.ADAPTER_ID = "polyglots/SinLlama_v01"
        self.EXTENDED_TOKENIZER_ID = "polyglots/Extended-Sinhala-LLaMA"
        
        # A10G supports bfloat16
        dtype = torch.bfloat16
        
        # 4-bit quantization config for the base model
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=dtype,
        )
        
        print("📥 Loading extended Sinhala tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.EXTENDED_TOKENIZER_ID,
            token=HF_TOKEN
        )
        
        # Make sure special tokens exist
        if self.tokenizer.pad_token is None and self.tokenizer.eos_token is not None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        target_vocab_size = len(self.tokenizer)
        print(f"📏 Target vocab size (extended): {target_vocab_size}")
        
        print("📥 Loading 4-bit base Llama-3-8B model...")
        base_model = AutoModelForCausalLM.from_pretrained(
            self.BASE_MODEL_ID,
            device_map="auto",
            quantization_config=bnb_config,
            torch_dtype=dtype,
            token=HF_TOKEN
        )
        
        # IMPORTANT: resize embeddings BEFORE loading adapter
        print("📏 Resizing token embeddings to match extended vocab...")
        base_model.resize_token_embeddings(target_vocab_size)
        
        print("🔗 Attaching SinLlama LoRA adapter...")
        self.model = PeftModel.from_pretrained(
            base_model,
            self.ADAPTER_ID,
            device_map="auto",
            low_cpu_mem_usage=True,
            token=HF_TOKEN
        )
        
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("✅ SinLlama model ready!")
        print(f"📊 Final vocab size (model): {self.model.get_input_embeddings().weight.shape[0]}")
        print(f"📊 Final vocab size (tokenizer): {len(self.tokenizer)}")
        print(f"🎯 Device: {self.device}")
    
    def create_prompt(self, user_message: str, context: str = "") -> str:
        """Create a structured prompt for SinLlama following notebook pattern"""
        system_prompt = f"""ඔබ සිංහල භාෂාවෙන් සහ ඉංග්‍රීසි භාෂාවෙන් උදව් කරන, හිතකාමී සහ වෘත්තීය Chatbot එකකි.

{context}

ඔබට සිංහල සහ ඉංග්‍රීසි දෙකේම ප්‍රශ්න වලට උදව්ක් සහ නිවැරදි පිළිතුරු ලබා දීමට හැකිය."""

        # Following the notebook's prompt format
        prompt = (
            f"[SYSTEM] {system_prompt}\n\n"
            f"[USER] {user_message}\n"
            f"[ASSISTANT]"
        )
        return prompt
    
    @modal.method()
    def generate_response(self, message: str, context: str = "", **kwargs) -> Dict[str, Any]:
        """Generate response using proper SinLlama PEFT model"""
        try:
            import torch
            start_time = time.time()
            
            # Create prompt
            prompt = self.create_prompt(message, context)
            
            # Tokenize input (following notebook approach)
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                add_special_tokens=False,
            ).to(self.device)
            
            # Generation parameters
            max_new_tokens = kwargs.get('max_tokens', 256)
            temperature = kwargs.get('temperature', 0.8)
            top_p = kwargs.get('top_p', 0.95)
            
            # Generate response (following notebook approach)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    top_p=top_p,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            
            # Take only the newly generated tokens (after the prompt)
            generated_ids = outputs[0][inputs["input_ids"].shape[-1]:]
            response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            response = response.strip()
            
            # If response is empty or too short, provide a default
            if not response or len(response.strip()) < 5:
                response = "මට ඔබේ ප්‍රශ්නය තේරුම් වෙනවා. කරුණාකර වැඩි විස්තර දෙන්න? (I understand your question. Could you please provide more details?)"
            
            generation_time = time.time() - start_time
            
            return {
                "response": response,
                "model": "SinLlama_v01_PEFT",
                "generation_time": round(generation_time, 2),
                "timestamp": time.time(),
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error generating response: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error. Please try again. (සමාවෙන්න, මට දෝෂයක් ඇති වුණා. කරුණාකර නැවත උත්සාහ කරන්න.) Error: {str(e)}",
                "model": "SinLlama_v01_PEFT",
                "generation_time": 0,
                "timestamp": time.time(),
                "success": False,
                "error": str(e)
            }

# Create FastAPI-compatible web endpoint
@app.function(
    image=image,
    min_containers=1
)
@modal.fastapi_endpoint(method="POST", label="sinllama-proper-chat-endpoint")
def chat_endpoint(data: Dict[str, Any]) -> Dict[str, Any]:
    """Web endpoint for proper SinLlama chat"""
    try:
        user_message = data.get("message", "")
        context = data.get("context", "")
        
        if not user_message:
            return {
                "error": "No message provided",
                "success": False
            }
        
        # Call the SinLlama service class method - fix parameter conflict
        service_cls = SinLlamaProperService()
        
        # Extract other parameters separately
        generation_params = {
            "max_tokens": data.get("max_tokens", 150),
            "temperature": data.get("temperature", 0.7),
            "top_p": data.get("top_p", 0.95)
        }
        
        result = service_cls.generate_response.remote(
            message=user_message,
            context=context,
            **generation_params
        )
        
        return result
        
    except Exception as e:
        print(f"❌ Endpoint error: {str(e)}")
        return {
            "response": "I'm sorry, there was an error processing your request. (සමාවෙන්න, ඔබේ ඉල්ලීම සැකසීමේදී දෝෂයක් ඇති විය.)",
            "error": str(e),
            "success": False,
            "model": "SinLlama_v01_PEFT"
        }

# Test function
@app.function(image=image)
def test_model():
    """Test the proper SinLlama PEFT model"""
    test_messages = [
        "Hello, how are you?",
        "කොහොමද?",
        "What can you tell me about Sri Lanka?",
        "ශ්‍රී ලංකාව ගැන කියන්න",
        "Can you help me with grocery shopping?"
    ]
    
    # Create the service and call methods directly
    service = SinLlamaProperService()
    for msg in test_messages:
        print(f"\n🔍 Testing: {msg}")
        result = service.generate_response.remote(msg)
        print(f"📝 Response: {result['response']}")
        print(f"⏱️ Time: {result['generation_time']}s")

if __name__ == "__main__":
    # Deploy or test locally
    print("🚀 SinLlama Proper PEFT Service Ready!")