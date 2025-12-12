"""
REST API Test Script for Vietnamese Medical Chatbot
Tests all CRUD endpoints: /api/chat, /api/intents, /api/search, /api/patients
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def print_response(name, response):
    print(f"\n{'='*50}")
    print(f"TEST: {name}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*50}")

def test_all():
    print("\n" + "="*60)
    print("    REST API FULL TEST - VIETNAMESE MEDICAL CHATBOT")
    print("="*60)

    # 1. GET /api/intents - List all intents
    print("\n[1] GET /api/intents")
    r = requests.get(f"{BASE_URL}/api/intents")
    print_response("List Intents", r)

    # 2. POST /api/chat - Chat dengan mode problem
    print("\n[2] POST /api/chat (greeting)")
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "xin chào",
        "mode": "problem"
    })
    print_response("Chat - Greeting", r)

    # 3. POST /api/chat - Booking
    print("\n[3] POST /api/chat (booking)")
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "cho tôi đặt lịch khám",
        "mode": "problem"
    })
    print_response("Chat - Booking", r)

    # 4. POST /api/chat - Sinusitis
    print("\n[4] POST /api/chat (sinusitis)")
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "nghẹt mũi kéo dài, đau đầu vùng trán",
        "mode": "problem"
    })
    print_response("Chat - Sinusitis", r)

    # 5. POST /api/chat - Gastric reflux
    print("\n[5] POST /api/chat (gastric reflux)")
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "đau bụng thượng vị, ợ chua",
        "mode": "problem"
    })
    print_response("Chat - Gastric Reflux", r)

    # 6. POST /api/chat - thongtin mode (search)
    print("\n[6] POST /api/chat (thongtin mode)")
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "viêm xoang điều trị thế nào",
        "mode": "thongtin"
    })
    print_response("Chat - Thongtin Mode", r)

    # 7. GET /api/search - Search for viêm xoang
    print("\n[7] GET /api/search?q=viêm xoang")
    r = requests.get(f"{BASE_URL}/api/search", params={"q": "viêm xoang", "limit": 3})
    print_response("Search - Viêm Xoang", r)

    # 8. GET /api/search - Search for trào ngược
    print("\n[8] GET /api/search?q=trào ngược")
    r = requests.get(f"{BASE_URL}/api/search", params={"q": "trào ngược dạ dày", "limit": 3})
    print_response("Search - Trào Ngược", r)

    # 9. GET /api/patients - List all patients
    print("\n[9] GET /api/patients")
    r = requests.get(f"{BASE_URL}/api/patients")
    print_response("List Patients", r)

    # 10. POST /api/patients - Create new patient
    print("\n[10] POST /api/patients (CREATE)")
    r = requests.post(f"{BASE_URL}/api/patients", json={
        "name": "Nguyễn Văn Test",
        "sex": "male",
        "age": 35,
        "diagnosis": "Viêm xoang",
        "date": "2025-12-12"
    })
    print_response("Create Patient", r)
    new_patient_id = r.json().get('id') if r.status_code == 201 else None

    # 11. GET /api/patients - List again after create
    print("\n[11] GET /api/patients (after create)")
    r = requests.get(f"{BASE_URL}/api/patients")
    print_response("List Patients After Create", r)

    # 12. GET /api/patients/<id> - Get specific patient
    if new_patient_id:
        print(f"\n[12] GET /api/patients/{new_patient_id}")
        r = requests.get(f"{BASE_URL}/api/patients/{new_patient_id}")
        print_response(f"Get Patient {new_patient_id}", r)

        # 13. DELETE /api/patients/<id> - Delete patient
        print(f"\n[13] DELETE /api/patients/{new_patient_id}")
        r = requests.delete(f"{BASE_URL}/api/patients/{new_patient_id}")
        print_response(f"Delete Patient {new_patient_id}", r)

        # 14. GET /api/patients - List again after delete
        print("\n[14] GET /api/patients (after delete)")
        r = requests.get(f"{BASE_URL}/api/patients")
        print_response("List Patients After Delete", r)

    print("\n" + "="*60)
    print("    API TEST COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    test_all()
