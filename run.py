app = 'Dynamics-Theme'
version = 'v1.2'
git_nickname = "Falbue"
installer = 'installer'
repo_installer = f"{git_nickname}/{installer}"
repo_app = f'{git_nickname}/{app}'

# библиотеки
import requests
import os
import sys

# пути
user_folder = os.path.expanduser('~')  # Получаем путь к папке пользователя
install_path = os.path.join(user_folder, 'Falbue')
installer_path = os.path.join(install_path, installer)
app_path = os.path.join(install_path, app)


# модули
def latest_version(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url)
    
    if response.status_code == 200:
        release_info = response.json()
        version = release_info['tag_name']
    else:
        version = '0'

    return version

def download_repository(app, folder_path):
    def download_file(file_url, file_name): 
        with open(file_name, 'wb') as f:
            f.write(requests.get(file_url).content)
        print(f"Загрузка: {file_name}")

    def download_files_from_github_in_dir(dir_name, dir_path): 
        api_url = f"https://api.github.com/repos/{git_nickname}/{installer}/contents/{dir_name}"
        response = requests.get(api_url)
        files_in_dir = response.json()
        
        for file_in_dir in files_in_dir:
            if file_in_dir['type'] == 'file': 
                file_path = os.path.join(dir_path, file_in_dir['name'])
                download_file(file_in_dir['download_url'], file_path)

    api_url = f"https://api.github.com/repos/{git_nickname}/{installer}/contents"
    response = requests.get(api_url)
    files = response.json()
    
    for file in files:
        file_path = os.path.join(folder_path, file['name'])
        if file['type'] == 'file': 
            download_file(file['download_url'], file_path)
        elif file['type'] == 'dir': 
            os.makedirs(file_path, exist_ok=True)
            download_files_from_github_in_dir(file['path'], file_path)


def create_folder(folder_name):
    user_folder = os.path.expanduser('~')  # Получаем путь к папке пользователя
    install_path = os.path.join(user_folder, 'Falbue')
    # Создаем папку для сохранения файлов на рабочем столе.
    folder_path = os.path.join(install_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

latest_version = latest_version(repo_app)
if version == str(latest_version):
    print("Последняя верия")
    import DynamicsTheme # запуск основного кода

else:
    print(f"Последняя найденная верия: {str(latest_version)}")
    if os.path.exists(installer_path):
        print("Установщик установлен!")
    else:
        create_folder(installer_path)
        download_repository(installer, installer_path)


    file_name = "confinst.flb"
    file_path = os.path.join(installer_path, file_name)
    # Создание файла и запись текста в него
    with open(file_path, "w", encoding='utf-8') as file:
        file.write(app)

    sys.path.append(installer_path)        
    import main # запуск основного кода