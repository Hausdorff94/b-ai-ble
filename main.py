import requests
import boto3
import json
import os
import logging

# logger config

logging.basicConfig(filename='bible.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

bible_verion_id = "es-bes"
bible_book = "genesis"
bible_chapter = 1
bible_verse = 1



# books_es = {
#     "génesis", "éxodo", "levítico", "números", "deuteronomio", "josué", "jueces",
#     "rut", "1samuel", "2samuel", "1reyes", "2reyes", "1crónicas", "2crónicas", 
#     "esdras", "nehemías", "ester", "job", "salmos", "proverbios", "eclesiastés",
#     "cantares", "isaías", "jeremías", "lamentaciones", "ezequiel", "daniel",
#     "oseas", "joel", "amós", "abdías", "jonás", "miqueas", "nahum", "habacuc",
#     "sofonías", "hageo", "zacarías", "malaquías", "mateo", "marcos", "lucas",
#     "juan", "hechos", "romanos", "1corintios", "2corintios", "gálatas", "efesios",
#     "filipenses", "colosenses", "1tesalonicenses", "2tesalonicenses", "1timoteo",
#     "2timoteo", "tito", "filemón", "hebreos", "santiago", "1pedro", "2pedro",
#     "1juan", "2juan", "3juan", "judas", "apocalipsis"
# }

books_es = {
    "génesis", "éxodo", "levítico", "números", "deuteronomio", "josué", "jueces",
    "rut", "1samuel", "2samuel", "1reyes", "2reyes", "1crónicas", "2crónicas", 
    "esdras", "nehemías", "ester", "job", "salmos", "proverbios", "eclesiastés",
    "cantares", "isaías", "jeremías", "lamentaciones", "ezequiel", "daniel",
    "oseas", "joel", "amós", "abdías", "jonás", "miqueas", "nahum", "habacuc",
    "sofonías", "hageo", "zacarías", "malaquías", "mateo", "marcos", "lucas",
    "juan", "hechos", "romanos", "2corintios", "gálatas", "efesios",
    "filipenses", "colosenses", "1tesalonicenses", "2tesalonicenses", "1timoteo",
    "2timoteo", "tito", "filemón", "hebreos", "santiago", "1pedro", "2pedro",
    "1juan", "2juan", "3juan", "judas", "apocalipsis"
}


def upload_to_s3(file_path, bucket_name, prefix):
    """
    Carga un archivo a un bucket de Amazon S3.

    Args:
        file_path (str): Ruta local del archivo que se va a cargar.
        bucket_name (str): Nombre del bucket de Amazon S3.
        prefix (str): Nombre del objeto en S3.

    Returns:
        bool: True si la carga fue exitosa, False en caso contrario.
    """
    # Inicializa el cliente de S3
    s3 = boto3.client('s3')

    try:
        # load to s3 bucket
        s3.upload_file(file_path, bucket_name, prefix)
        logger.info(f"File '{prefix}' uploaded to '{bucket_name}'")
        return True
    except Exception as e:
        logger.error(f"Error uploading file '{prefix}' to '{bucket_name}': {e}")
        return False

def get_verse(book_dict, bible_verion_id: str = "es-bes"):
    for book, ch in book_dict.items():
        for ch in range(1, ch+1):
            bible_chapter = ch
            for verse in range(1, 250):
                bible_verse = verse
                endpoint = f"https://cdn.jsdelivr.net/gh/wldeh/bible-api/bibles/{bible_verion_id}/books/{book}/chapters/{bible_chapter}/verses/{bible_verse}.json"
                try:
                    response = requests.get(endpoint)
                    data = response.json()
                    data = {"verse": data["text"]}
                    file_name_s3 = f"{bible_verion_id}/book={book}/chapter={bible_chapter}/verse={bible_verse}/{bible_verse}.json"
                    print(endpoint)
                    write_to_json(data, 'data.json')
                    upload_to_s3('data.json', "bible-289269610742", file_name_s3)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    break
        

def write_to_json(data, filename):
    with open(filename, "w") as outfile:
        json.dump(data, outfile)






if __name__ == "__main__":
    #Verify if the file chatpters_number.json exists usin os library
    if not os.path.exists("books_ch_es.json"):
        logger.info("The file books_ch_es.json does not exist")
        books_ch_es = dict()
        for book in books_es:
            for ch in range(1, 250):
                bible_chapter = ch
                endpoint = f"https://cdn.jsdelivr.net/gh/wldeh/bible-api/bibles/{bible_verion_id}/books/{book}/chapters/{bible_chapter}/verses/{bible_verse}.json"
                try:
                    response = requests.get(endpoint)
                    data = response.json()
                    print("Success ", book, bible_chapter, bible_verse, data)
                except:
                    logger.error(f"Error {book} {bible_chapter} {bible_verse}")
                    print("Error ", book, bible_chapter, bible_verse)
                    break

            books_ch_es[book] = ch - 1

        # chapters_number to json
        with open("books_ch_es.json", "w") as outfile:
            json.dump(books_ch_es, outfile)

    # Load the chapters_number.json file
            
    with open("books_ch_es.json", "r") as infile:
        books_ch_es = json.load(infile)

    logger.info("books_ch_es.json loaded")
    get_verse(books_ch_es)

    # file_path = 'ruta/al/archivo/a/cargar.txt'
    # bucket_name = 'nombre-del-bucket'
    # object_name = 'nombre-del-archivo-en-s3.txt'

    # upload_to_s3(file_path, bucket_name, object_name)