import yt_dlp
import sys
import logging
import os
import ffmpeg
from colorama import init, Fore, Style

logging.basicConfig(level=logging.INFO, format="%(message)s")
init(autoreset=True)

#
# Avassa
#


def download_indicator(data):
    if data["status"] == "finished":
        logging.info("Done downloading, now converting ...")
    elif data["status"] == "downloading":
        logging.info(
            f"Downloading: {data['_percent_str']} at {data['_speed_str']} ETA {data['_eta_str']}"
        )


# region Process and download
def process_queue(video_queue):
    for item in video_queue:
        url_dict = item[0]
        download_type = item[1]

        if download_type == "s":
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "logger": logging,
                "progress_hooks": [download_indicator],
            }
        elif download_type == "v":
            ydl_opts = {
                "format": "best",
                "merge_output_format": "mp4",
                "logger": logging,
                "progress_hooks": [download_indicator],
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = url_dict["url"]
            ydl.download(
                [url],
            )


# endregion


# region Search for results and add to queue
def search_and_add(video_name, queue):
    query = video_name
    url = f"ytsearch10:{query}"
    query = " ".join(video_name)
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }
    first_ten_results = dict()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)
        first_ten_results = extract_video_information(result["entries"])

    choice = get_user_input()

    if not choice:
        return
    tokens = choice.split(" ")

    queue.append([first_ten_results[f"{tokens[0]}"], tokens[1]])
    logging.info(
        Fore.GREEN + "The selected song has successfully added to download queue..."
    )
    # logging.info(
    #   f"Current state of queue:\n{queue}",
    # )


# endregion


# region Extract video info
def extract_video_information(video_dict):
    first_ten_results = dict()

    for number, video in enumerate(video_dict):

        video_title = video["title"]
        url = video["url"]
        video_description = Fore.YELLOW + f"{number+1}- " + f"{video_title}"
        if video.get("duration"):
            video_description += (
                Fore.BLUE + f"\nDuration = {get_duration(int(video['duration']))}"
            )
            logging.info(video_description)
            logging.info(Fore.RESET + "-" * 40)

        first_ten_results[f"{number+1}"] = {"url": video["url"]}

    return first_ten_results


# endregion


# reigon Get user input
def get_user_input():
    choice = input(
        "Please select one of the shown videos above you wish to download [1-10]...(To search again, leave blank)\t"
    )

    if not choice:
        return None
    else:
        choice = int(choice)
        if not isinstance(choice, int):
            raise ValueError("Illegal argument... Input an integer value.")
        else:
            if choice in range(0, 11):
                download_type = input(
                    Fore.GREEN
                    + "Select the download type v for video, s for sound only...\t"
                )
                if download_type and (download_type == "v" or download_type == "s"):
                    return str(choice) + " " + download_type
                else:
                    raise ValueError(
                        "Illegal argument, please select the values as demonstrated."
                    )
            else:
                raise ValueError("Please select a video inside 1-10 range.")


# endregion


# region get_duration
def get_duration(duration):
    mins = str(duration // 60)
    seconds = str(duration % 60)
    if len(seconds) == 1:
        seconds = "0" + seconds
    return f"{mins}:{seconds}"


# endregion

# region main


def main():
    queue = list()
    while 1:
        video_name = input(
            Fore.WHITE
            + "Please enter a video name... (Leave blank if you're done) \n"
            + Fore.RESET
        )
        if not video_name:
            break
        search_and_add(video_name, queue)
    process_queue(queue)
    logging.info(Fore.RESET + "Done...")
    return 0


# endregion

if __name__ == "__main__":
    main()
