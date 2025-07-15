import json

input_file = 'user-wallet-transactions.json'
output_file = 'sample_transactions.json'
sample_size = 10

with open(input_file, 'r') as f:
    data = json.load(f)

sample = data[:sample_size]

with open(output_file, 'w') as f:
    json.dump(sample, f, indent=2)

print(f"Extracted {sample_size} records to {output_file}") 