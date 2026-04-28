from rest_framework import viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingCreateSerializer


class BorrowingsViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def get_queryset(self):
        user = self.request.user
        q = self.queryset

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
