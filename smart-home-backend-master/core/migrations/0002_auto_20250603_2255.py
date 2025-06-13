# core/migrations/0002_empty.py
from django.db import migrations

class Migration(migrations.Migration):
    # 保持原始依赖关系不变
    dependencies = [
        ('core', '0001_initial'),
    ]
    
    # 空操作列表
    operations = []