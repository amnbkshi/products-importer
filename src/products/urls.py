from django.urls import path

from .views import ListCreateWebhooks, ProductsFromCSView, ListCreateProducts,\
     RetrieveUpdateDestroyProducts, DeleteAllProducts

urlpatterns = [
    path('upload_csv/', ProductsFromCSView.as_view()),
    path('products/', ListCreateProducts.as_view()),
    path('products/<int:pk>', RetrieveUpdateDestroyProducts.as_view()),
    path('delete_all/', DeleteAllProducts.as_view()),
    path('webhooks/', ListCreateWebhooks.as_view())
]