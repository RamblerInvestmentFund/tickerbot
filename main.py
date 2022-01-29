import os
import re
import time
from pprint import pprint

from slack_sdk import WebClient

import pdf

BOT_MEMBER_ID = "U030PM1HAEM"

SECTOR_MATERIALS = "CREMP7J77"
MATT_HYATT = "U02D6SFQ57Y"
ANTHONY_PETERS = "U01BWB9JQ2U"


def build_bot():
    """builds slack WebClient ... easy to read"""
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    return client


def get_ids(channels):
    names = [channel["name"] for channel in channels]
    ids = [channel["id"] for channel in channels]

    ids = {name: id for name, id in zip(names, ids)}
    return ids


def check_mention(*, client):
    """checks to see if the client is mentioned in the chat
    limited to SECTOR_MATERIALS atm
    """

    mention = "<@U030PM1HAEM>"

    history = client.conversations_history(channel=SECTOR_MATERIALS).data
    messages = history["messages"]
    last_message = messages[0]["text"]
    ticker = last_message.replace(mention, "").split(" ")[-1].upper()

    return ticker if mention in last_message else False


def send_report(*, client, ticker):
    """sends a pdf ticker report"""

    pdf.generate_report(ticker)

    # send report
    text = f"requested {ticker} report:"
    file = f"{ticker}-report.pdf"

    client.chat_postMessage(channel=SECTOR_MATERIALS, text=text)
    response = client.files_upload(channels=SECTOR_MATERIALS, file=file)

    # cleanup
    pass


def main():

    client = build_bot()

    while True:
        try:
            ticker = check_mention(client=client)
            if ticker:
                print(ticker)
                client.chat_postMessage(channel=SECTOR_MATERIALS,
                                        text='generating report... (eta 1min)')
                send_report(client=client, ticker=ticker)
            time.sleep(1)
        except:
            print('error')
            client.chat_postMessage(channel=SECTOR_MATERIALS, text='error')
            time.sleep(1)
            continue


if __name__ == "__main__":
    main()

"""NOTES:
- can only send messages in channels that the bot is in
"""


def sandbox():
    """snippets i was trying out"""

    client = build_bot()

    response = client.conversations_list(
        limit=999,
        types=[
            "public_channel",
            "private_channel",
        ],
    )  # 'mpim', 'im'])
    conversations = response["channels"]

    channels = [c["name"] for c in conversations]
    channels.sort()
