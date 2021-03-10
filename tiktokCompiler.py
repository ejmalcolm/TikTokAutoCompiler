import sys
import requests
import time
import random
from os import listdir, makedirs
from shutil import rmtree
import moviepy.editor as mp
from TikTokApi import TikTokApi
from urllib.request import urlretrieve
from PIL import Image

api = TikTokApi()

def get_top_hashtag(hashtag, count, start=0):
    videoDicts = api.byHashtag(hashtag,count=start+count)
    return videoDicts[start:]

def get_by_trending(count, start=0):
    videoDicts = api.trending(count=start+count)
    return videoDicts[start:]

def download_from_videoDicts(videoDicts, folderName):
    """Do not put a / in folderName"""
    total = len(videoDicts)
    # create the folder
    rmtree(folderName, ignore_errors=True)
    makedirs(folderName)
    for ind, vd in enumerate(videoDicts):
        VID = vd['itemInfos']['id']
        video_dict = api.getTikTokById(VID)
        downloadLink = video_dict['itemInfo']['itemStruct']['video']['downloadAddr']
        print(f'Downloading {ind+1}/{total}')
        r = requests.get(downloadLink, allow_redirects=True)
        with open(folderName + f'/{VID}.mp3', 'wb') as f:
            f.write(r.content)
        time.sleep(2.5)

def combine_in_folder(folderName):
    """Do not put a / in folderName"""
    clips = []
    for vF in listdir(folderName + '/'):
        clip = mp.VideoFileClip(folderName + '/' + vF)
        clips.append(clip)
    concat_clip = mp.concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile('Videos/' + f'combined_from_{folderName}.mp4')
    rmtree(folderName)
    return True

def filter_to_length(videoDicts, length):
    """Length is in seconds"""
    durs = 0
    newList = []
    for video in videoDicts:
        duration = video['itemInfos']['video']['videoMeta']['duration']
        newList.append(video)
        durs += duration
        if length < durs:
            print(f'Length of cut video is: {durs}')
            return newList
    print(f'Length of cut video is: {durs}')
    return newList

# ! youtube upload ! #

import subprocess

def upload_to_youtube(subject, title):
    yaml_string = f"""
    videos:
    -
        title: {title}
        file:  Videos/combined_from_{subject}.mp4
        description: Brand new {subject} tiktok compilation of all your favorite {subject} tiktoks that I put together! really trying to find all the best tiktoks of 2020 and particularly the funniest {subject} tiktok videos I can find, we all know {subject} tiktok is much better than straight tiktok. "#{subject}" "#tiktok" "#compilation"
        category: Music
        privacy: private
        tags:
            - tiktok
            - compilation
            - tiktoks
            - tik tok
            - Tik Tok
            - {subject}

    secrets_path: ./client_secrets.json
    credentials_path:  ./credentials.json
    """
    # write the YAML file
    with open('videoUpload.yaml', 'w') as f:
        print(yaml_string, file=f)
    # call the video upload CMD process
    subprocess.call([r'videoUpload.bat'])

# ! thumbnail creation ! #

def create_thumbnail(videoDicts, subject):
    """Creates a random thumbnail from a list of videoDicts"""
    #creates a new empty image
    blank_thumbnail = Image.new('RGBA', (1280,720))
    subDicts = random.sample(videoDicts, 3)
    for ind, sd in enumerate(subDicts):
        coverLink = sd['itemInfos']['covers'][0]
        # save the image
        print(f'Downloading Thumbnail: {ind+1}/3')
        urlretrieve(coverLink, f'TempThumbnail/{ind+1}.png')
        # open the image in Pillow
        im = Image.open(f'TempThumbnail/{ind+1}.png')
        im.thumbnail((800, 750))
        # paste self onto the blank_thumbnail
        blank_thumbnail.paste(im, (427*ind,0))
    # add tiktok logo
    logo = Image.open('TempThumbnail/tiktokicon.png').convert('RGBA')
    x, y = logo.size
    blank_thumbnail.paste(logo, (0,0,x,y), logo)
    # save thumbnail
    blank_thumbnail.save(f'TempThumbnail/{subject}_thumbnail.png')
    return 'TempThumbnail/newest_thumbnail.png'

if __name__ == "__main__":
    # set the subject
    subjects = ['Hamilton']
    # the title
    titles = ['Hamilton 4']
    for subject, title in zip(subjects, titles):
        # amount of tiktoks
        print(subject,title)
        tiktoks = 60
        # # length in seconds
        length = 720
        # # get the starting dict
        init_dict = get_by_trending(60)
        # # filter the videos to given length
        filtered_dicts = filter_to_length(init_dict, length)
        # download all the videos into a folder
        download_from_videoDicts(filtered_dicts, subject)
        # combine them all together
        combine_in_folder(subject)
        # upload to youtube
        upload_to_youtube(subject, title)
        create_thumbnail(filtered_dicts, subject)