from datetime import date

from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "expected_return_date",
        ]

    def validate_book(self, book):
        if book.inventory == 0:
            raise serializers.ValidationError("Book is not available")
        return book

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        return Borrowing.objects.create(
            user=user,
            borrow_date=date.today(),
            **validated_data
        )
