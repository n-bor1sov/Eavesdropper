import hashlib
import random
import re
from faker import Faker

def get_hash_seed(text):
    """
    Generate a hash seed from the input text.

    Args:
    - text (str): The input text to be hashed.

    Returns:
    - int: A hash-based seed.
    """
    hash_value = hashlib.md5(text.encode()).hexdigest()
    return int(hash_value, 16) % (2**32)  # Ensure the seed fits within a 32-bit integer range

def create_fake_company(text):
    """
    Create a fake company name based on the input text.

    Args:
    - text (str): The input text.

    Returns:
    - str: A fake company name.
    """
    if len(text) <= 4:
        return ''.join(random.choices(text, k=len(text)))
    else:
        fake = Faker()
        return fake.company()
    
def create_fake_geolocation(text):
    """
    Create a fake geographical location based on the input text.

    Args:
    - text (str): The input text.

    Returns:
    - str: A fake geographical location.
    """
    fake = Faker()
    
    return fake.city()

def create_mask(entity_group, text, seed=None):
    """
    Generates a fake replacement for a given entity group.

    Args:
    - entity_group (str): The type of entity to be masked.
    - text (str): The text to be masked.
    - seed (int): Seed for reproducibility.

    Returns:
    - str: A fake replacement or None if no masking is needed.
    """
    random.seed(seed)
    fake = Faker()
    
    entity_group_functions = {
        'ORG': lambda: create_fake_company(text),
        'PERSON': lambda: fake.name(),
        'GEO': lambda: create_fake_geolocation(text)
        }
    
    return entity_group_functions.get(entity_group, lambda: None)()

def mask(predictions, reproducible=True):
    """
    Mask entities in the input text with fake data.

    Args:
    - predictions (list of dict): Each dict contains 'text' and a list of entities with 'word' and 'entity_group'.
    - reproducible (bool): Whether to use a seed for reproducibility.

    Returns:
    - new_texts (list of str): Texts with masked entities.
    - key_dicts (list of dict): Mapping of original entities to fake ones.
    """
    new_texts, key_dicts = [], []
    for prediction in predictions:
        new_text = prediction['text']
        key_dict = {}
        seed = get_hash_seed(new_text) if reproducible else None
        
        for entity in prediction.get('entities', []):
            original = entity['word']
            if original not in key_dict:
                mask_value = create_mask(entity['entity_group'], original, seed)
                new_text = new_text.replace(original, mask_value)
                key_dict[original] = mask_value
        
        new_texts.append(new_text)
        key_dicts.append(key_dict)
    
    return new_texts, key_dicts

def demask(new_texts, key_dicts):
    """
    Demask fake data and restore original entities in the text.

    Args:
    - new_texts (list of str): Texts with fake data.
    - key_dicts (list of dict): Mapping of fake data to original entities.

    Returns:
    - list of str: Texts with original entities restored.
    """
    demasked_texts = []
    for text, key_dict in zip(new_texts, key_dicts):
        demasked_text = text
        if key_dict:
            for original, fake in key_dict.items():
                demasked_text = demasked_text.replace(fake, original)
        demasked_texts.append(demasked_text)
    
    return demasked_texts

# Sample data
sample = [
    {
        "text": "John Doe opened the first 'ABC Stores' in New York City on 10/15/2004, and by the end of the year, 15 more stores were launched.\n\nOn 04/13/2023, ABC Stores expanded to Los Angeles, California, opening 15 stores in the first half of the year.\n\nOn 07/02/2013, ABC Stores celebrated the opening of its 25th store in London.",
        "entities": [
            {"entity_group": "PERSON", "word": "John Doe", "start": 0, "end": 8},
            {"entity_group": "ORG", "word": "ABC Stores", "start": 25, "end": 35},
            {"entity_group": "GEO", "word": "New York City", "start": 49, "end": 63},
            {"entity_group": "GEO", "word": "Los Angeles, California", "start": 232, "end": 258},
            {"entity_group": "GEO", "word": "London", "start": 388, "end": 395}
        ]
    }
]

# Mask and demask the sample data
new_texts, key_dicts = mask(sample)
print('Original:')
print(sample[0]['text'])
print()

print('Masked:')
print(new_texts[0])
print()

print('*' * 50)

demasked_texts = demask(new_texts, key_dicts)
for old_text, new_text in zip(sample, demasked_texts):
    print('Original and demasked texts are identical:', old_text['text'] == new_text)
		