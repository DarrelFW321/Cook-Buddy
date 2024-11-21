import requests
from datasets import Dataset
import json
import time
import csv
import pandas as pd
import openai
import tiktoken
import random
import os
import re
import csv


csvReader = pd.read_csv(r'RecipeNLG_dataset.csv', nrows=51)

recsPerRequest = 5      # customize
requestsPerBatch = 2    # customize
recsPerBatch = recsPerRequest * requestsPerBatch
totalRequests = 50

systemMessage = "For each recipe name reply with 1 word for each in format: Cuisine (e.g. French, Thai), dish type (e.g. pasta, curry), course (snack, entree). Separate recipe responses by line." # 46 tokens
inputString = ""

curBatchNum = 0
currentFile = open(f"batchFiles/batch_{curBatchNum}.jsonl", 'w')
curBatchNum += 1

for i, recipe in csvReader.iterrows():
    inputString += f"{recipe[1]}\n"
    
    if ((i+1) % recsPerRequest == 0):
        inputString = inputString.rstrip()
        requestDict = {"custom_id": f"request-{int(((i+1)/recsPerRequest)-(requestsPerBatch-1))}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": systemMessage}, {"role": "user", "content": inputString}]}}
        currentFile.write(json.dumps(requestDict))
        currentFile.write("\n")
        inputString = "" 

    if i >= totalRequests-1:
        break
    
    if ((i+1) % recsPerBatch == 0):
        os.makedirs("batchFiles", exist_ok=True)
        currentFile = open(f"batchFiles/batch_{curBatchNum}.jsonl", 'w')
        curBatchNum += 1
