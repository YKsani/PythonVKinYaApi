import requests
import json
import tqdm

from vkapi import VkAPI
from yadiskapi import YaUploader

ROOTDIR = 'vk_fotos'


def get_photos_vk():

    print('Получаем данные из vk...')

    vk = VkAPI()

    owner_id_input = input('Введите ID или короткое имя пользователя, или нажмите Enter для использования личного ID: ')
    owner_id = vk.get_user_id(owner_id_input) if owner_id_input else vk.owner_id
    print(f'ID пользователя: {owner_id}')

    album_id_input = True
    album_id = 'wall'

    if album_id_input:
        user_albums = vk.get_user_albums(owner_id)
        if len(user_albums) > 0:
            albums_dict = {}
            for album in user_albums:
                if str(album['id']) != '-9000':
                    albums_dict.update({str(album['id']): album['title']})
                    album_id_print = f"id: {album['id']}, Название: {album['title']}, Число фотографий: {len(vk.get_user_photos_list(owner_id, album['id']))}"
                    print(album_id_print.replace('-', ''))
            temporary_album_id = int(input('Введите id альбома: '))
            album_id = str(temporary_album_id * -1)
            album_title = albums_dict[album_id]
    photos_list = vk.get_user_photos_list(owner_id, album_id)

    print(f'Всего фотографий в альбоме: {len(vk.get_user_photos_list(owner_id, album_id))}.')

    number_of_photos_input = input('Сколько фотографий загрузить на Яндекс.Диск? (По умолчанию - 5): ')
    if number_of_photos_input:
        number_of_photos = int(number_of_photos_input)
    else:
        number_of_photos = 5
    photos_list = photos_list[:number_of_photos]
    return photos_list, owner_id, album_title



def upload_to_yadisk(uploader, photos_list, path):
    log = []
    for photo_id, photo_url, likes_count, photo_size in tqdm.tqdm(photos_list,desc='Загрузка', ascii=' ░', ncols=100, colour= 'blue'):
        filename = f'{likes_count}_likes_{photo_id}.jpg'

        upload_url = uploader.get_upload_url(path=path, file=filename)
        upload_result = uploader.upload(requests.get(photo_url).content, upload_url)

        if upload_result != 201:
            print(f'Ошибка на стороне яндекса, файл с id {photo_id} не загружен: {upload_result}')
            log.append(
                {
                    'filename': filename,
                    'size': photo_size,
                    'result': upload_result
                }

            )
        else:
            log.append(
                {
                    'filename': filename,
                    'size': photo_size
                }
            )
    return log


def main():
    commands = {'vk': get_photos_vk, 'вк': get_photos_vk}

    command = ''
    while command != 'q':
        command = str.lower(input('Для того чтобы скачать фотографии из VK напишите команду "vk" или "вк": '))
        if command in commands:
            photos_list, owner_id, album_title = commands[command]()
            path = f'/{ROOTDIR}/{owner_id}/{album_title}'

            ya_token_input = input('Введите токен с полигона Яндекса: ')
            if ya_token_input:
                uploader = YaUploader(ya_token_input)
            else:
                uploader = YaUploader()

            temp_path = ''
            for folder in tqdm.tqdm(path.split('/'),desc='Проверка пути на Яндекс.диске, создание папок', ncols=100, colour='blue', bar_format='{l_bar}{bar}|'):
                temp_path += folder + '/'
                uploader.check_path(temp_path)

            log = upload_to_yadisk(uploader, photos_list, path)
            with open('log.json', 'w', encoding='utf8') as logfile:
                json.dump(log, logfile, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
