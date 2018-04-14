#!/usr/bin/env python3
import calendar
import collections
import datetime
import math
import os
import tweepy

import matplotlib.collections
import matplotlib.patches


# Not sure how to make this configurable
FONT_FAMILY = "Source Sans Pro"

DAYS_MAX = 7
HOURS_MAX = 24


def get_api_wrapper():
    auth = tweepy.OAuthHandler(
        os.environ["TWITTER_CONSUMER_KEY"],
        os.environ["TWITTER_CONSUMER_SECRET"]
    )
    auth.set_access_token(
        os.environ["TWITTER_ACCESS_TOKEN"],
        os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
    )
    return tweepy.API(auth)


def status_times_for(api, id):
    user = api.me() if id is None else api.get_user(id)
    utc_offset = user.utc_offset or 0

    delta = datetime.timedelta(seconds=utc_offset)

    cursor = tweepy.Cursor(
        api.user_timeline,
        id=id,

        # Reduce number of requests
        count=200,
        # Remove excess information
        trim_user=True,
        include_rts=False
    )
    for status in cursor.items():
        yield status.created_at + delta


def count_times(times):
    return collections.Counter((time.hour, time.weekday()) for time in times)


def patches_for(api, id):
    counts = count_times(status_times_for(api, id))

    maximum = max(counts.values())

    for xy, count in counts.items():
        # These metrics need improving to allow cross-user comparisons
        r = 0.4 * (count / maximum) + 0.05
        alpha = 0.1 + 0.8 * math.log(count, maximum)

        yield matplotlib.patches.Circle(
            xy,
            radius=r,
            facecolor=(0, 0, 0, alpha),
            linewidth=0
        )


def plot_punchcard(api, id, fig, ax):
    # Set axes ticks and labels
    ax.set_xlim(-0.5, HOURS_MAX - 0.5)
    ax.set_ylim(DAYS_MAX - 0.5, -0.5)
    ax.set_xticks(range(HOURS_MAX))
    ax.set_yticks(range(DAYS_MAX))
    ax.set_yticklabels(calendar.day_abbr)

    # Enable equal spacing for both axes
    ax.set_aspect("equal")

    # Disable extra axes spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Change axes appearance
    ax.spines["left"].set_color("#999999")
    ax.spines["bottom"].set_color("#999999")
    ax.tick_params(length=0, colors="#555555")

    # Plot patches for punchcard
    for patch in patches_for(api, id):
        ax.add_patch(patch)


if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt

    plt.rcParams["font.family"] = FONT_FAMILY

    parser = argparse.ArgumentParser()
    parser.add_argument("id", nargs="?",
                        help="ID or screen name of the user")
    parser.add_argument("-o", "--output", required=True,
                        type=argparse.FileType("wb"))
    args = parser.parse_args()

    api = get_api_wrapper()

    fig, ax = plt.subplots()
    plot_punchcard(api, args.id, fig, ax)

    plt.tight_layout()
    plt.savefig(args.output, bbox_inches="tight")
