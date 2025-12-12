"""
Build Lucene index for the medical chatbot using pyserini.
This script creates a lookup_db index from samples_retrieve_data.json.
"""
import json
import os
import shutil

# Create a jsonl file for indexing (pyserini format)
data_dir = './data/samples_retrieve_data.json'
output_dir = './lookup_db_corpus'
index_dir = './lookup_db'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Read the JSON data
with open(data_dir, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Convert to JSONL format for pyserini
with open(os.path.join(output_dir, 'docs.jsonl'), 'w', encoding='utf-8') as f:
    for doc in data:
        json_line = json.dumps(doc, ensure_ascii=False)
        f.write(json_line + '\n')

print(f"Created corpus with {len(data)} documents in {output_dir}")
print("Now run the following command to build the index:")
print(f"python -m pyserini.index.lucene --collection JsonCollection --input {output_dir} --index {index_dir} --generator DefaultLuceneDocumentGenerator --threads 1 --storePositions --storeDocvectors --storeRaw")
