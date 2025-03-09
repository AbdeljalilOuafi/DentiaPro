#!/usr/bin/env python3
"""test-appointments module"""


# testing_script.py
# A script to test the AppointmentViewSet API endpoints
import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # Adjust if necessary
django.setup()

import requests
import json
from datetime import datetime, timedelta
from tenants.models import Domain, Tenant
from tenants.models import User

# Base URL for the API
BASE_URL = 'http://dental-clinic-1.localhost:8000/api'  # Adjust as needed

# Authentication - usually you'd have a login endpoint to get a token
# Here we'll assume you have a token already

AUTH_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQxMDE4NDExLCJpYXQiOjE3NDEwMTgxMTEsImp0aSI6IjVhY2NiYTgyZWE5NDRkMmFiMTg5ODk2MDdlZDI3NTY0IiwidXNlcl9pZCI6MX0.g9lDLcZYOKGTLb0IxSD-5oAJnrTNiM02aAymyrUsbKI'
HEADERS = {
    'Authorization': f'Token {AUTH_TOKEN}',
    'Content-Type': 'application/json'
}

# Function to create a test patient
def create_patient(tenant_id, dentist_id):
    patient_data = {
        'first_name': 'Test',
        'last_name': 'Patient',
        'date_of_birth': '1990-01-01',
        'gender': 'M',
        'phone_number': '+12345678901',
        'email': 'test.patient@example.com',
        'address': '123 Test St, Test City',
        'dentist': dentist_id,
        'tenant': tenant_id
    }
    
    response = requests.post(
        f'{BASE_URL}/patients/',
        headers=HEADERS,
        data=json.dumps(patient_data)
    )
    
    if response.status_code == 201:
        print("Patient created successfully!")
        return response.json()['id']
    else:
        print(f"Failed to create patient: {response.text}")
        return None

# Function to create a test appointment
def create_appointment(tenant_id, patient_id, dentist_id):
    # Create an appointment for tomorrow at 10 AM
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    appointment_data = {
        'patient': patient_id,
        'dentist': dentist_id,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'status': 'SCHEDULED',
        'notes': 'Test appointment created via script'
    }
    
    response = requests.post(
        f'{BASE_URL}/appointments/',
        headers=HEADERS,
        data=json.dumps(appointment_data)
    )
    
    if response.status_code == 201:
        print("Appointment created successfully!")
        return response.json()['id']
    else:
        print(f"Failed to create appointment: {response.text}")
        return None

# Function to list all appointments
def list_appointments():
    response = requests.get(
        f'{BASE_URL}/appointments/',
        headers=HEADERS
    )
    
    if response.status_code == 200:
        appointments = response.json()
        print(f"Found {len(appointments)} appointments:")
        for app in appointments:
            print(f"ID: {app['id']}, Patient: {app['patient']}, Time: {app['start_time']}")
        return appointments
    else:
        print(f"Failed to list appointments: {response.text}")
        return None

# Function to get appointments by date range
def list_appointments_by_date(start_date, end_date):
    response = requests.get(
        f'{BASE_URL}/appointments/?start={start_date}&end={end_date}',
        headers=HEADERS
    )
    
    if response.status_code == 200:
        appointments = response.json()
        print(f"Found {len(appointments)} appointments between {start_date} and {end_date}")
        return appointments
    else:
        print(f"Failed to list appointments by date: {response.text}")
        return None

# Function to get appointments for a specific dentist
def list_appointments_by_dentist(dentist_id):
    response = requests.get(
        f'{BASE_URL}/appointments/?dentist={dentist_id}',
        headers=HEADERS
    )
    
    if response.status_code == 200:
        appointments = response.json()
        print(f"Found {len(appointments)} appointments for dentist {dentist_id}")
        return appointments
    else:
        print(f"Failed to list appointments by dentist: {response.text}")
        return None

# Function to get a single appointment
def get_appointment(appointment_id):
    response = requests.get(
        f'{BASE_URL}/appointments/{appointment_id}/',
        headers=HEADERS
    )
    
    if response.status_code == 200:
        appointment = response.json()
        print(f"Retrieved appointment: {appointment['id']}")
        return appointment
    else:
        print(f"Failed to get appointment: {response.text}")
        return None

# Function to update an appointment
def update_appointment(appointment_id, status='CONFIRMED', notes=None):
    update_data = {'status': status}
    if notes:
        update_data['notes'] = notes
        
    response = requests.patch(
        f'{BASE_URL}/appointments/{appointment_id}/',
        headers=HEADERS,
        data=json.dumps(update_data)
    )
    
    if response.status_code == 200:
        print(f"Updated appointment {appointment_id}")
        return response.json()
    else:
        print(f"Failed to update appointment: {response.text}")
        return None

# Function to delete an appointment
def delete_appointment(appointment_id):
    response = requests.delete(
        f'{BASE_URL}/appointments/{appointment_id}/',
        headers=HEADERS
    )
    
    if response.status_code == 204:
        print(f"Deleted appointment {appointment_id}")
        return True
    else:
        print(f"Failed to delete appointment: {response.text}")
        return False

# Function to get available time slots
def get_available_slots(start_date, end_date, dentist_id):
    response = requests.get(
        f'{BASE_URL}/appointments/calendar_slots/?start={start_date}&end={end_date}&dentist={dentist_id}',
        headers=HEADERS
    )
    
    if response.status_code == 200:
        slots = response.json()
        print(f"Found {len(slots)} available slots")
        return slots
    else:
        print(f"Failed to get available slots: {response.text}")
        return None

# Main function to run all tests
def run_tests():
    # You'll need to provide these values
    user = User.objects.get(email='dentist1@example.com')
    domain = Domain.objects.get(domain='dental-clinic-1.localhost')
    tenant = domain.tenant
    
    # Get tenant and dentist IDs
    tenant_id = tenant.id
    dentist_id = user.id
    
    # Create a test patient
    patient_id = create_patient(tenant_id, dentist_id)
    if not patient_id:
        print("Exiting tests as patient creation failed")
        return
    
    # Create a test appointment
    appointment_id = create_appointment(tenant_id, patient_id, dentist_id)
    if not appointment_id:
        print("Exiting tests as appointment creation failed")
        return
    
    # List all appointments
    list_appointments()
    
    # Get appointment by ID
    get_appointment(appointment_id)
    
    # List appointments for a specific date range
    today = datetime.now().strftime('%Y-%m-%d')
    next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    list_appointments_by_date(today, next_week)
    
    # List appointments for a specific dentist
    list_appointments_by_dentist(dentist_id)
    
    # Update the appointment
    update_appointment(appointment_id, status='CONFIRMED', notes='Updated via script')
    
    # Get available slots
    get_available_slots(today, next_week, dentist_id)
    
    # Delete the appointment
    delete_appointment(appointment_id)
    
    print("All tests completed!")

if __name__ == "__main__":
    run_tests()