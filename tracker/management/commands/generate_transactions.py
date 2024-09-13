import random
from faker import Faker
from django.core.management.base import BaseCommand
from tracker.models import User, Category, Transaction


class Command(BaseCommand):
    help = "Generate transactions for testing"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # create some categories
        categories = [
            "Bills",
            "Food",
            "Clothes",
            "Medical",
            "Housing",
            "Salary",
            "Social",
            "Transport",
            "Vacation",
        ]

        for category in categories:
            Category.objects.get_or_create(name=category)

        user = User.objects.filter(username="admin").first()
        if not user:
            user = User.objects.create_superuser(
                username="admin", email="admin@mail.com", password="1234"
            )

        categories = Category.objects.all()
        types = [x[0] for x in Transaction.TRANSACTION_TYPE_CHOICES]
        for i in range(1000):
            Transaction.objects.create(
                user=user,
                category=random.choice(categories),
                type=random.choice(types),
                amount=random.uniform(1, 2500),
                date=fake.date_between(start_date="-1y", end_date="today"),
            )
