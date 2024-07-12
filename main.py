import boto3
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Obtém as variáveis do arquivo .env
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
SOURCE_PHOTO = os.getenv('SOURCE_PHOTO')
TARGET_PHOTO = os.getenv('TARGET_PHOTO')

def compare_faces(source_photo, target_photo, bucket):
    """
    Compara duas imagens para verificar se elas contêm a mesma pessoa.
    :param source_photo: Nome da imagem fonte no S3.
    :param target_photo: Nome da imagem alvo no S3.
    :param bucket: Nome do bucket S3.
    """
    client = boto3.client('rekognition', region_name=AWS_REGION)  # Cria um cliente do Rekognition

    # Chama a API compare_faces do Rekognition para comparar as duas imagens
    response = client.compare_faces(
        SourceImage={
            'S3Object': {
                'Bucket': bucket,
                'Name': source_photo
            }
        },
        TargetImage={
            'S3Object': {
                'Bucket': bucket,
                'Name': target_photo
            }
        },
        SimilarityThreshold=90  # Define o limiar de similaridade para 90%
    )

    # Itera sobre as correspondências de rostos encontradas
    for faceMatch in response['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']  # Pega a posição do rosto
        similarity = str(faceMatch['Similarity'])  # Pega a similaridade do rosto

        # Imprime a posição e a similaridade do rosto encontrado
        print(f'The face at {position["Left"]} {position["Top"]} matches with {similarity}% similarity')

    # Se não houver correspondências de rostos, imprime uma mensagem
    if not response['FaceMatches']:
        print('No faces matched')

def upload_image_to_s3(file_path, bucket, object_name):
    """
    Faz o upload de uma imagem para um bucket S3.
    :param file_path: Caminho local do arquivo a ser enviado.
    :param bucket: Nome do bucket S3.
    :param object_name: Nome do objeto no S3 após o upload.
    """
    s3_client = boto3.client('s3', region_name=AWS_REGION)  # Cria um cliente do S3
    try:
        # Tenta fazer o upload do arquivo para o S3
        s3_client.upload_file(file_path, bucket, object_name)
        print(f'File {file_path} uploaded to {bucket}/{object_name}')
    except Exception as e:
        # Se ocorrer um erro, imprime a mensagem de erro
        print(f'Error uploading file: {e}')

def main():
    """
    Função principal do script.
    Faz o upload das imagens fonte e alvo para o S3 e compara os rostos nas duas imagens.
    """
    source_photo_path = f'images/{SOURCE_PHOTO}'  # Caminho local da imagem fonte
    target_photo_path = f'images/{TARGET_PHOTO}'  # Caminho local da imagem alvo

    # Faz o upload das imagens fonte e alvo para o S3
    upload_image_to_s3(source_photo_path, S3_BUCKET_NAME, SOURCE_PHOTO)
    upload_image_to_s3(target_photo_path, S3_BUCKET_NAME, TARGET_PHOTO)

    # Compara os rostos nas duas imagens
    compare_faces(SOURCE_PHOTO, TARGET_PHOTO, S3_BUCKET_NAME)

if __name__ == "__main__":
    main()  # Executa a função principal quando o script é executado diretamente
