from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

import uuid
import os
import requests


def create_watermarked_image(product):
    if product.file_type == "jpeg":
        base_image = Image.open(product.image)
    else:
        base_image = Image.open(product.eps_image)
    response = requests.get(settings.MEDIA_URL + "watermarks/Single_Logo_White_60.png")
    #response = requests.get("https://s3.amazonaws.com/sowarstock/watermarks/Single_Logo_White_60.png")
    watermark = Image.open(BytesIO(response.content))
    wwidth, wheight = watermark.size
    width, height = base_image.size
    offset = ((width - wwidth) // 2, (height - wheight) // 2)

    transparent = Image.new('RGBA', (width, height), (0,0,0,0))
    transparent.paste(base_image, (0,0))
    transparent.paste(watermark, offset, mask=watermark)
    watermarked_name = uuid.uuid4()
    img_io = BytesIO()
    transparent.save(img_io, format='PNG', quality=100)
    img_content = ContentFile(img_io.getvalue(), '{}.png'.format(watermarked_name))
    product.watermark = img_content
    product.save()


def eps_to_jpeg(product):
    new_name = uuid.uuid4() + "." + "jpeg"
    os.system("magick {}{} {}{}".format(settings.MEDIA_ROOT, product.file, settings.MEDIA_ROOT, new_name))
    product.image = new_name
    product.save()
