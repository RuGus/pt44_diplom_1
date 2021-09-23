# --*-- coding: UTF-8 --*--
"""Program for backup of VK user's photos to yandex Disk"""
import ya_disk

print("The program for backup of VK user's photos has been launched!!!")
print("---")
vk_user_id = input("Enter VK user id: ")
ya_disk_token = input("Enter yandex disk token: ")
print("---")
ya_disk_connection = ya_disk.YaUploader(ya_disk_token)
ya_disk_connection.save_vk_photos_to_ya_disk(vk_user_id)
