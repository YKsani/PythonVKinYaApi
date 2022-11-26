import requests
import json
from tokens import ya_token
from requests.exceptions import Timeout, ConnectionError

class YaUploader:
    apiurl = 'https://cloud-api.yandex.net/v1/disk/resources/upload'

    def __init__(self, token=ya_token):
        self.token = token
        self.auth = {
            'Authorization': f'OAuth {self.token}'
        }

    def get_upload_url(self, path, file):
        global response
        params = {
            'path': f'{path}/{file}',
            'overwrite': 'true'
        }
        try:
            response = requests.get(self.apiurl, params=params, headers=self.auth)
            if response.ok:
                print()
        except ConnectionError:
            print('Ошибка соединения, проверьте подключение к интернету')
            quit()
        except Timeout:
            print('Ошибка таймаута')
            quit()
        except:
            if response.status_code >= 400 and response.status_code < 500:
                print(f'Ошибка на стороне клиента: код ошибки {response.status_code}')
                quit()
            elif response.status_code >= 500:
                print(f'Ошибка на стороне сервера: код ошибки {response.status_code}')
                quit()
            else:
                print('Неустановленная ошибка')
        result = json.loads(response.text)
        return result.get('href')

    def check_path(self, path):
        global response_test
        params = {
            'path': path
        }
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        try:
            response_test = requests.get(url, params=params, headers=self.auth)
            requests.put(url, params=params, headers=self.auth)
            if response_test.ok:
                print()
        except ConnectionError:
            print('Ошибка соединения, проверьте подключение к интернету!')
            quit()
        except Timeout:
            print('Ошибка таймаута')
            quit()
        except:
            if response_test.status_code >= 400 and response_test.status_code < 500:
                print(f'Ошибка на стороне клиента: код ошибки {response_test.status_code}')
                quit()
            elif response_test.status_code >= 500:
                print(f'Ошибка на стороне сервера: код ошибки {response_test.status_code}')
                quit()
            else:
                print('Неустановленная ошибка')



    def upload(self, file, upload_url):
        global response
        if upload_url:
            response = requests.put(upload_url, data=file)
            return response.status_code
        else:
            return response.status_code
