import requests
from datasets import Dataset
import json
import time
import csv
import pandas as pd
import openai
import tiktoken
import random
from dotenv import load_dotenv
import os
import re
import csv


with open(r'RecipeNLG_dataset.csv', newline='') as csvFile:
    csvReader = csv.reader(csvFile)
    
    curBatchNum = -1
    systemMessage = "For each recipe name reply with 1 word for each in format: Cuisine (e.g. French, Thai), dish type (e.g. pasta, curry), course (snack, entree). Separate recipe responses by line." # 46 tokens
    inputString = ""
    for request in csvReader:
        if ((request[0]+1) % 50000 == 0):
            curBatchNum += 1
            os.makedirs("batchFiles", exist_ok=True)
            fileName = f"batchFiles/batch_{curBatchNum}.jsonl"
            currentFile = open(fileName, 'w')
            
        if ((request[0]+1) % 100 == 0):
            inputString = inputString.rstrip()
            requestDict = {"custom_id": f"request-{request[0]}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": systemMessage}, {"role": "user", "content": inputString}]}}
            currentFile.write(json.dumps(requestDict))
            inputString = ""
            
        inputString += f"{request[1]}\n"
    
