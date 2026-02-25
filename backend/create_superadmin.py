import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from user.models import AuthUser

def create_admin():
    email = 'admin@example.com'
    username = 'admin'
    password = 'Admin@123'
    
    if not AuthUser.objects.filter(email=email).exists():
        AuthUser.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Superuser created successfully: {username} ({email})")
    else:
        print(f"Superuser with email {email} already exists.")

if __name__ == '__main__':
    create_admin()
