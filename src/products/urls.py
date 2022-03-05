from django.urls import path

from .views import ProductsFromCSView, ListCreateProducts, RetrieveUpdateDestroyProducts

urlpatterns = [
    path('upload_csv/', ProductsFromCSView.as_view()),
    path('products/', ListCreateProducts.as_view()),
    path('products/<int:pk>', RetrieveUpdateDestroyProducts.as_view()),
]