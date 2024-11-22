import openai
import dotenv
import os

# SET THE FOLLOWING FOR EVERY BATCH
key1or2 = 2
batchNum = 1


dotenv.load_dotenv()
api_key = os.getenv(f"API_KEY{key1or2}")
openai.api_key = api_key

client = openai.OpenAI(api_key=api_key)


batch_file = client.files.create(
  file=open(f"batchFiles/batch_{batchNum}.jsonl", "rb"),
  purpose="batch"
)

batch_job = client.batches.create(
  input_file_id=batch_file.id,
  endpoint="/v1/chat/completions",
  completion_window="24h"
)

batchIDFile = open(f"batchIDs", 'a')
batchIDFile.write(f"batch_{batchNum}: {batch_file.id}\n")
batchIDFile.close()

print(batch_job)
