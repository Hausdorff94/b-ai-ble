import json
import boto3
import logging

logging.basicConfig(filename='utils.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

def write_to_json(data, filename):
    with open(filename, "w") as outfile:
        json.dump(data, outfile)

def read_json_from_s3(bucket_name, object_key):
    """
    Read a JSON file from Amazon S3.

    Args:
        bucket_name (str): Name of the Amazon S3 bucket.
        object_key (str): Key (path) of the JSON file in S3.

    Returns:
        dict: Dictionary containing the JSON data.
    """
    # Initialize the S3 client
    s3 = boto3.client('s3')

    try:
        # Get the JSON file object from S3
        response = s3.get_object(Bucket=bucket_name, Key=object_key)

        # Read the contents of the JSON file
        json_data = response['Body'].read()

        # Parse the JSON data
        json_dict = json.loads(json_data)

        return json_dict
    except Exception as e:
        print(f"Error reading JSON file from S3: {str(e)}")
        return None

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

import boto3

def list_directories(bucket_name, prefix):
    """
    List directories (prefixes) within a specific directory (prefix) in an S3 bucket.

    Args:
        bucket_name (str): Name of the Amazon S3 bucket.
        prefix (str): Prefix of the directory (folder) in S3.

    Returns:
        list: List of directory names (prefixes) within the specified prefix in S3.
    """
    # Initialize the S3 client
    s3 = boto3.client('s3')

    try:
        # List objects within the specified prefix
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')

        # Extract directory names (prefixes) from the response
        directories = [prefix['Prefix'] for prefix in response.get('CommonPrefixes', [])]

        return directories
    except Exception as e:
        print(f"Error listing directories in S3: {str(e)}")
        return []

import boto3

def list_files(bucket_name, prefix=''):
    """
    List files (objects) within a specific directory (prefix) in an S3 bucket.

    Args:
        bucket_name (str): Name of the Amazon S3 bucket.
        prefix (str, optional): Prefix of the directory (folder) in S3. Defaults to ''.

    Returns:
        list: List of file names (keys) within the specified prefix in S3.
    """
    # Initialize the S3 client
    s3 = boto3.client('s3')

    try:
        # List objects within the specified prefix
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        # Extract file names (keys) from the response
        files = [obj['Key'] for obj in response.get('Contents', [])]

        return files
    except Exception as e:
        print(f"Error listing files in S3: {str(e)}")
        return []