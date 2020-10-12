"""The EVGR Mixer App randomly pairs users in a channel

Will only run if there are >= 2 members in a channel
If there is an odd number of users, one pair will have a third user added
"""
import os
import logging
import random
from slack import WebClient
from slack.errors import SlackApiError

logging.basicConfig(level=logging.DEBUG)

# evgr token provided as environment variable by Google Cloud
TOKEN = os.environ['TOKEN']

# channel to pull member list from
MEMBER_CHANNEL = 'C01BK0926V8' # evgr-randomcoffees
# MEMBER_CHANNEL = 'C019ZHSR78W' # evgr-test

# channel to post message
POST_CHANNEL = '#evgr-randomcoffees'

client = WebClient(token=TOKEN)

def get_channel_users(channel):
    """Retrieve a list of the users in a channel"""
    try:
        response = client.conversations_members(channel=channel)
    except SlackApiError as err:
        assert err.response["error"]
    user_ids = response["members"]
    return user_ids

def filter_bots(users):
    """Remove bots from list of users"""
    human_users = []
    for user in users:
        user_info = client.users_info(user=user)['user']
        if not user_info['is_bot']:
            human_users.append(user)
    return human_users

def group_users(users):
    """Shuffle users and organize them into pairs"""
    random.shuffle(users)
    buddy_groups = None
    if len(users) > 1:
        buddy_groups = [users[i: i+2] for i in range(0, len(users), 2)]
        if len(users) % 2 > 0 and len(buddy_groups) > 1:
            buddy_groups[-2].extend(buddy_groups[-1])
            buddy_groups = buddy_groups[:-1]
    return buddy_groups

def post_message(buddy_groups, channel):
    """Post the groups in the channel"""
    resp = "Hi EVGR-mixers! :minion_wave: This week's random groups are as follows"
    for buddy_group in buddy_groups:
        resp += "\n:coffee: " + " & ".join([f"<@{buddy}>" for buddy in buddy_group])
    resp += "\nFind some time this week to connect with your random buddies "
    resp += ":blob_excited: :fireball:"

    try:
        response = client.chat_postMessage(channel=channel, mrkdwn=True, text=resp)
    except SlackApiError as err:
        assert err.response["error"]
    return response

def main(request):
    """Main entry point into the mixers app"""
    users = get_channel_users(MEMBER_CHANNEL)
    human_users = filter_bots(users)
    buddy_groups = group_users(human_users)
    if buddy_groups:
        resp = post_message(buddy_groups, POST_CHANNEL)
        ret = str(resp)
    else:
        ret = 'Not enough members to run'
    return ret

if __name__ == "__main__":
    main(None)
