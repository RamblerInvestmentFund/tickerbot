import os
import re
import time
from pathlib import Path
from pprint import pprint

from slack_sdk import WebClient

import pdf

# for RIF slack...
TICKERBOT = "U030PM1HAEM"
AUTHORS = ['Matt Hyatt']


def build_bot():
    """builds slack WebClient ... easy to read"""
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    return client


def get_channels(*, client):
    response = client.conversations_list(
        limit=999, types=["public_channel", "private_channel"]
    )  # 'mpim', 'im'])
    channels = response["channels"]

    names = [channel["name"] for channel in channels]
    ids = [channel["id"] for channel in channels]

    data = {name: id for name, id in zip(names, ids)}
    return data


def check_mention(*, client, dm):
    """
    checks to see if the client is mentioned in the chat
    """

    mention = "<@U030PM1HAEM>"

    history = client.conversations_history(channel=dm).data
    messages = history["messages"]
    last_message = messages[0]["text"]
    ticker = last_message.replace(mention, "").split(" ")[-1].upper()

    return ticker if mention in last_message else False


def get_name(*, client, uid):
    return client.users_info(user=uid)["user"]["real_name"]


def get_dm_info(*, client):
    response = client.conversations_list(limit=999, types=["im"])
    dms = [
        {
            "dm": channel["id"],
            "user": get_name(client=client, uid=channel["user"]),
            "uid": channel["user"],
        }
        for channel in response["channels"]
    ]
    return dms


def send_report(*, client, dm, ticker):
    """sends a pdf ticker report"""

    pdf.generate_report(ticker)

    # send report
    response = client.files_upload(channels=dm, file=f"{ticker}-report.pdf")

    # cleanup
    p = Path(__file__).parent
    files = [x for x in p.iterdir() if f'{ticker}-' in x.name]
    [os.remove(file) for file in files]


def main():

    print('running tickerbot...')
    client = build_bot()

    while True:
        dms = [item['dm'] for item in get_dm_info(client=client)]

        for dm in dms:

            try:
                ticker = check_mention(client=client, dm=dm)
                if ticker:
                    print(ticker)
                    client.chat_postMessage(
                        channel=dm, text=f"generating {ticker} report... (eta 1min)"
                    )
                    send_report(client=client, dm=dm, ticker=ticker)
            except Exception as ex:
                print("error")
                print(ex)
                print()
                client.chat_postMessage(channel=dm, text=f"error ... please contact {AUTHORS}")

            time.sleep(1.2)  # tier 3 feature

        '''
        request limits:
            tier 2
                20+ per minute
            tier 3
                50+ per minute
        '''


if __name__ == "__main__":
    main()


def sandbox():
    """snippets i was trying out"""

    quit()
