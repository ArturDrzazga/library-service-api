from datetime import date

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingCreateSerializer


class BorrowingsViewSet(viewsets.ModelViewSet):
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def get_queryset(self):
        user = self.request.user
        q = Borrowing.objects.select_related("book", "user")

        if not user.is_staff:
            q = q.filter(user_id=user.id)

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active == "true":
            q = q.filter(actual_return_date__isnull=True)
        elif is_active == "false":
            q = q.filter(actual_return_date__isnull=False)

        if user_id:
            q = q.filter(user_id=user_id)

        return q

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            raise ValidationError("Borrowing already returned")

        borrowing.actual_return_date = date.today()
        borrowing.save()
        borrowing.book.inventory += 1
        borrowing.book.save()

        return Response(BorrowingSerializer(borrowing).data)
