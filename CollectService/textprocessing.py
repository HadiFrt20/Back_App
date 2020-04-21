from textblob import TextBlob
import json


def GetSentiment(tweet_text):
    polarity = 0
    subjectivity = 0
    tweet = TextBlob(tweet_text)
    polarity = tweet.sentiment.polarity
    subjectivity = tweet.sentiment.subjectivity

    return polarity, subjectivity


def MatchKeywords(tweet_text):
    glossary = {}
    matched_keys = []
    text = []
    with open("CollectService/categorised_glossary.json", "r") as json_file:
        glossary = json.load(json_file)
    for value in tweet_text.split(' '):
        if(len(value) > 1):
            text.append(value.lower())
    for word in text:
        for k, values in glossary.items():
            for v in list(values):
                if word == v.lower():
                    matched_keys.append(k)
                    break
    return matched_keys


if __name__ == "__main__":
    txt = []
    txt.append("Chinese-owned Smithfield warehouse Foods shutters two more meat" +
               " processing plants in Missouri and Wisconsin after massive" +
               " coronavirus outbreak closed South Dakota factory," +
               " threatening the American food supply chain 5G")
    print(MatchKeywords(txt[0]))
