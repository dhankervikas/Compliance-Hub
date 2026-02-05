
import requests

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
        headers_found = False
        for k, v in res.headers.items():
            if 'access-control' in k.lower():
                print(f"    {k}: {v}")
                headers_found = True
        
        if not headers_found:
             print(" -> WARNING: No CORS headers found!")

        if res.status_code == 200 and 'access-control-allow-origin' in {k.lower(): v for k, v in res.headers.items()}:
             print(" -> CORS Check PASS")
        else:
             print(" -> CORS Check FAIL")

    except Exception as e:
        print(f" -> HTTP Failure: {e}")

if __name__ == "__main__":
    test_http_options("http://127.0.0.1:8002/api/v1/users/", "http://127.0.0.1:3000")
    test_http_options("http://127.0.0.1:8002/api/v1/auth/login", "http://127.0.0.1:3000")
