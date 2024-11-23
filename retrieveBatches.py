import openai
import dotenv
import os

# SET THE FOLLOWING FOR EVERY BATCH
key1or2 = 1   # 2 is anand
batchNum = 1

dotenv.load_dotenv()
api_key = os.getenv(f"API_KEY{key1or2}")
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
        batchResultFile = open(f"retrievedBatchesNew/batch_{batchNum}_output.jsonl", "w")
        batchResultFile.write(batchOutput)
        batchResultFile.close()
        