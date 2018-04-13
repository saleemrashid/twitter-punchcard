# Twitter Punchcards

Python script to generate Twitter "punchcards" showing at what times in the
week a Twitter account tweets at.

All timestamps are in the time zone of the account the punchcard is about.

![Example output](example.png)

## Installation

Make sure you have [Matplotlib](https://matplotlib.org/) installed.

## Usage

First, create a Twitter application and [generate an access
token](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens).

```bash
# Configure the Twitter OAuth token
export TWITTER_CONSUMER_KEY="XXXXXXXXXXXXXXXXXXXXXXXXX"
export TWITTER_CONSUMER_SECRET="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
export TWITTER_ACCESS_TOKEN="XXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
export TWITTER_ACCESS_TOKEN_SECRET="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# Generate a PNG image for the authenticated user
./main.py -o punchcard.png
# Generate a PNG image for @Twitter
./main.py -o twitter.png Twitter
```
