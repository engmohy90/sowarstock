from django.conf import settings
from django.core.files.base import ContentFile
from boto.s3.connection import S3Connection, Bucket, Key
from PIL import Image, ExifTags
from io import BytesIO
import requests
import uuid
import os

from . import models

THUMBNAIL_WIDTH = 500
THUMBNAIL_HEIGHT = 200

def image_file_from_url(url):
    response = requests.get(url)
    base_image = Image.open(BytesIO(response.content))
    return base_image


def remove_profile_image(user):
    S3_BUCKET = settings.S3_BUCKET
    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    url_list1 = user.profile_image_url.split("/")
    filename1 = url_list1[len(url_list1)-1]
    url_list2 = user.profile_image_crop.url.split("/")
    filename2 = url_list2[len(url_list2) - 1]

    b = Bucket(conn, S3_BUCKET)

    k = Key(b)

    k.key = 'profile_images/' + filename1

    b.delete_key(k)

    k.key = 'profile_images/crop/' + filename2

    b.delete_key(k)

    user.profile_image_url = None
    user.profile_image_crop = None
    user.save()


def crop_profile_image(user):
    base_image = image_file_from_url(user.profile_image_url)
    width, height = base_image.size
    if width == height:
        cropped = base_image
    else:
        cropped = base_image.crop((0,0,width,width))
    img_io = BytesIO()
    cropped.save(img_io, format="PNG", quality=100)
    name = uuid.uuid4()
    base_image_content = ContentFile(img_io.getvalue(), '{}.png'.format(name))
    user.profile_image_crop = base_image_content
    user.save()



def create_watermarked_image(product):
    if product.file_type == "jpeg/tiff":
        response = requests.get(product.image_url)
        base_image = Image.open(BytesIO(response.content))
    else:
        response = requests.get(product.file_url)
        base_image = Image.open(BytesIO(response.content))
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
    response = requests.get(sample_product.image_url)
    base_image = Image.open(BytesIO(response.content))

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
