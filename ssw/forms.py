from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, PasswordInput, Textarea, ImageField, FileField
from django.forms.widgets import ClearableFileInput, Select, SelectMultiple, CheckboxSelectMultiple
from django.utils.translation import ugettext_lazy as _
from notifications.models import Notification

from . import models


class MyProfileImageFileInput(ClearableFileInput):
    initial_text = 'Current Profile Picture'
    input_text = 'Change'
    clear_checkbox_label = 'Delete'


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.', label=_('Email Address'))

    class Meta:
        model = models.SowarStockUser
        fields = ('username', 'email', 'password1', 'password2',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        models.SowarStockUser.objects.filter(email=email).count()
        if email and models.SowarStockUser.objects.filter(email=email).count() > 0:
            raise forms.ValidationError(_('This email address is already registered.'))
        return email


class ProfilePersonalInfoForm(ModelForm):

    class Meta:
        model = models.SowarStockUser
        fields = ["first_name", "last_name", "country_code", "phone", "preferred_language"]
        labels = {
            'country_code': _('Country Code'),
            'phone': _('Phone'),
            'preferred_language': _('Preferred Language')
        }


class ProfilePublicInfoForm(ModelForm):
    class Meta:
        model = models.Contributor
        fields = ["display_name", "job_title", "description", "portfolio_url"]
        labels = {
            'display_name': _('Display name'),
            'job_title': _('Job title'),
            'description': _('Description'),
            'portfolio_url': _('Portfolio url')
        }


class AddressForm(ModelForm):
    class Meta:
        model = models.Address
        fields = ["address1", "address2", "city", "state","country", "zipcode"]
        labels = {
            'address1': _('Address 1'),
            'address2': _('Address 2'),
            'city': _('City'),
            'state': _('State'),
            'country': _('Country'),
            'zipcode': _('Zip Code'),
        }


class PhotoIdForm(ModelForm):
    class Meta:
        model = models.Contributor
        fields = ["photo_id"]


class PaymentMethodForm(ModelForm):
    class Meta:
        model = models.Contributor
        fields = ["preferred_payment_method", "bank_owner_name", "iban", "bank_name", "bank_country",
                  "western_union_account", "residency_country", "paypal_account"]
        labels = {
            'preferred_payment_method': _('Preferred payment method'),
            'bank_owner_name': _('Bank owner name'),
            'iban': _('IBAN'),
            'bank_name': _('Bank name'),
            'bank_country': _('Bank country'),
            'western_union_account': _('Western union account'),
            'residency_country': _('Residency country'),
            'paypal_account': _('Paypal account')
        }


class SampleProductForm(ModelForm):
    class Meta:
        model = models.SampleProduct
        fields = ["image"]


SampleProductFormset = forms.modelformset_factory(
    models.SampleProduct,
    fields=["image"],
    extra=10
)


class ProductForm(ModelForm):
    price_type = forms.ChoiceField(choices=(("default", _("Default")), ("custom", _("Custom"))))

    class Meta:
        model = models.Product
        fields = ["title", "file_type", "description", "keywords", "category",
                  "subcategory", "adult_content", "exclusive", "released", "editorial", "price_type",
                  "standard_price", "extended_price"]
        labels = {
            'title': _('Title'),
            'file_type': _('File Type'),
            'description': _('Description'),
            'keywords': _('Keywords'),
            'category': _('Category'),
            'subcategory': _('Subcategory'),
            'adult_content': _('Adult Content'),
            'exclusive': _('Exclusive'),
            'released': _('Released'),
            'editorial': _('Editorial'),
            'price_type': _('Price type'),
            'standard_price': _('Standard Price ($)'),
            'extended_price': _('Extended Price ($)'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subcategory'].queryset = models.SubCategory.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = models.SubCategory.objects.filter(main_category=category_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Subcategory queryset
        elif self.instance.pk:
            self.fields['subcategory'].queryset = self.instance.category.subcategory_set.order_by('name')


class ReviewForm(ModelForm):
    class Meta:
        model = models.Review
        fields = ["comment"]
        labels = {
            'comment': _('Comment')
        }


class FaqForm(ModelForm):
    class Meta:
        model = models.Faq
        fields = ["question", "answer"]


class PersonalFaqForm(ModelForm):
    class Meta:
        model = models.FaqPersonal
        fields = ["question"]
        labels = {
            'question': _('Have a Question ?')
        }


class NotificationForm(ModelForm):
    recipients = forms.ChoiceField(choices=(("contributors", "Contributors"), ("clients", "Clients"), ("custom", "Custom")))
    recipient = forms.ModelMultipleChoiceField(models.SowarStockUser.objects.all(), label="Recipient (select multiple)", widget=SelectMultiple(attrs={'style': 'height:200%'}))

    class Meta:
        model = Notification
        fields = ["recipients", "recipient", "level", "verb"]
        labels = {
            'verb': _('Message'),
            'level': _('Type'),
        }


class CategoryForm(ModelForm):
    class Meta:
        model = models.Category
        fields = ["name"]


class SubcategoryForm(ModelForm):
    main_category = forms.ModelMultipleChoiceField(models.Category.objects.all(), label="Category (select multiple)",
                                               widget=SelectMultiple(attrs={'style': 'height:200%'}))

    class Meta:
        model = models.SubCategory
        fields = ["name", "main_category"]


class CollectionForm(ModelForm):
    product = forms.ModelMultipleChoiceField(models.Product.objects.all(), label="Product (select multiple)",
                                             widget=CheckboxSelectMultiple)

    class Meta:
        model = models.Collection
        fields = ["title", "product"]


class LegalDocumentForm(ModelForm):
    class Meta:
        model = models.LegalDocument
        fields = ["document"]


class PaymentForm(ModelForm):
    class Meta:
        model = models.Payment
        fields = ["contributor", "receipt"]


class SearchKeywordSynonymsForm(ModelForm):
    class Meta:
        model = models.SearchKeywordSynonyms
        fields = ["word","synonyms"]


class UserRequestDeleteForm(ModelForm):
    class Meta:
        model = models.UserRequest
        fields = ["body"]
        labels = {
            'body': _('Reason for Deleting'),
        }


class SiteSettingsForm(ModelForm):
    class Meta:
        model = models.SiteSettings
        fields = ["watermark", "exclusive_percentage", "non_exclusive_percentage", "paypal_testing"]
