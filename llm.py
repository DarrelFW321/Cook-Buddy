import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
torch.cuda.empty_cache()  # Clear cache after generation

# Load the model and tokenizer without quantization
model = AutoModelForCausalLM.from_pretrained("allenyang687/cookbuddymodel")
tokenizer = AutoTokenizer.from_pretrained("allenyang687/cookbuddymodel")

# Enable gradient checkpointing (optional)
model.gradient_checkpointing_enable()

# Clear cache before starting
torch.cuda.empty_cache()

# Set up the TextStreamer for streaming the output (optional)
text_streamer = TextStreamer(tokenizer)

# Function to handle generating responses for a given input
def generate_response(user_input):
    prompt = """Hold Conversation.""

    ### Instruction:
    {instruction}

    ### Input:
    {input}

    ### Response:
    {response}"""

    inputs = tokenizer(
        [prompt.format(
            instruction="Be very specific with instructions and give the time and temperature to cook everything at.",  # You can customize this or make dynamic
            input=user_input,  # The user input will be used here
            response=""  # Leave blank for generation   
        )],
        return_tensors="pt"
    ).to("cuda")

    # Use mixed precision (optional)
    from torch.cuda.amp import autocast

    # Use no_grad() to save memory during inference
    with torch.no_grad(), autocast():
        generated_output = model.generate(
            **inputs, 
            streamer=text_streamer, 
            max_new_tokens=612,  # Limit token count for output
            temperature=0.7  # Control randomness (lower value = more deterministic)
        )

    # Decode the generated tokens into a string
    generated_text = tokenizer.decode(generated_output[0], skip_special_tokens=True)

    return generated_text

#Live chat loop
print("Chat with the model! Type 'exit' to stop.")
while True:
    user_input = input("You: ")  # Take input from the user
    if user_input.lower() == 'exit':
        print("Exiting chat. Goodbye!")
        break  # Exit the loop if the user types 'exit'
    else:
        response = generate_response(user_input)  # Generate the model response based on user input
        print(f"Model: {response}")  # Print the generated response