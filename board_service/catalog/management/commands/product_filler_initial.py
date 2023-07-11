from django.core.management import BaseCommand
from django.db import connection
from catalog.models import Product
import json


class Command(BaseCommand):
    def handle(self, *args, **options):
        cur = connection.cursor()
        cur.execute("TRUNCATE TABLE catalog_product RESTART IDENTITY")
        cur.close()

        with open('catalog_data.json', 'r', encoding='utf-8') as file:
            db = []
            data = json.load(file)
            for elem in data:
                db.append(Product(**elem))

            Product.objects.bulk_create(db)