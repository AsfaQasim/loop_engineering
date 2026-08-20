import os

def main():
    token = os.environ.get('DUMMY_API_TOKEN')
    if token:
        print(f"SUCCESS: DUMMY_API_TOKEN = {token}")
    else:
        print("FAILURE: DUMMY_API_TOKEN not found in environment variables.")
        print("Note: Credentials are available as environment variables; do not look for a .env file.")

if __name__ == "__main__":
    main()