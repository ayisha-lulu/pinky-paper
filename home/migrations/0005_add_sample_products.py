from django.db import migrations


def add_products(apps, schema_editor):
    Product = apps.get_model('home', 'Product')

    products = [
        {
            'name': 'Mini Cute Diary',
            'description': 'Cute mini diary with a beautiful pastel cover. Perfect for daily notes and journaling.',
            'price': '89.00',
            'category': 'Notebooks',
            'stock': 14,
        },
        {
            'name': 'Pastel Pen Set',
            'description': 'Colourful pastel gel pens with smooth writing.',
            'price': '99.00',
            'category': 'Pens',
            'stock': 20,
        },
        {
            'name': 'Heart Paper Clips',
            'description': 'Adorable heart-shaped paper clips in lovely colours.',
            'price': '59.00',
            'category': 'Accessories',
            'stock': 29,
        },
    ]

    for item in products:
        Product.objects.get_or_create(
            name=item['name'],
            defaults=item,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_order_address_order_full_name_order_payment_method_and_more'),
    ]

    operations = [
        migrations.RunPython(add_products, migrations.RunPython.noop),
    ]