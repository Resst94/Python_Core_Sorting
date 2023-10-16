import os
import shutil
import zipfile
import re
import sys
from pathlib import Path

# Transliterates the Cyrillic alphabet into Latin 

UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()


def normalize(name):
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', "_", new_name)
    return f"{new_name}.{'.'.join(extension)}"

images_files = list()
video_files = list()
doc_files = list()
audio_files = list()
archives = list()
folders = list() 
others = list()
known_extensions = set()
unknown_extensions = set()

file_extensions = {
        'images': images_files,
        'video': video_files,
        'documents': doc_files,
        'audio': audio_files,
        'archives': archives,
        'others': others
        }

def get_extensions(file_name):
    return Path(file_name).suffix[1:].lower()

def process_folder(folder):
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        normalized_item = normalize(item)
        

        if os.path.isfile(item_path):
            extension = item.split('.')[-1].lower()
            
            if extension in ('jpeg', 'png', 'jpg', 'svg'):
                images_files.append(item)
                known_extensions.add(extension)
                shutil.move(item_path, os.path.join('images', normalized_item))

            elif extension in ('avi', 'mp4', 'mov', 'mkv'):
                video_files.append(item)
                known_extensions.add(extension)
                shutil.move(item_path, os.path.join('video', normalized_item))

            elif extension in ('doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'):
                doc_files.append(item)
                known_extensions.add(extension)
                shutil.move(item_path, os.path.join('documents', normalized_item))

            elif extension in ('mp3', 'ogg', 'wav', 'amr'):
                audio_files.append(item)
                known_extensions.add(extension)
                shutil.move(item_path, os.path.join('audio', normalized_item))

            elif extension in ('zip', 'gz', 'tar'):
                archives.append(item)
                known_extensions.add(extension)
                archive_folder = os.path.join('archives', normalized_item.rsplit('.', 1)[0])
                if zipfile.is_zipfile(item_path):
                    with zipfile.ZipFile(item_path, 'r') as zip_ref:
                        zip_ref.extractall(archive_folder)

                else:
                    print(f"Skipping {item}: Not a valid zip file")
                os.remove(item_path)

            else:
                unknown_extensions.add(extension)
                others.append(item)
                shutil.move(item_path, os.path.join('others',normalized_item))

        elif os.path.isdir(item_path):
            # Recursively process nested folders
            if item not in ('images', 'video', 'documents', 'audio', 'archives', 'others'):
                process_folder(item_path)
                folders.append(item)
                continue
            else:
                shutil.rmtree(item_path)
        else:
            # We ignore symbolic links and other special files
            continue


def remove_empty_folders(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if not os.listdir(folder_path):
                os.rmdir(folder_path)

def main(source_folder):
    os.makedirs('images', exist_ok=True)
    os.makedirs('video', exist_ok=True)
    os.makedirs('documents', exist_ok=True)
    os.makedirs('audio', exist_ok=True)
    os.makedirs('archives', exist_ok=True)
    os.makedirs('others', exist_ok=True)

    process_folder(source_folder)
    remove_empty_folders(source_folder)
    
    print(f"Images: {images_files}\n")
    print(f"Video: {video_files}\n")
    print(f"Documents: {doc_files}\n")
    print(f"Audio: {audio_files}\n")
    print(f"Archives: {archives}\n")
    print(f"Unknown Extensions: {unknown_extensions}\n")
    print(f"Others: {others}\n")
    print(f"Known Extensions: {known_extensions}\n")

if __name__ == "__main__":
    source_folder = sys.argv[1]
    main(source_folder)


    