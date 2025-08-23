import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


class LLMWrapper:
    _model_cache = {}
    SUPPORTED_MODELS = {
        "llama": "meta-llama/Llama-2-7b-chat-hf",
        "qwen": "Qwen/Qwen2.5-7B-Instruct",
        "phi": "microsoft/Phi-4-mini-instruct"
    }

    def __init__(self, model_key: str = "llama", device: str = None):
        if model_key in self.SUPPORTED_MODELS:
            self.model_name = self.SUPPORTED_MODELS[model_key]
        else:
            self.model_name = model_key      #HF model ID directly

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(self.device)

        if self.model_name in self._model_cache:
            self.pipeline = self._model_cache[self.model_name]
            print(f"Loaded {self.model_name} from cache.")
            return

        print(f"Loading model: {self.model_name} on {self.device}")

        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            offload_folder="offload",  # Enables CPU offloading
            attn_implementation="flash_attention_2",  # Speeds up inference
            trust_remote_code=True
        )

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=0 if self.device == "cuda" else -1
        )

        self.pipeline = pipe
        self._model_cache[self.model_name] = pipe  # save in cache

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 3072,
        temperature: float = 0.7,
    ) -> str:

        outputs = self.pipeline(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.pipeline.tokenizer.eos_token_id,
        )
        return outputs[0]["generated_text"][len(full_prompt):].strip()



if __name__ == "__main__":
    queries = [
        "Convert the following travel plan request into JSON:\nPlan 3 days trip from Seattle to Texas.\nJSON:",
        "Write a Python function to calculate factorial recursively."
    ]

    llama_llm = LLMWrapper("llama")
    for q in queries:
        print("\n[LLaMA Response]\n", llama_llm.generate(q))

    qwen_llm = LLMWrapper("qwen")
    for q in queries:
        print("\n[Qwen Response]\n", qwen_llm.generate(q))

    phi_llm = LLMWrapper("phi")
    for q in queries:
        print("\n[Phi Response]\n", phi_llm.generate(q))
