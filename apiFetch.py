import requests
from datasets import Dataset
import json
import time

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

# Define a function to format the data
def format_meal_data_for_prompt(meals):
    examples = []
    for meal in meals:
        instruction = "Describe the recipe and ingredients for the meal."
        input_context = f"Meal: {meal['strMeal']}"
        output_response = f"Ingredients: {meal['strIngredient1']}, {meal['strIngredient2']}, ...\nInstructions: {meal['strInstructions']}"

        # Format with prompt template and add EOS token
        text = meal_prompt_template.format(instruction, input_context, output_response) + "<|endoftext|>"  # EOS token
        examples.append({"instruction": instruction, "input": input_context, "output": output_response, "text": text})
    return examples

# Fetch and format the data
meals = fetch_meal_data()
formatted_data = format_meal_data_for_prompt(meals)

# Convert to Hugging Face Dataset format
dataset = Dataset.from_list(formatted_data)

# Print sample data for verification
print(dataset[0])

dataset.save_to_disk("./mydataset10k")
