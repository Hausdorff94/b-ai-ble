import json
import boto3
import logging
import os
from IPython import display
from base64 import b64decode
import base64

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

def generate_ai_text(
    bedrock_runtime: any,
    customer_input: str,
    prompt: str,
    modelId: str = "meta.llama2-13b-chat-v1",
    accept: str = "application/json",
    contentType: str = "application/json",
    temperature: float = 0.9,
    top_p: float = 0.9,
    max_gen_len: int = 512
):
    final_prompt = f"""{customer_input}. {prompt}."""

    body = json.dumps(
        {
            "prompt": final_prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_gen_len": max_gen_len
        }
    )
    response = bedrock_runtime.invoke_model(
        body=body,
        modelId=modelId,
        accept=accept,
        contentType=contentType
    )
    response_body = json.loads(response.get("body").read())
    model_response = response_body.get("generation")
    list_response = [
        s.strip() for s in (
            list(filter(None, model_response.splitlines()))[:-1]
        )
    ]
    return model_response, list_response

def save_base64_image(
    base64_string: str,
    output_path: str = './data/',
    seed: int = None
    ):

    # Decode base64 string into bytes
    image_bytes = base64.b64decode(base64_string)

    # Write the bytes to a file

    with open(f"{output_path}output_image_{seed}.png", 'wb') as f:
        f.write(image_bytes)

def generate_ai_image(
    bedrock_runtime: any,
    style: str,
    verse: str = "",
    modelId: str = "stability.stable-diffusion-xl",
    style_preset: str = "photographic",
    negative_prompt: str = "",
    weight: float = 1.0,
    cfg_scale: int = 10,
    seed: int = 9936,
    steps: int = 70,
    width: int = 512,
    height: int = 512
):
    os.makedirs("data", exist_ok=True)
    if len(style) > 0:
        request = json.dumps(
            {
                "text_prompts": (
                    [
                        {
                            "text": f"""
                                        A scene of {style}
                                    """,
                            "weight": weight
                        },
                        {
                            "text": f"""
                                    A scene of {negative_prompt}
                                    """,
                            "weight": -10
                        }
                    ]
                ),
                "cfg_scale": cfg_scale,
                "seed": seed,
                "steps": steps,
                "style_preset": style_preset,
                "height": height
            }
        )
        response = bedrock_runtime.invoke_model(
            body=request,
            modelId=modelId
        )
        response_body = json.loads(
            response.get("body").read()
        )
        base_64_img_str = response_body["artifacts"][0].get("base64")
        display.display(
            display.Image(
                b64decode(base_64_img_str),
                width=width
            )
        )
        save_base64_image(base_64_img_str, seed=seed)