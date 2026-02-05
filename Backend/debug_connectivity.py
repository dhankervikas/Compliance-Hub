
import requests
import socket
import time

def test_tcp_connection(host, port):
    print(f"Testing TCP Connection to {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
        print(" -> TCP Connection SUCCESS")
        s.close()
        return True
    except Exception as e:
        print(f" -> TCP Connection FAILED: {e}")
        return False

def test_http_options(url, origin):
    print(f"\nTesting HTTP OPTIONS to {url}")
    print(f"Origin: {origin}")
    try:
        res = requests.options(
            url,
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            },
            timeout=2
        )
        print(f" -> Status: {res.status_code}")
        print(" -> Headers:")
        for k, v in res.headers.items():
            if 'access-control' in k.lower():
                print(f"    {k}: {v}")
        
        if res.status_code == 200 and 'access-control-allow-origin' in {k.lower(): v for k, v in res.headers.items()}:
             print(" -> CORS Check PASS")
        else:
             print(" -> CORS Check FAIL")

    except requests.exceptions.ConnectionError:
        print(f" -> HTTP Connection REFUSED (Network Error)")
    except Exception as e:
        print(f" -> HTTP Failure: {e}")

if __name__ == "__main__":
    print("=== DIAGNOSTIC START ===")
    
    # 1. TCP Check
    test_tcp_connection("127.0.0.1", 8002)
    test_tcp_connection("localhost", 8002)
    
    # 2. HTTP Check (127.0.0.1)
    # Browser is at localhost:3000, calling 127.0.0.1:8002
    test_http_options("http://127.0.0.1:8002/api/v1/auth/login", "http://localhost:3000")
    
    # 3. HTTP Check (localhost)
    test_http_options("http://localhost:8002/api/v1/auth/login", "http://localhost:3000")
    
    print("\n=== DIAGNOSTIC END ===")
