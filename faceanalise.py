import boto3
import json

s3 = boto3.resource('s3')
client = boto3.client('rekognition')

def detecta_faces():
        detecetadas = client.index_faces(
            CollectionId='faceslimao',
            DetectionAttributes =['DEFAULT'],
            ExternalImageId='TEMP',
            Image={
                'S3Object': {
                'Bucket': 'fa-imagens-limao',
                'Name': '_analise.png',
            },
        },
    )
        return detecetadas

def cria_lista_faceId_detectadas(detecetadas):
    faceId_detectadas = []
    for imagem in range(len(detecetadas['FaceRecords'])):
        faceId_detectadas.append(detecetadas['FaceRecords'][imagem]['Face']['FaceId'])
    return faceId_detectadas

def compara_imagens(faceId_detectadas):
    result = []
    for i in faceId_detectadas:
        result.append(
        client.search_faces(
            CollectionId='faceslimao',
            FaceId=i,
            FaceMatchThreshold=80,
            MaxFaces=10,
    )
)
        return result

def gera_dados_json(result):
    dados_json =[]
    for face in result:
        if (len(face.get('FaceMatches')))>=1:
            perfil = dict(nome=face['FaceMatches'][0]['Face']['ExternalImageId'],
                          faceMatch=round(face['FaceMatches'][0]['Similarity'],2))
            dados_json.append(perfil)
    return dados_json

def publica_dados(dados_json):
    arquivo = s3.Object('fa-resultado-limao','dados.json')
    arquivo.put(Body=json.dumps(dados_json))

def exclui_imagem_colecao(faceId_detectadas):
    client.delete_faces(
        CollectionId='faceslimao',
        FaceIds=faceId_detectadas,
    )

def main(event, context):
    detecetadas = detecta_faces()
    faceId_detectadas = cria_lista_faceId_detectadas(detecetadas)
    result = compara_imagens(faceId_detectadas)
    dados_json = gera_dados_json(result)
    publica_dados(dados_json)
    exclui_imagem_colecao(faceId_detectadas)
    print(json.dumps(dados_json, indent=4))





