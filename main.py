import ya_disk


# vk_id = input("Enter VK user id: ")
# ya_disk_token = input("Enter yandex disk token: ")

vk_token = "958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008"
vk_user_id = "1"
ya_disk_connection = ya_disk.YaUploader("AQAAAAAKxoMyAADLW1WWW_YfukWwnbbM104GD48")
ya_disk_connection.save_vk_photos_to_ya_disk(vk_token, vk_user_id, 4)


