from django.urls import path

from .views import ProductsFromCSView

urlpatterns = [
    path('products/upload_csv/', ProductsFromCSView.as_view()),
]