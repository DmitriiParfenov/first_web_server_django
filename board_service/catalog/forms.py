import re

from django.forms import models, ValidationError, BaseInlineFormSet

from catalog.models import Product, Category, Blog, Version


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ProductForm(StyleFormMixin, models.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'description', 'image', 'price', 'category',)

    def clean_name(self):
        cleaned_data = self.cleaned_data['name']
        banned_words = r'(.*)(биржа|казино|криптовалюта|крипта|дешево|бесплатно|обман|полиция|радар)(.*)'
        if re.match(banned_words, cleaned_data, flags=re.IGNORECASE):
            raise models.ValidationError('Нельзя публиковать запрещенные товары')

        return cleaned_data


class CategoryForm(StyleFormMixin, models.ModelForm):
    class Meta:
        model = Category
        fields = ('category', 'description')


class BlogForm(StyleFormMixin, models.ModelForm):
    class Meta:
        model = Blog
        fields = ('title', 'content', 'image', 'email')


class VersionForm(models.ModelForm):

    class Meta:
        model = Version
        fields = ('title', 'number', 'is_active',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'is_active':
                field.widget.attrs['class'] = 'form'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_number(self):
        cleaned_data = self.cleaned_data['number']
        if cleaned_data < 1.00:
            raise ValidationError('Номер версии не может быть меньше 1.00')
        return cleaned_data


class VersionBaseInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        active_list = [form.cleaned_data['is_active'] for form in self.forms if 'is_active' in form.cleaned_data]
        if active_list.count(True) > 1:
            raise ValidationError('Возможна лишь одна активная версия. Пожалуйста, активируйте только 1 версию.')

