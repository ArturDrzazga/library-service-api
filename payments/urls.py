from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payments.views import PaymentViewSet

router = DefaultRouter()
router.register("", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
]