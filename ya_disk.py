# --*-- coding: UTF-8 --*--
"""Yandex disk integration module"""
import json
import os
import requests
from tqdm import tqdm
import vk
import configparser


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
        """Метод загружает файл по ссылке на яндекс диск

        Args:
            file_path(str): название файла на яндекс диске
            url(str): url к файлу, который нужно сохранить на ЯД

        Returns:
            result(str): Результат операции
        """
        if len(file_path.split("/")) > 1:
            data = requests.get(url).content
            response = requests.put(self.get_upload_url(file_path), data=data)
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

    @staticmethod
    def generate_file_names_to_upload(photos_dict: dict) -> dict:
        """Дополняет словарь с данными о фотографиях информацией о наименовании файла

        Args:
            photos_dict(dict): dict with photos upload info

        Returns:
            photos_dict(dict): dict with photos upload info
        """
        file_names = []
        for key, value in photos_dict.items():
            file_name = f"{value['likes_count']}.{value['img_type']}"
            if file_name in file_names:
                file_name = (
                    f"{value['likes_count']}_{value['date']}.{value['img_type']}"
                )
            file_names.append(file_name)
            value.setdefault("file_name", file_name)
        return photos_dict

    def save_vk_photos_to_ya_disk(self, vk_user_id: str, photo_count: int = 5) -> None:
        """Метод для сохранения фотографий из профиля пользователя VK на ЯД

        Args:
            vk_user_id(str): vk user info_dict
            photo_count(int): count of photos for upload
        """
        config = configparser.ConfigParser()
        config.read("config.ini")
        vk_connection = vk.VkDownloader(config.get("Vk", "service_token"))
        file_name = config.get("Vk", "photos_info_file_name")
        folder_name = config.get("Ya_disk", "folder_name")
        result_file_name = config.get("Ya_disk", "uploaded_files_list_file_name")

        vk_connection.save_photos_info_to_file(vk_user_id, file_name)
        photos_dict = vk_connection.get_photos_upload_info_from_file(file_name)
        photos_dict = self.generate_file_names_to_upload(photos_dict)
        dict_for_sort = {}
        for key, value in photos_dict.items():
            dict_for_sort[key] = value["size_px"]
        photos_ids_sorted_by_size = list(
            {
                k: dict_for_sort[k]
                for k in sorted(dict_for_sort, key=dict_for_sort.get, reverse=True)
            }.keys()
        )
        if photo_count > len(photos_dict):
            count = len(photos_dict)
        else:
            count = photo_count
        try:
            self.create_path(folder_name)
        except requests.exceptions.HTTPError:
            pass
        finally:

            for id in tqdm(
                photos_ids_sorted_by_size[:count],
                desc="File transfer progress",
            ):
                if folder_name is not None:
                    upload_file_name = f'{folder_name}/{photos_dict[id]["file_name"]}'
                else:
                    upload_file_name = photos_dict[id]["file_name"]
                self.upload_by_url(upload_file_name, photos_dict[id]["url"])
                result_record = {
                    "file_name": photos_dict[id]["file_name"],
                    "size": photos_dict[id]["size_type"],
                }
                self.record_result_to_file(result_file_name, result_record)

    @staticmethod
    def record_result_to_file(result_file_name: str, result_record: dict) -> None:
        """Метод для записи информации о файлах, загруженных на ЯД

        Args:
            result_file_name(str): output file name
            result_record(dict): dict with record info
        """
        if not os.path.isfile(result_file_name):
            with open(result_file_name, "w") as result:
                result.write("[]")
        json_data = json.load(open(result_file_name, encoding="utf-8"))
        json_data.append(result_record)
        json.dump(json_data, open(result_file_name, mode="w", encoding="utf-8"))
