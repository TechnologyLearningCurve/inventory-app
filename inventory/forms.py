from django import forms
from .models import Product, Category, Supplier, StockMovement

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-checkbox'
            else:
                field.widget.attrs['class'] = 'form-input'
            
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3

class ProductForm(BaseForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'supplier', 'unit_price', 'quantity', 'reorder_level', 'description', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select Category"
        self.fields['supplier'].empty_label = "Select Supplier"

class CategoryForm(BaseForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class SupplierForm(BaseForm):
    class Meta:
        model = Supplier
        fields = ['name', 'email', 'phone', 'address']

class StockMovementForm(BaseForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'reference', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].empty_label = "Select Product"
