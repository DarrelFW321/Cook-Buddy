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


recsPerRequest = 100      # customize
requestsPerBatch = 50000    # customize
recsPerBatch = recsPerRequest * requestsPerBatch
totalRecipes = 2231142
maxTokens = 2000000     # set to 2000000
maxBytes = 200000000    # set to 200000000

csvReader = pd.read_csv(r'RecipeNLG_dataset.csv', nrows=totalRecipes+1)

systemMessage = "For each recipe name reply with 1 word for each in format: Cuisine (e.g. French, Thai), dish type (e.g. pasta, curry), course (snack, entree). 0 numbering but no recipe name" # 46 tokens
inputString = ""

curBatchNum = 0
os.makedirs('batchFiles', exist_ok=True)
currentFile = open(f"batchFiles/batch_{curBatchNum}.jsonl", 'w')
curBatchNum += 1
encoding = tiktoken.encoding_for_model("gpt-4o-mini")
sysMsgTokenCnt = len(encoding.encode(systemMessage))
#jsonLine = r'{"custom_id": "request-0", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": "For each recipe name reply with 1 word for each in format: Cuisine (e.g. French, Thai), dish type (e.g. pasta, curry), course (snack, entree). 0 numbering but no recipe name"}, {"role": "user", "content": ""}]}}\n'
#jsonLineByteCnt = len(jsonLine.encode("utf-8"))

tokenSum = 0
tokenSum += sysMsgTokenCnt
# byteSum = 0
# byteSum += jsonLineByteCnt

requestNum = 0
posAdjust = 0
recipeInReqIndex = 0

os.makedirs("batchFiles", exist_ok=True)
nextStart = open(f"batchFiles/nextStart.txt", 'w')
for i, recipe in csvReader.iterrows():
    curName = recipe[1] 
    curTokens = len(encoding.encode(curName))
    #curBytes = len(curName.encode("utf-8"))
    
    if (tokenSum + curTokens) > maxTokens:                       
        inputString = inputString.rstrip()
        tokenSum -= 1
        requestDict = {"custom_id": f"request-{requestNum}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": systemMessage}, {"role": "user", "content": inputString}]}}
        currentFile.write(json.dumps(requestDict))
        currentFile.write("\n")
        inputString = ""
        
        tokenSum = 0
        tokenSum += sysMsgTokenCnt
        requestNum += 1
        
        currentFile.close()
        currentFile = open(f"batchFiles/batch_{curBatchNum}.jsonl", 'w')
        
        nextStart.write(f"{curBatchNum}, {recipe[0]}, {curName}\n")
        print([curBatchNum, recipe[0], curName], "tokenLimitReached")
        curBatchNum += 1
    """
    if (byteSum + curBytes) > maxBytes:               
        inputString = inputString.rstrip()
        byteSum -= 1
        tokenSum -= 1
        requestDict = {"custom_id": f"request-{requestNum}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": systemMessage}, {"role": "user", "content": inputString}]}}
        currentFile.write(json.dumps(requestDict))
        currentFile.write("\n")
        inputString = ""
        
        tokenSum += sysMsgTokenCnt
        byteSum = 0
        requestNum += 1
        
        currentFile.close()
        currentFile = open(f"batchFiles/batch_{curBatchNum}.jsonl", 'w')
        curBatchNum += 1
    """
    inputString += f"{curName}\n"
    tokenSum += curTokens + 1   # + 1 for newline
    #byteSum += curBytes + 1
    
    if (recipeInReqIndex == recsPerRequest):
        recipeInReqIndex = 0
        inputString = inputString.rstrip()
        #byteSum -= 1
        tokenSum -= 1
        requestDict = {"custom_id": f"request-{requestNum}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": systemMessage}, {"role": "user", "content": inputString}]}}
        currentFile.write(json.dumps(requestDict))
        currentFile.write("\n")
        inputString = ""
        
        tokenSum += sysMsgTokenCnt
        #byteSum += jsonLineByteCnt
        requestNum += 1
    
    recipeInReqIndex += 1

print(recipe)

if (inputString != ""):
    inputString = inputString.rstrip()
    #byteSum -= 1
    tokenSum -= 1
    requestDict = {"custom_id": f"request-{requestNum}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": systemMessage}, {"role": "user", "content": inputString}]}}
    currentFile.write(json.dumps(requestDict))
    currentFile.write("\n")

nextStart.close()
currentFile.close()