
import requests

def debug_cors():
    url = "http://localhost:8002/api/v1/users/"
    origin = "http://localhost:3000"
    
    print(f"Testing CORS Options for: {url}")
    print(f"Origin: {origin}")
    
    try:
        response = requests.options(
            url,
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print("Headers:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
            
        if "Access-Control-Allow-Origin" in response.headers:
            print("\nSUCCESS: CORS Header Present!")
            if response.headers["Access-Control-Allow-Origin"] == origin:
                 print(" -> Origin Matches.")
            else:
                 print(f" -> Origin Mismatch! Got: {response.headers['Access-Control-Allow-Origin']}")
        else:
            print("\nFAILURE: Access-Control-Allow-Origin header MISSING.")
            
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    debug_cors()
