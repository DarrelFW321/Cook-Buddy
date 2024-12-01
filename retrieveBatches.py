import openai
import dotenv
import os

# SET THE FOLLOWING FOR EVERY BATCH
key1or2 = 1  # 2 is anand
batchNum = 7

dotenv.load_dotenv()
api_key = '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'
openai.api_key = api_key

client = openai.OpenAI(api_key=api_key)


with open("retrievedBatchesNew/submittedBatchIDs", "r") as batchIDFile:
    reader = batchIDFile.read()
    lines = reader.splitlines()
    batchID = ((lines[batchNum]).split(": "))[1]

    print(batchID)
    
    batch = client.batches.retrieve(batchID)

    print(batch.status)
    if (batch.status == "completed"):
        batchOutput = client.files.content(batch.output_file_id).content
        batchResultFile = open(f"retrievedBatchesNew/batch_{batchNum}_output.jsonl", "wb")
        batchResultFile.write(batchOutput)
        batchResultFile.close()
