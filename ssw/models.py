from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import uuid
from easy_thumbnails.fields import ThumbnailerImageField
from mimetypes import MimeTypes

# Create your models here.

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class Address(models.Model):
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)

    def __str__(self):
        return self.address1


class SowarStockUser(User):
    USER_TYPES = (("contributor", "Contributor"),("client", "Client"),
                  ("admin", "Admin"),("image_reviewer", "Image Reviewer"),
                  ("financial_admin", "Financial Admin"))
    LANGUAGES = (("en", "English"),("ar", "Arabic"))
    FORGOT_PASSWORD_STATUSES = (("none", "None"),("not_used", "Not Used"), ("used", "Used"))
    type = models.CharField(max_length=255, choices=USER_TYPES)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    preferred_language = models.CharField(max_length=2, choices=LANGUAGES, null=True, blank=True)
    email_verification_code = models.UUIDField(default=uuid.uuid4)
    email_verified = models.BooleanField(default=False)
    forgot_password_verification = models.UUIDField(null=True, blank=True, unique=True)
    forgot_password_status = models.CharField(max_length=255, default="none", choices=FORGOT_PASSWORD_STATUSES)
    address = models.OneToOneField(Address, on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    class Meta:
        verbose_name = "Sowar Stock User"


class Contributor(SowarStockUser):
    ACCOUNT_STATUS = (("unverified", "Unverified"), ("verified", "Verified"))
    status = models.CharField(max_length=255, choices=ACCOUNT_STATUS)
    photo_id = models.FileField(upload_to='photo_id/', null=True, blank=True)
    photo_id_verified = models.BooleanField(default=False)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    portfolio_url = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=255, null=True, blank=True)

    def is_verified(self):
        return self.address and self.email_verified and self.photo_id_verified

    class Meta:
        verbose_name = "Contributor User"


class Client(SowarStockUser):

    def is_verified(self):
        return self.email_verified

    class Meta:
        verbose_name = "Client User"


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categorie"


class SubCategory(models.Model):
    name = models.CharField(max_length=255)
    main_category = models.ManyToManyField(Category)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sub Categorie"


class Product(models.Model):
    ADMIN_STATUS_OPTIONS = (("pending_approval", "Pending Approval"),
                            ("pending_admin_approval", "Pending Admin Approval"),
                            ("approved", "Approved"), ("rejected", "Rejected"))
    REJECTION_REASON_OPTIONS = (("title_description", "Title/Description"), ("size_resolution", "Size and/or Resolution"),
                                ("trademark_copyright", "Trademark and/or Copyright"), ("lighting_exposure", "Lighting and/or Expusure"),
                                ("noise_artifact", "Noise, Artifact, and/or Film Grain"), ("focus", "Focus"),
                                ("farming_cropping", "Framing, Cropping, and/or Composition"), ("camera_sensor","Camera Sensor Dirt/Spot"),
                                ("overuse_noise", "Overuse of Noise Reduction"), ("over_editing", "Over-editing"),
                                ("lens_problems","Lens Problems (as Purple or Fringing)"), ("similar_submissions", "Similar Submissions"),
                                ("limited_commercial_value", "Limited Commercial Value"), ("keywords", "Keywords"),
                                ("other", "Other"))
    FILE_TYPE_OPTIONS = (("jpeg", "JPEG"), ("eps", "EPS"))
    public_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    file_type = models.CharField(max_length=255, default="jpeg", choices=FILE_TYPE_OPTIONS)
    image = ThumbnailerImageField(upload_to='products/', null=True, blank=True)
    eps_image = ThumbnailerImageField(upload_to='products/', null=True, blank=True)
    file = models.FileField(upload_to='products/', null=True, blank=True)
    watermark = ThumbnailerImageField(upload_to='products/watermarked/', null=True, blank=True)
    released = models.BooleanField(default=False)
    exclusive = models.BooleanField(default=False)
    status = models.CharField(max_length=255, choices=ADMIN_STATUS_OPTIONS, default="pending_approval")
    rejection_reason = models.CharField(max_length=255, null=True, blank=True, choices=REJECTION_REASON_OPTIONS)
    rejection_note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #keywords = ListCharField(base_field=models.CharField(max_length=255), max_length = 10)
    keywords = models.CharField(max_length=255, blank=False, null=False)
    category = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, blank=True,null=True, on_delete=models.CASCADE)
    standard_price = models.IntegerField(default=15)
    extended_price = models.IntegerField(default=149)
    owner = models.ForeignKey(Contributor, on_delete=models.CASCADE)

    def get_display_image(self):
        if self.file_type == "jpeg":
            return self.image
        else:
            return self.eps_image

    def product_size(self):
        if self.file_type == "jpeg":
            return sizeof_fmt(self.image.size)
        else:
            return sizeof_fmt(self.file.size)

    def is_photo(self):
        return self.category.name == "Photos"

    def is_vector(self):
        return self.category.name == "Vectors and Paintings"

    def is_calligraphy(self):
        return self.category.name == "Calligraphy"

    def __str__(self):
        return "{} by {}".format(self.title,self.owner.username)

    def clean(self):
        file_type = self.file_type
        if file_type == "jpeg":
            image_size = self.image.size
            base_image = Image.open(self.image)
            image_width = base_image.width
            image_height = base_image.height
            image_size_in_megapixels = (image_width * image_height) / 1000000
            image_format = base_image.format
            if image_format != "JPEG":
                raise ValidationError(_('Image format has to be only JPEG'))
            if image_size > 52428800:  # 50 MB
                raise ValidationError(_('Image size has to be less than 50 MB'))
            if image_size_in_megapixels < 4:
                raise ValidationError(_('Image has to be at least 4 Megapixels'))
            pass
        else:
            file_size = self.file.size
            mime = MimeTypes()
            mime_type = mime.guess_type(self.file.url)
            if mime_type[0] != "application/postscript":
                raise ValidationError(_('Format is not EPS'))
            if file_size > 15728640:  # 15 MB
                raise ValidationError(_('File size has to be less than 15 MB'))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Product, self).save(*args, **kwargs)


class Collection(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    owner = models.ForeignKey(Contributor, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    comment = models.TextField(null=False, blank=False)
    owner = models.ForeignKey(SowarStockUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment


class Faq(models.Model):
    question = models.TextField(blank=False, null = False)
    answer = models.TextField(blank=False, null = False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question


class FaqPersonal(models.Model):
    question = models.TextField(blank=False, null=False)
    answer = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name="owner")
    replier = models.ForeignKey(SowarStockUser, on_delete=models.PROTECT, null=True, blank=True, related_name="replier")

    def __str__(self):
        return self.question


class UserRequest(models.Model):
    STATUS_OPTIONS = (("pending_approval", "Pending Approval"), ("approved", "Approved"), ("rejected", "Rejected"))
    body = models.CharField(max_length=255, default="pending_approval")
    status = models.CharField(max_length=255, choices=STATUS_OPTIONS, default="pending_approval")
    owner = models.ForeignKey(Contributor, on_delete=models.CASCADE)

    def __str__(self):
        return self.owner.username


class ShoppingCart(models.Model):
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total(self):
        t = 0
        if self.shoppingcartitem_set.all():
            for item in self.shoppingcartitem_set.all():
                if item.status == "in_cart":
                    t += item.price()
        return t

    def __str__(self):
        return self.owner.username


class ShoppingCartItem(models.Model):
    LICENSE_OPTIONS = (("standard", "Standard"), ("extended", "Extended"))
    STATUS_OPTIONS = (("in_cart", "In Cart"), ("removed", "Removed"), ("purchased", "Purchased"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    license_type = models.CharField(max_length=255, choices=LICENSE_OPTIONS)
    status = models.CharField(max_length=255, choices=STATUS_OPTIONS, default="in_cart")
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title + " | " + self.cart.owner.username

    def price(self):
        if self.license_type == "standard":
            return self.product.standard_price
        else:
            return self.product.extended_price


class Order(models.Model):
    order_no = models.IntegerField(unique=True)
    total = models.IntegerField()
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.order_no)


class OrderItem(models.Model):
    price = models.DecimalField(max_digits=5, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="product")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orderitem")
    shopping_cart_item = models.ForeignKey(ShoppingCartItem, on_delete=models.PROTECT, related_name="shopping_cart_item")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} | {}".format(self.product.title,self.order.order_no)


class LegalDocument(models.Model):
    title = models.CharField(max_length=255)
    document = models.FileField(upload_to='legal/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Featured(models.Model):
    TYPE_OPTIONS = (("slider", "Slider"), ("contributors", "Contributors"), ("featured", "Featured"))
    type = models.CharField(max_length=255, choices=TYPE_OPTIONS)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    contributor = models.ForeignKey(Contributor, on_delete=models.PROTECT, null=True, blank=True)
    image = ThumbnailerImageField(upload_to='featured/', null=True, blank=True)


class Earning(models.Model):
    TYPE_OPTIONS = (("contributor", "Contributor"), ("sowarstock", "SowarStock"))
    type = models.CharField(max_length=255, choices=TYPE_OPTIONS)
    order_item = models.ForeignKey(OrderItem, on_delete=models.PROTECT)
    contributor = models.ForeignKey(Contributor, on_delete=models.PROTECT, null=True, blank=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2)


    def __str__(self):
        return "${} to {} for order {}".format(self.amount, self.type, self.order_item)


class Payment(models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    contributor = models.ForeignKey(Contributor, on_delete=models.PROTECT)
    receipt = models.FileField(upload_to='payments/')
    earning = models.OneToOneField(Earning, on_delete=models.PROTECT)

    def __str__(self):
        return "${} to {}".format(self.amount, self.contributor)
