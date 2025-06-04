from django.db import migrations

def create_users(apps, schema_editor):
    SmartHomeUser = apps.get_model('core', 'SmartHomeUser')
    SmartHomeUser.objects.create_user(username='member1', password='member123', role='member')

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),  # 依赖之前的迁移
    ]
    operations = [
        migrations.RunPython(create_users),
    ]