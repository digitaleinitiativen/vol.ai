import feedparser
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
import hashlib
import os
import json
import requests

# Set your OpenAI API key here

# Path to the file where we'll store the hashes of processed headlines
PROCESSED_HEADLINES_FILE = 'processed_headlines.json'

# Directory to save the images
IMAGE_SAVE_DIRECTORY = 'generated_images'

def load_processed_headlines():
    if os.path.exists(PROCESSED_HEADLINES_FILE):
        with open(PROCESSED_HEADLINES_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_processed_headlines(processed_headlines):
    with open(PROCESSED_HEADLINES_FILE, 'w') as file:
        json.dump(processed_headlines, file)

def generate_image(prompt):
    response = client.images.generate(prompt=prompt,
    model="dall-e-3",
    n=1,
    size="1792x1024")
    image_url = response.data[0].url
    return image_url

def text_prompt(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )
    return chat_completion.choices[0].message.content

def download_image(image_url, save_path):
    response = requests.get(image_url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

def main():

    # Ensure the image save directory exists
    if not os.path.exists(IMAGE_SAVE_DIRECTORY):
        os.makedirs(IMAGE_SAVE_DIRECTORY)

    # Load the list of processed headlines
    processed_headlines = load_processed_headlines()

    # URL of the vol.at RSS feed
    feed_url = 'https://www.vol.at/news/vorarlberg/feed?rss'
    source = "vol.at"

    if 1:
        feed_url = 'https://rss.orf.at/vorarlberg.xml'
        source = 'vorarlberg.orf.at'

    # Parse the RSS feed
    feed = feedparser.parse(feed_url)

    # Count of images generated
    image_count = 0
    max_images = 5

    # Iterate over the feed entries
    for entry in feed.entries:
        if image_count >= max_images:
            break
        
        headline = entry.title
        description = entry.description
        # Generate a unique hash for each headline
        headline_hash = hashlib.sha256(headline.encode()).hexdigest()

        if headline_hash in ['bb5b8b1d811b5d854ac8da42ffee5f4549b6cfd3f93282b0bee1b69d31e78111']:
            print(f'{headline_hash}: "{headline}" skipped')
            continue

        # Check if the headline has already been processed
        if headline_hash not in processed_headlines:
            answer = text_prompt(f'''Du bist der Autor eines Comics.
                                 Erstelle mir die Beschreibung des Coverbilds für ein Comic.
                                 Mit der Beschreibung will ich ein Comic im Retro-Comic-Stil erstellen.
                                 Das Comic soll zum Titel "{headline}" und zur Schilderung "{description}" passen.
                                 Verwende in der Beschreibung konkret Dinge die in Titel und Schilderung vorkommen.
                                 Die Hauptcharaktere sollen als Superhelden oder Dinosaurier dargstellt werden.
                                 Die Charaktere haben alle Körperformen (dünn, dick, klein, groß) vertreten alle Geschlechter und Ethnien. Sie können auch körperlich benachteiligt sein.
                                 Die Geschichte spielt an einem Strand.
                                 Weitere Elemente die vorkommen können sind Kokosnüsse, Luftmatratzen, Steinböcke, Palmen usw. Das ist aber optional.
                                 Sämtliche Texte auf dem Cover sollen in deutsch gehalten sein.
                                 ''')
            print(f'{headline_hash}: {headline}')
            print(f'{description}')
            print(f'{answer}')

            # Generate an image based on the headline
            image_url = generate_image(f'''Erstelle mir das Cover für ein deutsches Comic im Retro Stil, dass der folgenden Beschreibung folgt:
                                       {answer}
                                       ''')
            print(f'Generated image for headline "{headline}": {image_url}')

            # Download the image
            image_filename = f"{headline_hash}.png"
            image_path = os.path.join(IMAGE_SAVE_DIRECTORY, image_filename)
            download_image(image_url, image_path)
            print(f'Saved image to {image_path}')

            # Add the hash to the list of processed headlines
            processed_headlines[headline_hash] = {
                "title": headline,
                "description": description,
                "prompt": answer,
                "source": source,
                "link": entry.link,
                "time": entry.published

            }
            image_count += 1
            save_processed_headlines(processed_headlines)
        else:
            print(f'{headline_hash}: Headline "{headline}" already processed.')
        save_processed_headlines(processed_headlines)

if __name__ == '__main__':
    main()
