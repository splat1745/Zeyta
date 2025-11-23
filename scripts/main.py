from llama_cpp import Llama

# Path to your GGUF model file
model_path = "C:/models/llama-3-7b-instruct.Q4_K_M.gguf"

# Load the model
llm = Llama(model_path=model_path, n_ctx=2048, n_threads=8)

# Generate a response
prompt = "Explain Newton's third law in one line."
output = llm(prompt, max_tokens=100)

# Print model response
print(output["choices"][0]["text"])
