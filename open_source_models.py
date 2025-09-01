import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class LLMWrapper:
    _model_cache = {}
    SUPPORTED_MODELS = {
        "llama": "meta-llama/Llama-2-7b-chat-hf",
        "qwen": "Qwen/Qwen2.5-7B-Instruct",
        "phi": "microsoft/Phi-4"
    }

    def __init__(self, model_key: str = "llama", device: str = None):
        try:
            if model_key in self.SUPPORTED_MODELS:
                self.model_name = self.SUPPORTED_MODELS[model_key]
            else:
                self.model_name = model_key      #HF model ID directly

            self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
            print(self.device)

            if self.model_name in self._model_cache:
                self.tokenizer, self.model = self._model_cache[self.model_name]
                print(f"Loaded {self.model_name} from cache.")
                return

            print(f"Loading model: {self.model_name} on {self.device}")

            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                # offload_folder="offload",  # Enables CPU offloading
                # attn_implementation="flash_attention_2"  # Speeds up inference
            )

            self.tokenizer = tokenizer
            self.model = model
            self._model_cache[self.model_name] = (tokenizer, model)

        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 3072,
        temperature: float = 0,
    ) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            inputs = self.tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(self.model.device)

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )

            return self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[-1]:],
                skip_special_tokens=True
            ).strip()
        except Exception as e:
            print(f"Error generating text: {e}")


if __name__ == "__main__":
    with open('prompts/step_to_code_destination_cities.txt', 'r') as file:
        prompt = file.read()

    step = """
# Destination cities #
# Set cities to be a list including Myrtle Beach only
# Loop through cities for 1 destination city
# Initialize Z3 solver s
# Set 'city' variable to be the index of the destination city
# Assert 'city' variable equals to city index
    """
    lines = step.split('#\n')[1]
    print(prompt+lines)

    # Use any model key ("llama", "qwen", "phi")
    qwen_llm = LLMWrapper("qwen")
    prompt = (prompt + lines)
    print("\n[Qwen Response]\n", qwen_llm.generate(prompt))
