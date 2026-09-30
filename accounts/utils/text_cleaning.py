import re
import emoji

def clean_text(text):
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = emoji.replace_emoji(text, replace='')
    text = re.sub(r"[^a-zA-Z\s]", '', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()

    return text
