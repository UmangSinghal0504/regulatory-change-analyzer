import requests

# Test with your actual text files
response = requests.post(
    'http://localhost:5000/analyze',
    files={
        'old_file': open('Text_v1.txt', 'rb'),
        'new_file': open('Text_v2.txt', 'rb')
    }
)

print("Status Code:", response.status_code)
print("Response:", response.json())