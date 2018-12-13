from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ExifTags
from io import BytesIO

import uuid
import os

from . import models

THUMBNAIL_WIDTH = 500
THUMBNAIL_HEIGHT = 200

def create_watermarked_image(product):
    if product.file_type == "jpeg/tiff":
        base_image = Image.open(product.image)
    else:
        base_image = Image.open(product.eps_image)
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation': break
    try:
        exif = dict(base_image._getexif().items())
        if exif:
            if exif[orientation]:
                if exif[orientation] == 3:
                    base_image = base_image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    base_image = base_image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    base_image = base_image.rotate(90, expand=True)
    except:
        print("no exif for this product")
    site_settings = models.SiteSettings.objects.get(pk=1)
    #response = requests.get("https://s3.amazonaws.com/sowarstock/watermarks/logo_white_400w.png")
    #watermark = Image.open(BytesIO(response.content))
    watermark = Image.open(site_settings.watermark)
    wwidth, wheight = watermark.size
    thumbnail_img_io = BytesIO()
    watermark_img_io = BytesIO()


    ## CREATE THUMBNAIL ##
    width, height = base_image.size
    ratio = height / width
    thumbnail_height = int(round(THUMBNAIL_WIDTH*ratio))
    base_image.thumbnail((THUMBNAIL_WIDTH, thumbnail_height))
    thumbnail_name = uuid.uuid4()
    base_image.save(thumbnail_img_io, format="PNG", quality=100)
    base_image_content = ContentFile(thumbnail_img_io.getvalue(), '{}.png'.format(thumbnail_name))
    product.thumbnail = base_image_content
    product.save()


    ## CREATE WATERMARK ##
    offset = ((base_image.width - wwidth) // 2, (base_image.height - wheight) // 2)

    transparent = Image.new('RGBA', (base_image.width, base_image.height), (0,0,0,0))
    transparent.paste(base_image, (0,0))
    transparent.paste(watermark, offset, mask=watermark)
    watermarked_name = uuid.uuid4()

    transparent.save(watermark_img_io, format='PNG', quality=100)
    watermark_img_content = ContentFile(watermark_img_io.getvalue(), '{}.png'.format(watermarked_name))
    product.watermark = watermark_img_content
    product.save()



def create_thumbnailed_image(sample_product):
    base_image = Image.open(sample_product.image)
    img_io = BytesIO()
    width, height = base_image.size
    ratio = height / width
    thumbnail_height = int(round(THUMBNAIL_WIDTH * ratio))
    base_image.thumbnail((THUMBNAIL_WIDTH, thumbnail_height))
    thumbnail_name = uuid.uuid4()
    base_image.save(img_io, format="PNG", quality=100)
    base_image_content = ContentFile(img_io.getvalue(), '{}.png'.format(thumbnail_name))
    sample_product.thumbnail = base_image_content
    sample_product.save()


def eps_to_jpeg(product):
    new_name = uuid.uuid4() + "." + "jpeg"
    os.system("magick {}{} {}{}".format(settings.MEDIA_ROOT, product.file, settings.MEDIA_ROOT, new_name))
    product.image = new_name
    product.save()
