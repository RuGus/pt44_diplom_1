# --*-- coding: UTF-8 --*--
"""VK integration module"""
import datetime
import json
import requests


class VkDownloader:
    def __init__(self, token: str) -> None:
        """Initialize object

        Args:
            token(str): vk access token
        """
        self.token = token

    def get_photos_info(self, user_id: str) -> dict:
        """Get photos info to dict

        Args:
            user_id(str): VK user id

        Returns:
            info_dict(dict): dict of photos info from response of VK API request
        """
        url = "https://api.vk.com/method/photos.get"
        params = {
            "owner_id": user_id,
            "access_token": self.token,
            "v": "5.131",
            "album_id": "profile",
            "extended": "1",
        }
        response = requests.get(url, params)
        info_dict = response.json()["response"]["items"]
        return info_dict

    def save_photos_info_to_file(self, user_id: str, file_name: str) -> None:
        """Save photos info to json file

        Args:
            user_id(str): VK user id
            file_name(str): output file name
        """
        with open(file_name, "w") as file:
            json.dump(self.get_photos_info(user_id), file)

    @staticmethod
    def get_photos_full_info_from_file(file_name: str) -> dict:
        """Load photos info from json file

        Args:
            file_name(str): input json file name

        Returns:
            info_dict(dict): dict of photos info from json file
        """
        with open(file_name) as file:
            info_dict = json.load(file)
        return info_dict

    def get_photo_max_size_by_type_from_file(
        self, photo_id: str, file_name: str
    ) -> tuple:
        """Get photo max size by type info from file

        Args:
            photo_id(str): photo id
            file_name(str): name of json file with photos info

        Returns:
            url(tuple): (size in px, url, size type)
        """
        info_dict = self.get_photos_full_info_from_file(file_name)
        # типы размеров в порядке убывания
        sizes_grades = {
            "w": 2560 * 2048,
            "z": 1080 * 1024,
            "y": int((807 ** 2) * 2 / 3),
            "r": int((510 ** 2) * 2 / 3),
            "q": int((320 ** 2) * 2 / 3),
            "p": int((200 ** 2) * 2 / 3),
            "o": int((130 ** 2) * 2 / 3),
            "x": int((604 ** 2) * 2 / 3),
            "m": int((130 ** 2) * 2 / 3),
            "s": int((75 ** 2) * 2 / 3),
        }
        for photo in info_dict:
            if photo_id == photo["id"]:
                for grade, size_px in sizes_grades.items():
                    for size in photo["sizes"]:
                        if size["type"] == grade:
                            url = (size_px, size["url"], size["type"])
                            return url

    def get_photo_max_size_by_size_from_file(
        self, photo_id: str, file_name: str
    ) -> tuple:
        """Get photo max size by size(px) info from file

        Args:
            photo_id(str): photo id
            file_name(str): name of json file with photos info

        Returns:
            url(tuple): (size in px, url, size type)
        """
        info_dict = self.get_photos_full_info_from_file(file_name)
        for photo in info_dict:
            if photo_id == photo["id"]:
                if (
                    int(photo["sizes"][0]["height"]) == 0
                    or int(photo["sizes"][0]["width"]) == 0
                ):
                    return self.get_photo_max_size_by_type_from_file(
                        photo_id, file_name
                    )
                max_size_index = 0
                for size in photo["sizes"]:
                    max_size = int(photo["sizes"][max_size_index]["height"]) * int(
                        photo["sizes"][max_size_index]["width"]
                    )
                    current_size = int(size["height"]) * int(size["width"])
                    if current_size > max_size:
                        max_size_index = photo["sizes"].index(size)
                max_size = int(photo["sizes"][max_size_index]["height"]) * int(
                    photo["sizes"][max_size_index]["width"]
                )
                url = (
                    max_size,
                    photo["sizes"][max_size_index]["url"],
                    photo["sizes"][max_size_index]["type"],
                )
                return url

    def get_photos_upload_info_from_file(self, file_name: str) -> dict:
        """Get photos upload info from file

        Args:
            file_name(str): name of json file with photos info

        Returns:
            photos_dict(dict): dict with photos upload info
        """
        info_dict = self.get_photos_full_info_from_file(file_name)
        photos_dict = {}
        for photo in info_dict:
            max_size_info = self.get_photo_max_size_by_size_from_file(
                photo["id"], file_name
            )
            photos_dict[photo["id"]] = {
                "size_px": max_size_info[0],
                "size_type": max_size_info[2],
                "likes_count": photo["likes"]["count"],
                "date": datetime.datetime.utcfromtimestamp(photo["date"]).strftime(
                    "%Y-%m-%d"
                ),
                "url": max_size_info[1],
                "img_type": max_size_info[1].split(".")[-1][:3],
            }
        return photos_dict
