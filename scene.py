from utils.utils import (
    read_json_from_s3,
    list_directories,
    upload_to_s3,
    list_files,
    write_to_json)

# Example usage:
if __name__ == "__main__":
    bucket_name = 'bibleapi-289269610742'
    root_prefix = 'es-bes/books/'

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
                    verse_json = {
                        "scene": text
                    }
                    write_to_json(verse_json, 'data.json')
                    verse = verse.replace('es-bes', 'es-bes_scenes_txt')
                    upload_to_s3(
                        'data.json',
                        bucket_name,
                        verse)
