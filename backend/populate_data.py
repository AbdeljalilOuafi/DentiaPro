#!/usr/bin/env python3
import os
import psycopg2
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # Adjust if necessary

django.setup()


from django.core.management import call_command
from django.db import connection
from decouple import config
from tenants.models import Tenant, Domain
from inventory.models import Clinic
from django_tenants.utils import schema_context, get_public_schema_name
from django.contrib.auth import get_user_model
from django.db import transaction


User = get_user_model()

def reset_db():
    """Drop and recreate the database"""
    db_params = {
        'dbname': 'postgres',  # Connect to postgres db instead of your app db
        'user': config('DB_USER'),
        'password': config('DB_PASSWORD'),
        'host': config('DB_HOST', default='localhost'),
        'port': config('DB_PORT', default='5432')
    }
    
    db_name = config('DB_NAME')
    
    # Connect to postgres db to drop/create target db
    conn = psycopg2.connect(**db_params)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Terminating existing connections...")
    try:
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
            AND pid <> pg_backend_pid();
        """)
    except Exception as e:
        print(f"Error terminating connections: {e}")
    
    print("Dropping existing database...")
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
    except Exception as e:
        print(f"Error dropping database: {e}")
        # If we can't drop the database, we should exit
        cursor.close()
        conn.close()
        raise Exception("Failed to drop database. Please check permissions and existing connections.")
    
    print("Creating fresh database...")
    try:
        cursor.execute(f"CREATE DATABASE {db_name}")
    except Exception as e:
        print(f"Error creating database: {e}")
        cursor.close()
        conn.close()
        raise Exception("Failed to create database. Please check permissions.")
    
    cursor.close()
    conn.close()
    
def run_migrations():
    """Run all necessary migrations"""
    print("Running migrations for shared apps...")
    call_command('migrate_schemas', '--shared')
    print("Running migrations for tenant apps...")
    call_command('migrate_schemas')

def create_superuser():
    """Create a superuser for development"""
    print("Creating superuser...")
    User.objects.create_superuser(
        email="admin@example.com",
        password="admin123",
        first_name="Admin",
        last_name="User",
        clinic_name="Admin Clinic"
    )

def populate_test_data():
    """Create test tenants and their data"""
    
    public_schema = get_public_schema_name()

    with schema_context(public_schema):
        with transaction.atomic():
            # Create tenant1
            user1 = User.objects.create_user(
                email="dentist1@example.com",
                password="testpass123",
                first_name="John",
                last_name="Doe",
                clinic_name="Dental Clinic 1",
                is_paid=True,
                is_verified=True, #Email verification
                role=User.Role.ADMIN
            )
            
            tenant1 = Tenant.objects.create(
                schema_name=f"tenant_{user1.id}",
                name='Dental Clinic 1',
                user=user1,
                is_verified=True,
                paid_until=None
            )
            
            Domain.objects.create(
                domain='dental-clinic-1.localhost',  # Changed to localhost
                tenant=tenant1,
                is_primary=True
            )

            # Create tenant2
            user2 = User.objects.create_user(
                email="dentist2@example.com",
                password="testpass123",
                first_name="Jane",
                last_name="Smith",
                clinic_name="Dental Clinic 2",
                is_paid=True,
                is_verified=True,
                role=User.Role.ADMIN

            )
            
            tenant2 = Tenant.objects.create(
                schema_name=f"tenant_{user2.id}",
                name='Dental Clinic 2',
                user=user2,
                is_verified=True,
                paid_until=None
            )
            
            Domain.objects.create(
                domain='dental-clinic-2.localhost',  # Changed to localhost
                tenant=tenant2,
                is_primary=True
            )

    # Add data to tenant1's schema
    with schema_context(f"tenant_{user1.id}"):
        Clinic.objects.create(name="Main Branch", patient_count=150)
        Clinic.objects.create(name="Downtown Branch", patient_count=75)

    # Add data to tenant2's schema
    with schema_context(f"tenant_{user2.id}"):
        Clinic.objects.create(name="Westside Clinic", patient_count=200)

def main():
    """Main function to run the setup"""
    print("Starting development database setup...")
    
    # Reset database
    reset_db()
    
    
    # Run migrations
    run_migrations()
    
        
    # Populate test data
    populate_test_data()
    
    print("\nSetup completed successfully!")
    print("\nCredentials:")
    print("Superuser:")
    print("  Email: admin@example.com")
    print("  Password: admin123")
    print("\nTest Users:")
    print("1. Dental Clinic 1:")
    print("  Email: dentist1@example.com")
    print("  Password: testpass123")
    print("  URL: http://dental-clinic-1.localhost:8000/api/clinics/")
    print("\n2. Dental Clinic 2:")
    print("  Email: dentist2@example.com")
    print("  Password: testpass123")
    print("  URL: http://dental-clinic-2.localhost:8000/api/clinics/")

if __name__ == "__main__":
    main()