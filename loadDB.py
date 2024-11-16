from datasets import load_from_disk

dataset = load_from_disk('./mydataset')
numRows = len(dataset)
print(numRows)
print(dataset[0])
print()
print()
print(dataset[50])