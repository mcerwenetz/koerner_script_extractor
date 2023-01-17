import os
import pydub
import myzipfile
import shutil
import logging
import gc


def rename_all_pptx():

    all_files = os.listdir()

    for filename in all_files:
        
        if filename.endswith('.pptx'):
            logging.info(f"renaming filename {filename}")
            filename_without_suffix = filename.split(".")[0]
            filename_as_zip = filename_without_suffix + ".zip"
            shutil.copyfile(filename, filename_as_zip)


def extract_one_audio(zip_file: myzipfile.ZipFile, path: str):
    for filename in zip_file.namelist():
        if filename.endswith(".m4a"):
            logging.info(f"extracting all audios of file {filename}")

            try:
                zip_file.extract(filename, path=path)
                logging.info(f"extraced file {filename}")
            except Exception as e:
                logging.error(e)


def concat_all_audios(filepath, name):
    logging.info(f"concating all audios of chapter {filepath}")
    path = filepath + "/ppt/media/"
    max_file_count = 50
    filelist = ["media" + str(i) + ".m4a" for i in range(1, max_file_count)]
    filelist = [path + file for file in filelist]
    filelist = filter(lambda filename: os.path.isfile(filename), filelist)
    audios = [pydub.AudioSegment.from_file(
        file) for file in filelist]

    chapter_audio = pydub.AudioSegment.empty()
    for audio in audios:
        # logging.info(f"concatinating {audio}")
        chapter_audio = chapter_audio.append(audio, crossfade=0)
    chapter_audio.export(name+".mp3", format="mp3", bitrate="128k")
    logging.info("exported chapter")


def extract_all_audio_files():

    all_files = [str(i) + ".zip" for i in range(1, 100)]
    all_files = filter(lambda filename: os.path.isfile(filename), all_files)

    for idx, filename in enumerate(all_files):

        with myzipfile.ZipFile(filename) as zip_file:
            file_name_without_suffix = filename.split(".")[0]
            if not os.path.exists(file_name_without_suffix):
                os.mkdir(file_name_without_suffix)
            extract_one_audio(zip_file, file_name_without_suffix)
            concat_all_audios(filename.split(".")[0], str(idx+1))


def concat_all_chapters():
    logging.info("concatinating all chapters")
    files = [str(i) + ".mp3" for i in range(1, 100)]
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


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("copying pptx into zips")
    rename_all_pptx()
    logging.info("extracting all audio files")
    extract_all_audio_files()
    concat_all_chapters()


if __name__ == '__main__':
    main()
