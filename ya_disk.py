import json
import os
import requests
import vk


class YaUploader:
    """Класс для работы с ЯД"""

    def __init__(self, token: str) -> None:
        """Инициализация объекта

        Args:
            token(str): Токен к API ЯД
        """
        self.token = token

    def get_upload_url(self, file_path: str) -> str:
        """Метод получает ссылку для загрузки файла на ЯД

        Args:
            file_path(str): Путь к файлу, который необходимо загрузить на ЯД

        Returns:
            upload_url (str): URL для загрузки файла
        """
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {"path": file_path, "overwrite": True}
        headers = {"Authorization": f"OAuth {self.token}"}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        upload_url = response.json()["href"]
        return upload_url

    def upload(self, file_path: str) -> str:
        """Метод загружает файл на яндекс диск

        Args:
            file_path(str): Путь к файлу, который необходимо загрузить на ЯД

        Returns:
            result(str): Результат операции
        """
        if not os.path.isfile(file_path):
            result = "Файл не существует"
        else:
            if len(file_path.split("/")) > 1:
                self.create_path(file_path[: file_path.rfind("/")])
            response = requests.put(
                self.get_upload_url(file_path), data=open(file_path, "rb")
            )
            response.raise_for_status()
            result = f"Статус ответа {response.status_code}"
        return result

    def upload_by_url(self, file_path: str, url: str) -> str:
        if len(file_path.split("/")) > 1:
            data = requests.get(url).content
            response = requests.put(
                self.get_upload_url(file_path), data=data
            )
            response.raise_for_status()
            result = f"Статус ответа {response.status_code}"
            return result


    def create_dir(self, dir: str) -> None:
        """Метод создания папки

        Args:
            dir(str): Наименование папки

        """
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {"path": dir, "overwrite": True}
        headers = {"Authorization": f"OAuth {self.token}"}
        response = requests.put(url, params=params, headers=headers)
        response.raise_for_status()

    def create_path(self, path: str) -> None:
        """Метод создания структуры папок

        Args:
            path(str): Структура папок

        """
        path_dirs = path.split("/")
        total_path = ""
        for dir in path_dirs:
            total_path += dir + "/"
            self.create_dir(total_path)

    def generate_file_names_to_upload(self, photos_dict, folder_name):
        file_names = []
        for key, value in photos_dict.items():
            file_name = f"{folder_name}/{value['likes_count']}.{value['img_type']}"
            if file_name in file_names:
                file_name = f"{folder_name}/{value['likes_count']}_{value['date']}.{value['img_type']}"
            file_names.append(file_name)
            value.setdefault("file_name", file_name)
        return photos_dict

    def save_vk_photos_to_ya_disk(self, vk_token, vk_user_id, photo_count):
        vk_connection = vk.VkDownloader(vk_token)
        file_name = "photos.json"
        folder_name = "VK_photos"
        vk_connection.save_photos_info_to_file(vk_user_id, file_name)
        photos_dict = vk_connection.get_photos_by_size_from_file(file_name)
        photos_dict = self.generate_file_names_to_upload(photos_dict, folder_name)
        # сортировка ид по размеру фото
        dict_for_sort = {}
        for key, value in photos_dict.items():
            dict_for_sort[key] = value["size_px"]
        photos_ids_sorted_by_size = list({k: dict_for_sort[k] for k in sorted(dict_for_sort, key=dict_for_sort.get, reverse=True)}.keys())

        if photo_count > len(photos_dict):
            count = len(photos_dict)
        else:
            count = photo_count
        self.create_dir(folder_name)
        for id in photos_ids_sorted_by_size[:count]:
            self.upload_by_url(photos_dict[id]["file_name"], photos_dict[id]["url"])
            with open("result.json", "a") as result:
                json.dump(photos_dict[id], result)
                result.write("\n")
