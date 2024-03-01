from utils.utils import (
    read_json_from_s3,
    list_directories,
    upload_to_s3,
    list_files,
    write_to_json,
    generate_ai_text)

from utils_br import bedrock
import os


def set_environment():
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    # os.environ["AWS_PROFILE"] = ""
    os.environ["BEDROCK_ASSUME_ROLE"] = ""  # E.g. "arn:aws:..."

    bedrock_runtime = bedrock.get_bedrock_client(
        assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
        region=os.environ.get("AWS_DEFAULT_REGION", None))
    return bedrock_runtime

def translate_verse(verse: str, bedrock_runtime: any):
    customer_input = """
    You're an expert translator from spanish to english
    """
    prompt = f"""
    Without adding any content, simply translate the following verse
    [VERSE]
    {verse}
    [/VERSE]

    Your response is only the flag <translated> , for example:

    [EXAMPLE]
    - original: Mi nombre es Juan
    - <translated>: My name is John
    Response: My name is John

    - original: Buenos días
    - <translated>: Good morning
    Response: Good morning
    [/EXAMPLE]
    """
    model_response, list_response = generate_ai_text(bedrock_runtime,customer_input, prompt, temperature=0)
    verse_en = model_response.split('[VERSE]')[-1][:-8].strip()
    return verse_en

def create_scene(verse_en, bedrock_runtime: any):
    customer_input = """
    You're an expert on the Christian Bible, with an unparalleled command of its intricate narratives, deep symbolism and theological nuance,
    Through your expertise, you breathe life into ancient stories
    """
    prompt = f"""
    Describe one scene for the following verse:
    [VERSE]
    {verse_en}
    [/VERSE]

    Follow the examples to write the scene using the above verse.

    [EXAMPLES]

    [VERSE]
    David and Goliat
    [/VERSE]
    - <SCENE>: David killed to Goliat. He's stand up on the desert, all trops are screaming.
    - Response: David killed to Goliat. He's stand up on the desert, all trops are screaming.

    [VERSE]
    Moises in Egypt
    [/VERSE]
    - <SCENE>: Moises is walking around the city. He's looking for his brother
    - Response: Moises is walking around the city. He's looking for his brother
    [/EXAMPLES]
    """
    
    model_response, list_response = generate_ai_text(bedrock_runtime,customer_input, prompt, temperature=0.8)
    scene_splited = model_response.split('<SCENE>:')
    
    while len(scene_splited) < 2:
        model_response, list_response = generate_ai_text(bedrock_runtime,customer_input, prompt, temperature=0.8)
        scene_splited = model_response.split('<SCENE>:')

    scene = scene_splited[-1].strip()
    return scene

def main():
    bucket_name = 'bibleapi-289269610742'
    root_prefix = 'es-bes/books/'
    bedrock_runtime = set_environment()

    books = list_directories(bucket_name, root_prefix)
    for book in books:
        book = book.split('/')[-2]
        chapter_prefix = f'{root_prefix}{book}/chapters/'
        chapters = list_directories(bucket_name, chapter_prefix)
        for chapter in chapters:
            chapter = chapter.split('/')[-2]
            verse_prefix = f'{chapter_prefix}{chapter}/verses/'
            verses = list_files(bucket_name, verse_prefix)
            for verse in verses:
                json_data = read_json_from_s3(bucket_name, verse)
                if json_data:
                    text = json_data['text']
                    verse_en = translate_verse(text, bedrock_runtime)
                    scene = create_scene(verse_en, bedrock_runtime)
                    verse_json = {
                        "scene": scene
                    }
                    write_to_json(verse_json, 'data.json')
                    verse = verse.replace('es-bes', 'es-bes_scenes_txt')
                    upload_to_s3(
                        'data.json',
                        bucket_name,
                        verse)
