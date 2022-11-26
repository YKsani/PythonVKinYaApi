from tokens import vk_token, vk_service_token
from datetime import datetime
from requests.exceptions import Timeout, ConnectionError
import requests


class VkAPI:
    apiurl = 'https://api.vk.com/method/'

    def __init__(self, token=vk_token, version='5.130'):
        global check_response
        self.token = token
        self.version = version
        self.params = {
            'access_token': self.token,
            'v': self.version
        }
        try:
            check_response = requests.get(self.apiurl + 'users.get', self.params)
            self.owner_id = requests.get(self.apiurl + 'users.get', self.params).json()['response'][0]['id']
            if check_response.ok:
                print('Соединение установлено!')
        except ConnectionError:
            print('Ошибка соединения, проверьте подключение к интернету')
            quit()
        except Timeout:
            print('Ошибка таймаута')
            quit()
        except:
            if check_response.status_code >= 400 and check_response.status_code < 500:
                print(f'Ошибка на стороне клиента: код ошибки {check_response.status_code}')
                quit()
            elif check_response.status_code >= 500:
                print(f'Ошибка на стороне сервера: код ошибки {check_response.status_code}')
                quit()
            else:
                if check_response.status_code == 200:
                    print('Соединение установлено, но возникла ошибка: проверьте правильность Vk-токена(возможно он устарел)')
                    quit()
                else:
                    print('Неустановленная ошибка')


    def get_user_photos_list(self, owner_id=None, album_id='wall'):
        if owner_id is None:
            owner_id = self.owner_id
        photo_params = {
            **self.params,
            'owner_id': owner_id,
            'album_id': album_id,
            'extended': 1,
            'count': 1000
        }
        photos_dict = requests.get(self.apiurl + 'photos.get', photo_params).json()
        output = []
        for photo in photos_dict['response']['items']:
            maxsize = 0
            photo_url = ''
            photo_size = ''
            for size in photo['sizes']:
                if maxsize <= size.get('height') + size.get('width'):
                    maxsize = size.get('height') + size.get('width')
                    photo_url = size.get('url')
                    photo_size = size.get('type')
            photo_date = datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d_%H.%M.%S')
            output += [(photo_date, photo_url, photo['likes']['count'], photo_size)]
        return output

    def get_user_albums(self, owner_id=None):
        if owner_id is None:
            owner_id = self.owner_id
        album_params = {
            **self.params,
            'owner_id': owner_id,
            'need_system': 1
        }
        if owner_id == self.owner_id:
            album_params['access_token'] = vk_service_token
        response = requests.get(self.apiurl + 'photos.getAlbums', album_params)
        result = response.json()['response']['items']
        return result

    def get_user_id(self, username):
        params = {
            **self.params,
            'user_ids': username
        }
        try:
            return requests.get(self.apiurl + 'users.get', params).json()['response'][0]['id']
        except(Exception):
            print('Вы ввели некорректное имя пользователя или такого пользователя не существует')
            quit()