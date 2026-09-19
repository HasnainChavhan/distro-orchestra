import csv
import random
import os

POSITIVE_TEMPLATES = [
    "I absolutely love the new {}!",
    "The {} is fantastic and works like a charm.",
    "Highly recommend this {}, it changed my life.",
    "Best {} I have ever used.",
    "Such a wonderful experience with this {}."
]

NEGATIVE_TEMPLATES = [
    "I hate this {}, it is terrible.",
    "The {} is the worst thing ever.",
    "Do not buy this {}, it broke immediately.",
    "Awful experience, the {} is a waste of money.",
    "I am so disappointed with this {}."
]

NEUTRAL_TEMPLATES = [
    "The {} is okay.",
    "I have no strong feelings about this {}.",
    "This is a standard {}.",
    "It's an average {}, nothing special.",
    "The {} does what it is supposed to do."
]

SUBJECTS = ["product", "app", "service", "device", "feature", "update", "phone", "laptop", "software", "tool"]

def generate_samples(num_samples=500):
    data = []
    for _ in range(num_samples):
        sentiment = random.choice(["POSITIVE", "NEGATIVE", "NEUTRAL"])
        subject = random.choice(SUBJECTS)
        if sentiment == "POSITIVE":
            text = random.choice(POSITIVE_TEMPLATES).format(subject)
        elif sentiment == "NEGATIVE":
            text = random.choice(NEGATIVE_TEMPLATES).format(subject)
        else:
            text = random.choice(NEUTRAL_TEMPLATES).format(subject)
        data.append({"text": text, "sentiment": sentiment})
    
    os.makedirs(os.path.dirname("data/samples.csv"), exist_ok=True)
    with open("data/samples.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "sentiment"])
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated {num_samples} samples to data/samples.csv")

if __name__ == "__main__":
    generate_samples()
