import json
import os
from io import BytesIO
import matplotlib.pyplot as plt

import requests
from dagster import asset, AssetExecutionContext, MetadataValue, MaterializeResult

import pandas as pd


@asset
def top_story_ids() -> None:
    newstories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"

    top_new_story_ids = requests.get(newstories_url).json()[:100]

    os.makedirs("data", exist_ok=True)

    with open("data/topstory_ids.json", "w") as f:
        json.dump(top_new_story_ids, f)


@asset(deps=[top_story_ids])
def topstories(context: AssetExecutionContext) -> MaterializeResult:
    with open("data/topstory_ids.json", "r") as f:
        top_new_story_ids = json.load(f)

    top_stories = []
    for story_id in top_new_story_ids:
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = requests.get(story_url).json()
        top_stories.append(story)

        if len(top_stories) % 20 == 0:
            print(f"Downloaded {len(top_stories)} stories")

    df = pd.DataFrame(top_stories)
    df.to_csv("data/topstories.csv", index=False)

    return MaterializeResult(metadata= {
        "num_stories": len(df),
        "preview": MetadataValue.md((df.head().to_markdown())),
    })

@asset(deps=[topstories])
def most_frequent_words() -> None:
    stopwords = ["a", "the", "an", "of", "to", "in", "for", "and", "with", "on", "is"]

    topstories_df = pd.read_csv("data/topstories.csv")

    word_counts = {}

    for title in topstories_df["title"]:
        lower_title = title.lower()
        for word in lower_title.split():
            cleaned_word = word.strip(".,-!?:;()[]'\"-")
            if cleaned_word not in stopwords:
                word_counts[word] = word_counts.get(word, 0) + 1


    top_words = {pair[0]: pair[1] for pair in sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:25]}

    with open("data/topwords.json", "w") as f:
        json.dump(top_words, f)