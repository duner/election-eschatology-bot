import os
import random
import tweepy
from datetime import datetime, timezone, timedelta
import pytz
import time

ODDS = 3 if os.environ.get("ON_HEROKU", False) else 3
WAIT_FOR = 60 if os.environ.get("ON_HEROKU", False) else 3600

auth = tweepy.OAuthHandler(
    os.environ.get('TWITTER_CONSUMER_KEY'),
    os.environ.get('TWITTER_CONSUMER_SECRET')
)
auth.set_access_token(
    os.environ.get('TWITTER_ACCESS_TOKEN'),
    os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
)
api = tweepy.API(auth)


def get_timedelta_till_election():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(timezone.utc)
    poll_closing = datetime(2016, 11, 9, 0, tzinfo=timezone.utc)
    return poll_closing - now

def timedelta_by_total_periods(delta):
    seconds = delta.total_seconds()
    return {
        'total_hours': (seconds/60),
        'total_minutes': round(seconds/60),
        'total_seconds': seconds,
    }

def list_to_sentance(list):
    if len(list) is 2:
        return list[0] + " and " + list[1]
    else:
        return ", ".join(list[0:-1]) + " and " + list[-1]


def construct_string(delta, totals):
    days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
    now = datetime.now(timezone.utc)

    random_number = bool(random.getrandbits(1))
    beginnings = ['There are ', 'Only ', 'Thank god, there are only ', 'It’s almost over! Only ', "The election is almost over! Only ", ]
    endings = [
        ' until the first polls close on Election Day.',
        ' until the first major set of poll closings across America!',
        ' until this godforsaken election finally ends.',
        ' until this trainwreck of an election comes to an end.'
    ]
    middles = [
        "{:,} seconds".format(int(totals['total_seconds'])),
        "{:,} minutes".format(totals['total_minutes'])
    ]

    if now.hour == 0:
        middles.append("{:,} days".format(days))
    if now.minute == 0:
        middles.append("{:,} hours".format(totals['total_hours']))

    fancy_middle = []
    if days: fancy_middle.append("{:,} days".format(days))
    if hours: fancy_middle.append("{:,} hours".format(hours))
    if minutes: fancy_middle.append("{:,} minutes".format(minutes))

    middles.append(list_to_sentance(fancy_middle))

    print(middles)

    string = random.choice(beginnings) + random.choice(middles) + random.choice(endings)
    return string


def get_next_time_to_tweet():
    options = [
        datetime.replace(datetime.now() + timedelta(days=1), hour=0, minute=0, second=0),
        datetime.replace(datetime.now() + timedelta(hours=1), minute=0, second=0),
        datetime.replace(datetime.now() + timedelta(minutes=random.randint(1,59)), second=0),
    ]
    return random.choice(options)

def send_tweet(string):
    status = api.update_status(status=string)
    print("TWEETED: " + string)

def main():
    have_i_tweeted = False
    while not have_i_tweeted:
            tweet_at = get_next_time_to_tweet()
            print("NEXT TWEET AT: " + tweet_at.isoformat())
            wait_to_tweet = tweet_at - datetime.now()
            if wait_to_tweet.total_seconds() < WAIT_FOR: #dont wait more than one hour
                print("WAITING FOR " + str(wait_to_tweet.total_seconds()) + " SECONDS")
                time.sleep(wait_to_tweet.seconds)
                delta = get_timedelta_till_election()
                totals = timedelta_by_total_periods(delta)
                string = construct_string(delta, totals)
                if len(string) < 140:
                    send_tweet(string)
                    have_i_tweeted = True


if __name__ == "__main__":
    if random.choice(range(ODDS)) == 0:
        main()
    else:
        print("SKIPPING")
