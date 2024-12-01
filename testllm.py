from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "allenyang687/cookbuddymodel"  # Replace with your actual model path

try:
    # Load the model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("Model and tokenizer loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
