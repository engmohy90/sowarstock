from django.db import models
from django.contrib.auth.models import User
import uuid
from easy_thumbnails.fields import ThumbnailerImageField

# Create your models here.

class Address(models.Model):
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    #owner = models.ForeignKey(SowarStockUser, on_delete=models.CASCADE)
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

    def is_verified(self):
        return self.address and self.email_verified and self.photo_id_verified

    class Meta:
        verbose_name = "Contributor User"

class Client(SowarStockUser):
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
    ADMIN_STATUS_OPTIONS = (("pending_approval", "Pending Approval"),("pending_admin_approval", "Pending Admin Approval"),("approved", "Approved"), ("rejected", "Rejected"))
    public_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    image = ThumbnailerImageField(upload_to='products/', null=False)
    released = models.BooleanField(default=False)
    status = models.CharField(max_length=255, choices=ADMIN_STATUS_OPTIONS, default="pending_approval")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #keywords = ListCharField(base_field=models.CharField(max_length=255), max_length = 10)
    keywords = models.CharField(max_length=255)
    category = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, blank=True,null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(Contributor, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

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
            return 15
        else:
            return 149

class Order(models.Model):
    order_no = models.IntegerField(unique=True)
    total = models.IntegerField()
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.order_no)

class OrderItem(models.Model):
    price = models.IntegerField()
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