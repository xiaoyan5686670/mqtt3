#!/usr/bin/env python
import requests
import json

# EMQX API configuration
API_KEY = "f3d064c3dacad617"
API_SECRET = "ezGnurOe8d4GV2LJF4Ptw46wnavTqL9AenBZyIoePWwP"
EMQX_SERVER = "172.16.208.176"
API_PORT = 18083

def test_emqx_api():
    """Test EMQX REST API connection"""
    api_url = f"http://{EMQX_SERVER}:{API_PORT}/api/v5/clients"
    
    print("=" * 60)
    print("Testing EMQX REST API Connection")
    print("=" * 60)
    print(f"URL: {api_url}")
    print(f"API Key: {API_KEY}")
    print(f"Secret Key: {API_SECRET[:20]}...")
    print("")
    
    try:
        # Send request with Basic Auth
        response = requests.get(
            api_url,
            auth=(API_KEY, API_SECRET),
            timeout=10,
            params={'limit': 10}
        )
        
        print(f"Status Code: {response.status_code}")
        print("")
        
        if response.status_code == 200:
            data = response.json()
            client_count = len(data.get('data', []))
            total_count = data.get('meta', {}).get('count', 0)
            
            print("✅ Connection Successful!")
            print("")
            print(f"Total Clients: {total_count}")
            print(f"Clients in Response: {client_count}")
            print("")
            
            if client_count > 0:
                print("Client List:")
                print("-" * 60)
                for i, client in enumerate(data['data'][:5], 1):
                    print(f"{i}. ClientID: {client.get('clientid')}")
                    print(f"   Username: {client.get('username', 'N/A')}")
                    print(f"   IP: {client.get('ip_address')}")
                    print(f"   Connected: {client.get('connected')}")
                    print(f"   Connected At: {client.get('connected_at')}")
                    print("")
                
                if client_count > 5:
                    print(f"... and {client_count - 5} more clients")
            else:
                print("No clients connected")
            
            print("=" * 60)
            print("Test completed successfully!")
            
        elif response.status_code == 401:
            print("❌ Authentication Failed!")
            print("Error: Invalid API Key or Secret Key")
            print("")
            print("Please check:")
            print("1. API Key is correct")
            print("2. Secret Key is correct")
            print("3. API Key is not expired")
            
        else:
            print(f"❌ API Request Failed!")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.Timeout:
        print("❌ Connection Timeout!")
        print("Please check:")
        print("1. EMQX server is running")
        print("2. Network connection is stable")
        print("3. API port (18083) is accessible")
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error!")
        print("Cannot connect to EMQX server")
        print("")
        print("Please check:")
        print(f"1. EMQX server ({EMQX_SERVER}) is running")
        print(f"2. Port {API_PORT} is open")
        print("3. Firewall settings")
    
    except Exception as e:
        print(f"❌ Unexpected Error!")
        print(f"Error: {e}")
    
    print("=" * 60)


if __name__ == "__main__":
    test_emqx_api()
