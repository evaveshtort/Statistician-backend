from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('cardpictures', image_name, file_object, file_object.size)
        return f"http://localhost:9000/cardpictures/{image_name}"
    except Exception as e:
        return {"error": str(e)}

def add_pic(new_metric, pic):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
           access_key=settings.AWS_ACCESS_KEY_ID,
           secret_key=settings.AWS_SECRET_ACCESS_KEY,
           secure=settings.MINIO_USE_SSL
    )
    code = new_metric.metric_code
    i = new_metric.metric_id
    img_obj_name = f"{code}" + '_' + f"{i}.png"

    if not pic:
        return Response({"error": "Нет файла для изображения метрики."})
    result = process_file_upload(pic, client, img_obj_name)

    if 'error' in result:
        return Response(result)

    new_metric.picture_url = result
    new_metric.save()

    return Response({"message": "success"})

def delete_pic(metric):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            secure=settings.MINIO_USE_SSL
    )

    code = metric.metric_code
    i = metric.metric_id
    img_name = f"{code}" + '_' + f"{i}.png"
    try:
        client.remove_object('cardpictures', img_name)
        return Response({"message": "success"})
    except Exception as e:
        return Response({"error": str(e)})