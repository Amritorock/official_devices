#!/usr/bin/env python
#
# Python code which automatically posts Message in a Telegram Group if any new update is found.
# Intended to be run on every push
# USAGE : python3 post.py
# See README for more.
#
# Copyright (C) 2022 PrajjuS <theprajjus@gmail.com>
#
# Credits: Ashwin DS <astroashwin@outlook.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation;
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import re
import telebot
import os
import json
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
from NoobStuffs.libtelegraph import TelegraphHelper

# Get configs from workflow secrets
def getConfig(config_name: str):
    return os.getenv(config_name)
try:
    BOT_TOKEN = getConfig("BOT_TOKEN")
    CHAT_ID = getConfig("CHAT_ID")
    PRIV_CHAT_ID = getConfig("PRIV_CHAT_ID")
    STICKER_ID =  getConfig("STICKER_ID")
    BANNER_URL = getConfig("BANNER_URL_U")
    ELIXIR_VERSION_CHECK = getConfig("ELIXIR_VERSION_CHECK")
except KeyError:
    print("Fill all the configs plox..\nExiting...")
    exit(0)

try:
    NOTES = getConfig("NOTES")
except:
    NOTES = None

# Init bot
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Init telegraph
telegraph = TelegraphHelper("Project-Elixir", "https://t.me/projectelixir_bot")

# File directories
jsonDir = "builds"
idDir = ".github/scripts"

# Get elixir verion using regex
def get_elixir_version(filename: str):
    version_regex = r"^ProjectElixir_([0-9]{1,2}\.[0-9]+)_.+(?:zip|img|xz)$"
    match = re.search(version_regex, filename)
    return match.group(1)

# Store IDs in a fileto compare
def update(IDs):
    with open(f"{idDir}/file_ids.txt", "w+") as log:
        for ids in IDs:
            log.write(f"{str(ids)}\n")

# Return IDs of all latest files from json files
def get_new_id():
    files = []
    file_id = []
    for all in os.listdir(jsonDir):
        files.append(all)
    for all_files in files:
        with open(f"{jsonDir}/{all_files}", "r") as file:
            data = json.loads(file.read())
            file_id.append(data['id'])
    return file_id

# Return previous IDs
def get_old_id():
    old_id = []
    with open(f"{idDir}/file_ids.txt", "r") as log:
        for ids in log.readlines():
            old_id.append(ids.replace("\n", ""))
    return old_id

# Remove elements in 2nd list from 1st, helps to find out which device got an update
def get_diff(new_id, old_id):
    first_set = set(new_id)
    sec_set = set(old_id)
    return list(first_set - sec_set)

# Grab needed info using ID of the file
def get_info(ID):
    files = []
    for all in os.listdir(jsonDir):
        files.append(all)
    for all_files in files:
        with open(f"{jsonDir}/{all_files}", "r") as file:
            data = json.loads(file.read())
            if data['id'] == ID:
                device = all_files
                break
    with open(f"{jsonDir}/{device}") as device_file:
        info = json.loads(device_file.read())
        ANDROID_VERSION = info['version']
        ELIXIR_VERSION = get_elixir_version(info['filename'])
        DEVICE_NAME = info['device_name']
        CODENAME =  info['device']
        MAINNTAINER = info['tg_username']
        try:
            XDA = info['xda_thread']
        except KeyError:
            XDA = None
        DOWNLOAD_URL = info['url']
        DATE_TIME = datetime.datetime.fromtimestamp(int(info['datetime']))
        MD5 = info['filehash']
        SIZE = round(int(info['size'])/1000000000, 2)
        msg = ""
        msg += f"Project Elixir {ELIXIR_VERSION}\n"
        msg += f"Android Version: {ANDROID_VERSION}\n"
        msg += f"Device Name: {DEVICE_NAME} ({CODENAME})\n"
        msg += f"Maintainer: {MAINNTAINER}\n"
        msg += f"Date Time: {DATE_TIME}\n"
        msg += f"Download URL: {DOWNLOAD_URL}\n"
        msg += f"Size: {SIZE}G\n"
        msg += f"MD5: {MD5}\n"
        msg += f"XDA Thread: {XDA}\n"
        print(msg)
        return {
            "android_version": ANDROID_VERSION,
            "elixir_version": ELIXIR_VERSION,
            "device_name": DEVICE_NAME,
            "codename": CODENAME,
            "maintainer": MAINNTAINER,
            "datetime": DATE_TIME,
            "size": SIZE,
            "download": DOWNLOAD_URL,
            "md5": MD5,
            "xda": XDA
        }

# Prepare function for posting message in channel
def send_post(chat_id, image, caption, button):
    if caption == "" or not caption or caption is None:
        return bot.send_photo(chat_id=chat_id, photo=image, reply_markup=button)
    else:
        return bot.send_photo(chat_id=chat_id, photo=image, caption=caption, reply_markup=button)

# Prepare message format for channel
def message_content(information):
    msg = ""
    msg += f"<b>Project Elixir OFFICIAL - Android {information['android_version']} Update</b>\n\n"
    msg += f"<b>Device:</b> <code>{information['device_name']} ({information['codename']})</code>\n"
    msg += f"<b>Maintainer:</b> <a href='https://t.me/{information['maintainer']}'>{information['maintainer']}</a>\n"
    msg += f"<b>Rom Version:</b> <code>{information['elixir_version']}</code>\n"
    msg += f"<b>Build Date:</b> <code>{information['datetime']} UTC</code>\n\n"
    msg += f"<b>Source Changelogs:</b> <a href='https://projectelixiros.com/changelog'>Here</a>\n"
    msg += f"<b>Device Changelogs:</b> <a href='https://github.com/ProjectElixir-Devices/Changelogs/blob/UNO/{information['codename']}.md'>Here</a>\n\n"
    msg += f"<b>Installation Guide:</b> <a href='https://github.com/ProjectElixir-Devices/Wiki/blob/UNO/{information['codename']}.md'>Here</a>\n" 
    msg += f"<b>Screenshots:</b> <a href='https://projectelixiros.com/gallery'>Here</a>\n"
    msg += f"<b>MD5:</b> <code>{information['md5']}</code>\n"
    if NOTES is not None and len(NOTES) > 1:
        msg += f"\n<b>Notes:</b>\n"
        for LINES in NOTES.split('\n'):
            msg+=f"<b>•</b> <code>{LINES}</code>\n"
    msg += f"\n<b>Do consider donating if you want to appreciate our work</b>\n<b>UPI:</b> <code>dwarmachine24@oksbi</code>\n<b>PayPal:</b> https://www.paypal.me/uglykid24\n<b>Patreon:</b> https://www.patreon.com/join/uglykid24\n<b>BMC:</b> https://www.buymeacoffee.com/uglykid"
    return msg

# Prepare buttons for message
def button(information):
    buttons = InlineKeyboardMarkup()
    if information['xda'] is None:
        buttons.row_width = 2
        button1 = InlineKeyboardButton(text="Channel", url=f"https://t.me/Elixir_Updates")
        button2 = InlineKeyboardButton(text="Support", url=f"https://t.me/Elixir_Discussion")
        button3 = InlineKeyboardButton(text="Download", url=f"https://projectelixiros.com/download")
        return buttons.add(button1, button2, button3)
    else:
        buttons.row_width = 3
        button1 = InlineKeyboardButton(text="Channel", url=f"https://t.me/Elixir_Updates")
        button2 = InlineKeyboardButton(text="XDA", url=f"{information['xda']}")
        button3 = InlineKeyboardButton(text="Support", url=f"https://t.me/Elixir_Discussion")
        button4 = InlineKeyboardButton(text="Download", url=f"https://projectelixiros.com/download")
        return buttons.add(button1, button2, button3, button4)

# Send updates to channel and commit changes in repo
def tg_message():
    commit_message = "Update new IDs and push OTA"
    commit_description = "Data for following device(s) were changed:\n"
    if len(get_diff(get_new_id(), get_old_id())) == 0:
        print("All are Updated\nNothing to do\nExiting...")
        tg_log()
        sleep(2)
        exit(1)
    else:
        print(f"IDs Changed:\n{get_diff(get_new_id(), get_old_id())}\n")
        for devices in get_diff(get_new_id(), get_old_id()):
            info = get_info(devices)
            if STICKER_ID:
                bot.send_sticker(CHAT_ID, STICKER_ID)
                send_post(CHAT_ID, BANNER_URL, message_content(info), button(info))
            else:
                send_post(CHAT_ID, BANNER_URL, message_content(info), button(info))
            commit_description += f"- {info['device_name']} ({info['codename']})\n"
            sleep(5)
    update(get_new_id())
    open("commit_mesg.txt", "w+").write(f"Elixir: {commit_message} [BOT]\n\n{commit_description}")

# Prepare function for posting message in private group
def send_log(chat_id, text):
    return bot.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True)

def send_log_button(chat_id, text, button):
    return bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=button,
        disable_web_page_preview=True
    )

# Get all the devices which are in official repo
def get_devices():
    files = []
    devices = []
    for all in os.listdir(jsonDir):
        files.append(all)
    for all_files in files:
        with open(f"{jsonDir}/{all_files}", "r") as file:
            data = json.loads(file.read())
            if data['is_active']:
                devices.append({
                    "device_name": data['device_name'],
                    "codename": data['device'],
                    "maintainer": data['tg_username'],
                    "elixir_version": get_elixir_version(data['filename'])
                })
    return devices

# Prepare log format for private group
def tg_log():
    Updated = []
    YetToUpdate = []
    buttons = InlineKeyboardMarkup()
    for device in get_devices():
        if device['elixir_version'] == ELIXIR_VERSION_CHECK:
            Updated.append(device)
        else:
            YetToUpdate.append(device)
    count = 1
    msg = ""
    msg += f"<b>Project Elixir Devices UpsideDownCake Update Status</b><br><br>"
    msg += f"<b>The following devices have been updated to the version</b> <code>{ELIXIR_VERSION_CHECK}</code> <b>in the current month:</b> "
    if len(Updated) == 0:
        msg += f"<code>None</code>"
    else:
        for device in Updated:
            msg += f"<br><b>{count}.</b> <code>{device['device_name']} ({device['codename']})</code> <b>-</b> <a href='https://t.me/{device['maintainer']}'>{device['maintainer']}</a>"
            count += 1
    msg += "<br><br>"
    count = 1
    msg += f"<b>The following devices have not been updated to the version</b> <code>{ELIXIR_VERSION_CHECK}</code> <b>in the current month:</b> "
    if len(YetToUpdate) == 0:
        msg += f"<code>None</code>"
    else:
        for device in YetToUpdate:
            msg += f"<br><b>{count}.</b> <code>{device['device_name']} ({device['codename']})</code> <b>-</b> <a href='https://t.me/{device['maintainer']}'>{device['maintainer']}</a>"
            count += 1
    msg += "<br><br>"
    msg += f"<b>Total Official Devices:</b> <code>{str(len(get_devices()))}</code><br>"
    msg += f"<b>Updated during current month:</b> <code>{str(len(Updated))}</code><br>"
    msg += f"<b>Not Updated during current month:</b> <code>{str(len(YetToUpdate))}</code><br><br>"
    msg += f"<b>Information as on:</b> <code>{str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M'))} hours (UTC)</code>"
    text = f"<b>Project Elixir Devices UpsideDownCake (v{ELIXIR_VERSION_CHECK}) Update Status</b>\n\n"
    text += f"<b>Total Official Devices:</b> <code>{str(len(get_devices()))}</code>\n"
    text += f"<b>Updated during current month:</b> <code>{str(len(Updated))}</code>\n"
    text += f"<b>Not Updated during current month:</b> <code>{str(len(YetToUpdate))}</code>\n"
    text += f"<b>Information as on:</b> <code>{str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M'))} hours (UTC)</code>"
    telegph_url = telegraph.create_page(title="Device Update Status", content=msg)
    button1 = InlineKeyboardButton("More Info", telegph_url['url'].replace("telegra.ph", "graph.org"))
    buttons.add(button1)
    send_log_button(PRIV_CHAT_ID, text, buttons)

# Final stuffs
tg_message()
tg_log()
print("Successfull")
sleep(2)
