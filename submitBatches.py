import openai
import dotenv
import os

# SET THE FOLLOWING FOR EVERY BATCH
key1or2 = 1   # 2 is anand
batchNum = 3

dotenv.load_dotenv()
api_key = os.getenv(f"API_KEY{key1or2}")
openai.api_key = api_key

client = openai.OpenAI(api_key=api_key)


batch_file = client.files.create(
  file=open(f"batchFilesNew/batch_{batchNum}.jsonl", "rb"),
  purpose="batch"
)

batch_job = client.batches.create(
  input_file_id=batch_file.id,
  endpoint="/v1/chat/completions",
  completion_window="24h"
)

os.makedirs('retrievedBatchesNew', exist_ok=True)

batchIDFile = open(f"retrievedBatchesNew/submittedBatchIDs", 'a')
batchIDFile.write(f"Key {key1or2} batch_{batchNum}: {batch_job.id}\n")
batchIDFile.close()

print(batch_job)
