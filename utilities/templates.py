import requests

def get_template_data(authorization, template_id):
    url = f'http://127.0.0.1:8000/api/templates/{template_id}/'

    # url = f'https://colegios-api-42b1901162d8.herokuapp.com/api/templates/{template_id}/'

    try:
        response = requests.get(url, headers={'authorization': authorization})
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print('Error occurred while making the request:', e)
        return None