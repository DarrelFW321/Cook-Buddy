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


recsPerRequest = 50      # customize
requestsPerBatch = 50000    # customize
recsPerBatch = recsPerRequest * requestsPerBatch
totalRecipes = 2231142  # set to 2231142
maxTokens = 2000000     # set to 2000000
maxBytes = 200000000    # set to 200000000

csvReader = pd.read_csv(r'RecipeNLG_dataset.csv', nrows=totalRecipes)

curBatchNum = 0
os.makedirs('batchFilesNew', exist_ok=True)
currentFile = open(f"batchFilesNew/batch_{curBatchNum}.jsonl", 'w')
curBatchNum += 1
encoding = tiktoken.encoding_for_model("gpt-4o-mini")
sysMsgTokenCnt = len(encoding.encode(f"For each of {recsPerRequest} recipe names reply with 1 word for each in format: Cuisine (ex. French, Thai), dish type (ex. pasta, curry), course (snack, entree). Number recipe responses but don't include recipe names"))       

tokenSum = 0
tokenSum += sysMsgTokenCnt

requestNum = 0
nextRecipeIndex = 0
inputString = ""

nextStart = open(f"batchFilesNew/nextStart.txt", 'w')
for i, recipe in csvReader.iterrows():
    curName = recipe[1] 
    curTokens = len(encoding.encode(curName)) + 1   # +1 for number
    
    if (tokenSum + curTokens) > maxTokens:                       
        inputString = inputString.rstrip()
        tokenSum -= 1
        requestDict = {"custom_id": f"request-{requestNum}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": f"For each of {nextRecipeIndex} recipe names reply with 1 word for each in format: Cuisine (ex. French, Thai), dish type (ex. pasta, curry), course (snack, entree).  Number recipe responses but don't include recipe names"}, {"role": "user", "content": inputString}]}}
        currentFile.write(json.dumps(requestDict))
        currentFile.write("\n")
        inputString = ""
        
        tokenSum = 0
        tokenSum += sysMsgTokenCnt
        requestNum += 1
        
        currentFile.close()
        currentFile = open(f"batchFilesNew/batch_{curBatchNum}.jsonl", 'w')
        
        nextStart.write(f"{curBatchNum}, {recipe[0]}, {curName}\n")
        print([curBatchNum, recipe[0], curName], "tokenLimitReached")
        curBatchNum += 1
        
        nextRecipeIndex = 0

    inputString += f"{nextRecipeIndex+1} {curName}\n"
    tokenSum += curTokens + 1   # + 1 for newline
    
    nextRecipeIndex += 1
    
    if (nextRecipeIndex == recsPerRequest):
        inputString = inputString.rstrip()
        tokenSum -= 1
        requestDict = {"custom_id": f"request-{requestNum}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": f"For each of {recsPerRequest} recipe names reply with 1 word for each in format: Cuisine (ex. French, Thai), dish type (ex. pasta, curry), course (snack, entree). Number recipe responses but don't include recipe names"}, {"role": "user", "content": inputString}]}}
        currentFile.write(json.dumps(requestDict))
        currentFile.write("\n")
        inputString = ""
        
        tokenSum += sysMsgTokenCnt
        requestNum += 1
        
        nextRecipeIndex = 0



if (inputString != ""):
    inputString = inputString.rstrip()
    requestDict = {"custom_id": f"request-{requestNum}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": f"For each of {nextRecipeIndex} recipe names reply with 1 word for each in format: Cuisine (ex. French, Thai), dish type (ex. pasta, curry), course (snack, entree). Number recipe responses but don't include recipe names"}, {"role": "user", "content": inputString}]}}
    currentFile.write(json.dumps(requestDict))
    currentFile.write("\n")

nextStart.close()
currentFile.close()
