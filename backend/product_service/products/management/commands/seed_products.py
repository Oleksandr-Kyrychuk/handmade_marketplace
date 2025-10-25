import json
import requests
from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from django.conf import settings
from products.models import Category, Product
from decimal import Decimal
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seed database with real categories and products from JSON file (with vendor validation)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-vendor-check',
            action='store_true',
            help='Skip validation of vendor_id via User Service (use for local testing)',
        )

    def handle(self, *args, **kwargs):
        skip_vendor_check = kwargs['skip_vendor_check']
        json_path = Path(__file__).resolve().parent / 'products_seed.json'

        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f'JSON file not found: {json_path}'))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # === 1. Створюємо категорії ===
        self.stdout.write("Створення категорій...")
        categories = {}
        for cat_data in data.get('categories', []):
            name = cat_data['name']
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'parent': None}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Створено: {name} (ID: {category.id})'))
            else:
                self.stdout.write(self.style.WARNING(f'  Вже існує: {name} (ID: {category.id})'))
            categories[name] = category

        # === 2. Перевірка vendor_id (якщо не пропущено) ===
        products_data = data.get('products', [])
        if not products_data:
            self.stdout.write(self.style.WARNING("Немає продуктів у JSON файлі."))
            return

        vendor_ids = {p['vendor_id'] for p in products_data}
        valid_vendor_ids = set()

        if skip_vendor_check:
            self.stdout.write(self.style.WARNING("Пропущено перевірку vendor_id (--skip-vendor-check)"))
            valid_vendor_ids = vendor_ids
        else:
            user_service_url = getattr(settings, 'USER_SERVICE_URL', None)
            if not user_service_url:
                self.stdout.write(self.style.ERROR("USER_SERVICE_URL не налаштовано в settings"))
                return

            self.stdout.write(f"Перевірка {len(vendor_ids)} vendor_id у User Service...")
            for vid in sorted(vendor_ids):
                try:
                    response = requests.get(
                        f"{user_service_url}/users-list/{vid}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        valid_vendor_ids.add(vid)
                        self.stdout.write(self.style.SUCCESS(f'  Vendor {vid} — існує'))
                    else:
                        self.stdout.write(self.style.WARNING(f'  Vendor {vid} — НЕ існує (HTTP {response.status_code})'))
                except requests.RequestException as e:
                    self.stdout.write(self.style.ERROR(f'  Vendor {vid} — помилка запиту: {e}'))

        if not valid_vendor_ids:
            self.stdout.write(self.style.ERROR("Жоден vendor_id не валідний. Сідинг скасовано."))
            return

        # === 3. Створюємо продукти ===
        self.stdout.write("Створення продуктів...")
        created_count = 0
        skipped_count = 0

        for prod_data in products_data:
            original_name = prod_data['name']
            vendor_id = prod_data.get('vendor_id')

            # Пропускаємо, якщо vendor не валідний
            if vendor_id not in valid_vendor_ids:
                self.stdout.write(self.style.WARNING(f"  Пропущено: '{original_name}' (vendor_id {vendor_id} не існує)"))
                skipped_count += 1
                continue

            # Копіюємо дані, щоб не змінювати оригінал
            prod = prod_data.copy()

            # Категорія
            category_name = prod.pop('category_name', None)
            category = categories.get(category_name)
            if not category:
                self.stdout.write(self.style.ERROR(f"  Категорія '{category_name}' не знайдена для '{original_name}'"))
                skipped_count += 1
                continue
            prod['category'] = category

            # Аукціон: переводимо дні → datetime
            auction_days = prod.pop('auction_end_time_days', None)
            if auction_days is not None:
                if not isinstance(auction_days, int) or auction_days <= 0:
                    self.stdout.write(self.style.WARNING(f"  Некоректні auction_end_time_days для '{original_name}': {auction_days}"))
                else:
                    prod['auction_end_time'] = now() + timedelta(days=auction_days)

            # Конвертація цін у Decimal
            for field in ['price', 'discount_price', 'start_price']:
                value = prod.get(field)
                if value is not None:
                    try:
                        prod[field] = Decimal(str(value))
                    except (ValueError, TypeError, Decimal.InvalidOperation):
                        self.stdout.write(self.style.WARNING(f"  Некоректна ціна '{field}' для '{original_name}': {value}"))
                        prod[field] = Decimal('0.00') if field in ['price', 'start_price'] else None
                else:
                    prod[field] = Decimal('0.00') if field in ['price', 'start_price'] else None

            # Додаткові поля
            prod['is_approved'] = prod.get('is_approved', True)
            prod['stock'] = prod.get('stock', 0)

            # Створюємо продукт
            try:
                product, created = Product.objects.get_or_create(
                    name=prod['name'],
                    defaults=prod
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"  Створено: '{product.name}' (ID: {product.id}, Vendor: {vendor_id})"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"  Вже існує: '{product.name}' (ID: {product.id})"
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Помилка створення '{original_name}': {e}"))
                skipped_count += 1

        # === Підсумок ===
        self.stdout.write(self.style.SUCCESS(
            f"\nСідинг завершено: створено {created_count} продуктів, пропущено {skipped_count}."
        ))
        if not skip_vendor_check and skipped_count > 0:
            self.stdout.write(self.style.WARNING(
                "Порада: створіть відсутніх користувачів у User Service або використовуйте --skip-vendor-check"
            ))