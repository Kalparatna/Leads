"""
Simple test script to verify the Lead Scoring API functionality
"""

import requests
import json
import os

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_offer_upload():
    """Test offer upload"""
    print("Testing offer upload...")
    offer_data = {
        "name": "AI Outreach Automation",
        "value_props": ["24/7 outreach", "6x more meetings"],
        "ideal_use_cases": ["B2B SaaS mid-market"]
    }
    
    response = requests.post(
        f"{BASE_URL}/offer",
        headers={"Content-Type": "application/json"},
        json=offer_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_leads_upload():
    """Test leads upload"""
    print("Testing leads upload...")
    
    # Check if sample file exists
    if not os.path.exists("sample_leads.csv"):
        print("sample_leads.csv not found. Please create it first.")
        return
    
    with open("sample_leads.csv", "rb") as f:
        files = {"file": ("sample_leads.csv", f, "text/csv")}
        response = requests.post(f"{BASE_URL}/leads/upload", files=files)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_scoring():
    """Test lead scoring"""
    print("Testing lead scoring...")
    response = requests.post(f"{BASE_URL}/score")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_results():
    """Test results retrieval"""
    print("Testing results retrieval...")
    response = requests.get(f"{BASE_URL}/results")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"Number of results: {len(results)}")
        if results:
            print("Sample result:")
            print(json.dumps(results[0], indent=2))
    else:
        print(f"Response: {response.json()}")
    print()

def test_csv_export():
    """Test CSV export"""
    print("Testing CSV export...")
    response = requests.get(f"{BASE_URL}/results/export")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        with open("exported_results.csv", "w") as f:
            f.write(response.text)
        print("Results exported to exported_results.csv")
    else:
        print(f"Response: {response.text}")
    print()

def main():
    """Run all tests"""
    print("=== Lead Scoring API Test Suite ===\n")
    
    try:
        test_health_check()
        test_offer_upload()
        test_leads_upload()
        test_scoring()
        test_results()
        test_csv_export()
        
        print("=== All tests completed ===")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()