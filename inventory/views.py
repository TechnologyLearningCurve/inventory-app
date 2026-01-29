from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum, F, Count
from django.contrib import messages
from .models import Product, Category, Supplier, StockMovement
from .forms import ProductForm, CategoryForm, SupplierForm, StockMovementForm

def landing_page(request):
    return render(request, 'landing.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Analytics
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_products = Product.objects.filter(is_active=True, quantity__lte=F('reorder_level'))
    low_stock_count = low_stock_products.count()
    
    total_value = Product.objects.filter(is_active=True).aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total'] or 0
    
    recent_movements = StockMovement.objects.select_related('product').order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products,
        'total_value': total_value,
        'recent_movements': recent_movements,
        'page_title': 'Dashboard'
    }
    return render(request, 'dashboard/index.html', context)

# --- Product Views ---

@login_required
def product_list(request):
    products = Product.objects.select_related('category', 'supplier').filter(is_active=True)
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    context = {
        'products': products,
        'page_title': 'Products',
        'categories': Category.objects.all()
    }
    return render(request, 'products/list.html', context)

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'products/form.html', {'form': form, 'page_title': 'Add Product'})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/form.html', {'form': form, 'page_title': 'Edit Product'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.is_active = False # Soft delete
        product.save()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')
    return render(request, 'products/confirm_delete.html', {'obj': product, 'page_title': 'Delete Product'})

# --- Category Views ---

@login_required
def category_list(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    return render(request, 'categories/list.html', {'categories': categories, 'page_title': 'Categories'})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'categories/form.html', {'form': form, 'page_title': 'Add Category'})

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'categories/form.html', {'form': form, 'page_title': 'Edit Category'})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('category_list')
    return render(request, 'categories/confirm_delete.html', {'obj': category, 'page_title': 'Delete Category'})

# --- Supplier Views ---

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers/list.html', {'suppliers': suppliers, 'page_title': 'Suppliers'})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier created successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'suppliers/form.html', {'form': form, 'page_title': 'Add Supplier'})

@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'suppliers/form.html', {'form': form, 'page_title': 'Edit Supplier'})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('supplier_list')
    return render(request, 'suppliers/confirm_delete.html', {'obj': supplier, 'page_title': 'Delete Supplier'})

# --- Stock Views ---

@login_required
def stock_movement_list(request):
    movements = StockMovement.objects.select_related('product', 'created_by').order_by('-created_at')
    return render(request, 'stock/movements.html', {'movements': movements, 'page_title': 'Stock Movements'})

@login_required
def stock_adjust(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.created_by = request.user
            
            # Update product quantity
            product = movement.product
            if movement.movement_type == 'IN':
                product.quantity += movement.quantity
            elif movement.movement_type == 'OUT':
                product.quantity -= movement.quantity
            elif movement.movement_type == 'ADJUSTMENT':
                # For adjustment, we might want to set absolute value or just add/subtract.
                # Assuming adjustment adds/subtracts for now to keep it consistent, 
                # or we could interpret it as "set to" if we changed logic.
                # Let's stick to simple "add/subtract" logic based on signed int or handling it here.
                # Let's assume standard behavior: IN adds, OUT removes, ADJUSTMENT adds (can be negative).
                product.quantity += movement.quantity
            
            product.save()
            movement.save()
            messages.success(request, 'Stock adjustment recorded.')
            return redirect('stock_movement_list')
    else:
        form = StockMovementForm()
    return render(request, 'stock/adjust.html', {'form': form, 'page_title': 'Adjust Stock'})
