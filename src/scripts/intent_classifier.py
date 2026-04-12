from transformers import pipeline

# Load the classifier from Hugging Face
classifier = pipeline(
    "text-classification", 
    model="Thrad/thrad-bert-conversation-classifier",
    truncation=True,        # Cuts text longer than 512 tokens
    max_length=512
)

def test_classifier(text):
    # The model returns a list of dictionaries
    result = classifier(text)[0]
    
    print(f"Input Text: '{text}'")
    print(f"Label:      {result['label']}")
    print(f"Confidence: {result['score']:.4f}")
    print("-" * 30)

test_examples = [
    "How do I solve this quadratic equation for my math homework?",
    "Can you help me write a Python script to scrape a website?",
    "What are the best noise-canceling headphones under $200?",
    "Tell me a story about a dragon who lives in a library.",
    "I've been feeling really lonely lately and don't know who to talk to.",
    "Hey there, how is your day going?"
]

if __name__ == "__main__":
    for text in test_examples:
        test_classifier(text)