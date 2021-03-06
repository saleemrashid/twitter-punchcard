#!/usr/bin/env python3
import calendar
import collections
import math
import os
import tweepy

import matplotlib.collections
import matplotlib.patches


DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tweepy_cache")

DAYS_MAX = 7
HOURS_MAX = 24


def get_api_wrapper(cache_dir):
    auth = tweepy.OAuthHandler(
        os.environ["TWITTER_CONSUMER_KEY"],
        os.environ["TWITTER_CONSUMER_SECRET"]
    )
    auth.set_access_token(
        os.environ["TWITTER_ACCESS_TOKEN"],
        os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
    )
    return tweepy.API(auth, cache=tweepy.FileCache(cache_dir))


def status_times_for(api, id):
    user = api.me() if id is None else api.get_user(id)

    cursor = tweepy.Cursor(
        api.user_timeline,
        id=id,

        # Reduce number of requests
        count=200,
        # Remove excess information
        trim_user=True,
        include_rts=False
    )

    return (status.created_at for status in cursor.items())


def count_times(times):
    return collections.Counter((time.hour, time.weekday()) for time in times)


def patches_for(api, id):
    counts = count_times(status_times_for(api, id))

    maximum = max(counts.values())

    for xy, count in counts.items():
        # These metrics need improving to allow cross-user comparisons
        r = 0.4 * (count / maximum) + 0.1
        alpha = 0.2 + 0.8 * math.log(count, maximum)

        yield matplotlib.patches.Circle(
            xy,
            radius=r,
            facecolor=(0, 0, 0, alpha),
            linewidth=0
        )


def get_hour_ticklabels():
    hours = [12, *range(1, 12)]

    for meridiem in ("am", "pm"):
        for i, hour in enumerate(hours):
            if i % 6 == 0:
                yield "{} {}".format(hour, meridiem)
            else:
                yield None


def plot_punchcard(api, id, fig, ax):
    # Set axes ticks and labels
    ax.set_xticks(range(HOURS_MAX))
    ax.set_yticks(range(DAYS_MAX))
    ax.set_xlim(-0.5, HOURS_MAX - 0.5)
    ax.set_ylim(DAYS_MAX - 0.5, -0.5)
    ax.set_xticklabels(get_hour_ticklabels())
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

    parser = argparse.ArgumentParser()
    parser.add_argument("id", nargs="?",
                        help="ID or screen name of the user")
    parser.add_argument("-o", "--output", required=True,
                        type=argparse.FileType("wb"))
    parser.add_argument("-C", "--cache-dir", default=DEFAULT_CACHE_DIR,
                        help="Path to Tweepy cache directory")
    parser.add_argument("-F", "--font-family",
                        help="Font family for Matplotlib")
    args = parser.parse_args()

    if args.font_family:
        plt.rcParams["font.family"] = args.font_family

    api = get_api_wrapper(args.cache_dir)

    fig, ax = plt.subplots()
    plot_punchcard(api, args.id, fig, ax)

    plt.tight_layout()
    plt.savefig(args.output, bbox_inches="tight", dpi=300)
