import requests
from datasets import Dataset
import json
from unsloth import FastLanguageModel
import time

max_seq_length = 2048 # Choose any! We auto support RoPE Scaling internally!
dtype = None # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
load_in_4bit = True # Use 4bit quantization to reduce memory usage. Can be False.

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Meta-Llama-3.1-8B",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
    # token = "hf_...", # use one if using gated models like meta-llama/Llama-2-7b-hf
)

# Define the prompt template
meal_prompt_template = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

# Define a function to fetch data from TheMealDB API
def fetch_meal_data(num_meals=10000):
    meals = []
    for _ in range(num_meals):
        # Fetch a single random meal
        response = requests.get("https://www.themealdb.com/api/json/v1/1/random.php")
        if response.status_code == 200:
            data = response.json()
            if data["meals"] is not None:
                meals.append(data["meals"][0])  # Append only the first meal object
        time.sleep(0.1)  # Sleep to avoid hitting the server too quickly (politeness delay)

    return meals

EOS_TOKEN = tokenizer.eos_token # Must add EOS_TOKEN
# Define a function to format the data
def format_meal_data_for_prompt(meals):
    examples = []
    for meal in meals:
        instruction = "Describe the recipe and ingredients for the meal."
        input_context = f"Meal: {meal['strMeal']}"
        output_response = f"Ingredients: {meal['strIngredient1']}, {meal['strIngredient2']}, ...\nInstructions: {meal['strInstructions']}"

        # Format with prompt template and add EOS token
        text = meal_prompt_template.format(instruction, input_context, output_response) + EOS_TOKEN
        examples.append(text)
    return examples

# Fetch and format the data
meals = fetch_meal_data()
formatted_data = format_meal_data_for_prompt(meals)

# Convert to Hugging Face Dataset format
dataset = Dataset.from_list(formatted_data)

# Print sample data for verification
print(dataset[0])

dataset.save_to_disk("./mydataset10k")
