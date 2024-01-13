import os
import shutil
import zipfile
import re
import sys

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


def create_directory(directory_path):
    os.makedirs(directory_path, exist_ok=True)


def process_image(item, item_path, normalized_item, source_folder):
    images_folder = os.path.join(source_folder, 'images')
    create_directory(images_folder)
    images_files.append(item)
    known_extensions.add('image')
    dest_path = os.path.join(images_folder, normalized_item)
    shutil.move(item_path, dest_path)


def process_video(item, item_path, normalized_item, source_folder):
    video_folder = os.path.join(source_folder, 'video')
    create_directory(video_folder)
    video_files.append(item)
    known_extensions.add('video')
    dest_path = os.path.join(video_folder, normalized_item)
    shutil.move(item_path, dest_path)


def process_document(item, item_path, normalized_item, source_folder):
    documents_folder = os.path.join(source_folder, 'documents')
    create_directory(documents_folder)
    doc_files.append(item)
    known_extensions.add('document')
    dest_path = os.path.join(documents_folder, normalized_item)
    shutil.move(item_path, dest_path)


def process_audio(item, item_path, normalized_item, source_folder):
    audio_folder = os.path.join(source_folder, 'audio')
    create_directory(audio_folder)
    audio_files.append(item)
    known_extensions.add('audio')
    dest_path = os.path.join(audio_folder, normalized_item)
    shutil.move(item_path, dest_path)


def process_archive(item, item_path, normalized_item, source_folder):
    archives_folder = os.path.join(source_folder, 'archives')
    create_directory(archives_folder)
    archives.append(item)
    known_extensions.add('archive')
    dest_path = os.path.join(archives_folder, normalized_item.rsplit('.', 1)[0])
    if zipfile.is_zipfile(item_path):
        with zipfile.ZipFile(item_path, 'r') as zip_ref:
            zip_ref.extractall(dest_path)
    else:
        print(f"Skipping {item}: Not a valid zip file")
    os.remove(item_path)


def process_other(item, item_path, normalized_item, source_folder):
    others_folder = os.path.join(source_folder, 'others')
    create_directory(others_folder)
    unknown_extensions.add('other')
    others.append(item)
    dest_path = os.path.join(others_folder, normalized_item)
    shutil.move(item_path, dest_path)


def process_folder(folder, source_folder):
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        normalized_item = normalize(item)

        if os.path.isfile(item_path):
            extension = item.split('.')[-1].lower()

            processors = {
                'jpeg': process_image,
                'png': process_image,
                'jpg': process_image,
                'svg': process_image,
                'avi': process_video,
                'mp4': process_video,
                'mov': process_video,
                'mkv': process_video,
                'doc': process_document,
                'docx': process_document,
                'txt': process_document,
                'pdf': process_document,
                'xlsx': process_document,
                'pptx': process_document,
                'mp3': process_audio,
                'ogg': process_audio,
                'wav': process_audio,
                'amr': process_audio,
                'zip': process_archive,
                'gz': process_archive,
                'tar': process_archive
            }

            processor = processors.get(extension, process_other)
            processor(item, item_path, normalized_item, source_folder)

        elif os.path.isdir(item_path):
            # Recursively process nested folders
            if item not in ('images', 'video', 'documents', 'audio', 'archives', 'others'):
                process_folder(item_path, source_folder)
                folders.append(item)
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


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 sort.py <source_folder>")
        sys.exit(1)

    source_folder = os.path.abspath(sys.argv[1])

    process_folder(source_folder, source_folder)
    remove_empty_folders(source_folder)

    print(f"\nImages: {images_files}\n")
    print(f"Video: {video_files}\n")
    print(f"Documents: {doc_files}\n")
    print(f"Audio: {audio_files}\n")
    print(f"Archives: {archives}\n")
    print(f"Unknown Extensions: {unknown_extensions}\n")
    print(f"Others: {others}\n")
    print(f"Known Extensions: {known_extensions}\n")

    print(" The folder is sorted \N{winking face}")
    print(" Thank you for using our sorter \N{saluting face}")
    print(" Have a nice day \N{smiling face with smiling eyes}")


if __name__ == "__main__":
    main()
