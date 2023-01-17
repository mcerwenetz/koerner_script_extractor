import os
import pydub
import myzipfile
import shutil
import logging
import gc
import tracemalloc
import threading
import time 

MAX_AUDIO_FILES_PER_PPT = 100
INPUT_PATH_PREFIX = "in"
OUTPUT_PATH_PREFIX = "out"

def check_mem():
    tracemalloc.start()
        
    while True:
        current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
        time.sleep(0.1)
    tracemalloc.stop()
    


def rename_all_pptx():

    all_files = os.listdir(INPUT_PATH_PREFIX)

    for filename in all_files:

        if filename.endswith('.pptx'):
            filename_without_suffix = filename.split(".")[0]
            source_file_path = os.sep.join([INPUT_PATH_PREFIX, filename])
            filename_as_zip = filename_without_suffix + ".zip"
            dest_file_path = os.sep.join([INPUT_PATH_PREFIX, filename_as_zip])
            logging.info(f"renaming filename {filename}")
            shutil.copyfile(source_file_path, dest_file_path)


def extract_one_audio(zip_file: myzipfile.ZipFile, path: str):
    logging.info(f"extracting all audios of file {path}")

    for filename in zip_file.namelist():
        if filename.endswith(".m4a"):

            try:
                zip_file.extract(filename, path=path)
                # logging.info(f"extraced file {filename}")
            except Exception as e:
                logging.error(e)


def concat_all_audios(filepath, file_name):
    logging.info(f"concating all audios of chapter {filepath}")
    path = filepath + "/ppt/media/"
    filelist = ["media" + str(i) + ".m4a" for i in range(1, MAX_AUDIO_FILES_PER_PPT)]
    filelist = [path + file for file in filelist]
    filelist = filter(lambda filename: os.path.isfile(filename), filelist)
    audios = [pydub.AudioSegment.from_file(
        file) for file in filelist]

    chapter_audio = pydub.AudioSegment.empty()
    # for audio in audios:
        # logging.info(f"concatinating {audio}")
        # chapter_audio = chapter_audio.append(audio, crossfade=0)
    output_file_path = os.sep.join([OUTPUT_PATH_PREFIX, file_name])
    chapter_audio.export(output_file_path+".mp3", format="mp3", bitrate="128k")
    logging.info("exported chapter")


def cleanup(folder_name):
    logging.info("cleaning up temporary files")
    file_name = folder_name + ".zip"
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    if os.path.isfile(file_name):
        os.remove(file_name)


def extract_all_audio_files():

    all_files = sorted(os.listdir(INPUT_PATH_PREFIX))
    zip_files = filter(lambda filename: filename.endswith(".zip"), all_files)

    for idx, filename in enumerate(zip_files):

        file_path = os.sep.join([INPUT_PATH_PREFIX, filename])
        with myzipfile.ZipFile(file_path) as zip_file:
            folder_name = filename.split(".")[0]
            folder_path = os.sep.join([INPUT_PATH_PREFIX,folder_name])
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
            extract_one_audio(zip_file, folder_path)
            concat_all_audios(folder_path, folder_name)
            cleanup(folder_path)


def concat_all_chapters():
    logging.info("concatinating all chapters")
    files = [str(i) + ".mp3" for i in range(1, MAX_AUDIO_FILES_PER_PPT)]
    files = filter(lambda filename: os.path.isfile(filename), files)

    logging.info("reading all audios")
    audios = [pydub.AudioSegment.from_file(
        file) for file in files if file.endswith(".mp3")]
    chapter_audio = pydub.AudioSegment.empty()
    for idx, audio in enumerate(audios):
        logging.info(f"concatinating chapter {idx+1}")
        chapter_audio = chapter_audio.append(audio, crossfade=0)
        # logging.info(f"concatinated {chapter_audio}")
    logging.info("everything appended\nexporting")
    del audios
    gc.collect()
    chapter_audio.export("full"+".mp3", format="mp3", bitrate="128k")
    logging.info("finished concatinating everything")


def create_structure():
    if not os.path.exists(INPUT_PATH_PREFIX):
        os.mkdir(INPUT_PATH_PREFIX)
    if not os.path.exists(OUTPUT_PATH_PREFIX):
        os.mkdir(OUTPUT_PATH_PREFIX)


def main():
    threading.Thread(target=check_mem).start()
    # logging.basicConfig(level=logging.INFO)
    logging.info("creating folder structure if necessary")
    create_structure()
    logging.info("copying pptx into zips")
    rename_all_pptx()
    logging.info("extracting all audio files")
    extract_all_audio_files()
    # concat_all_chapters()


if __name__ == '__main__':
    main()
