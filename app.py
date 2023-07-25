import flask
from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
from requests import post
import tweepy
import matplotlib.pyplot as plt
import os
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

plt.style.use('fivethirtyeight')
nltk.download('vader_lexicon')

# You can generate generate keys at https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api to test the project.
consumer_key=""
consumer_secret=""
access_token=""
access_token_secret=""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth)

analyzeSent = SentimentIntensityAnalyzer()

app = Flask(__name__, template_folder="my-app/build")
CORS(app)
@app.route("/")
@cross_origin()
def serve():
    print(os.getcwd())
    return flask.render_template('index.html')


@app.route('/search', methods=['POST', 'GET'])
@cross_origin()
def search():
    keyword = request.form.get('keyword')

    tweets = []
    likes = []
    time = []
    tweetSentiment = []
    tweetSentimentNum = []
    overallSentiment = ''
    number_of_tweets = 100

    search_term = f"{keyword} OR \"{keyword} \" OR \" {keyword}\""
    overallSentimentNum = 0
    unique_tweets = set()

    for i in tweepy.Cursor(api.search_tweets, q=search_term, lang ='en', since = "2023-01-01", tweet_mode="extended").items(number_of_tweets):
        if i.full_text not in unique_tweets and not i.full_text.startswith('RT @'):
            unique_tweets.add(i.full_text)
            tweets.append(i.full_text)
            likes.append(i.favorite_count)
            time.append(i.created_at)
            tweetSentimentNum.append(analyzeSent.polarity_scores(i.full_text)["compound"])
            if analyzeSent.polarity_scores(i.full_text)["compound"] <= -0.6666:
                tweetSentiment.append("Extremely Negative")
            elif analyzeSent.polarity_scores(i.full_text)["compound"] <= -0.3333:
                tweetSentiment.append("Very Negative")
            elif analyzeSent.polarity_scores(i.full_text)["compound"] < 0:
                tweetSentiment.append("Negative")
            elif analyzeSent.polarity_scores(i.full_text)["compound"] == 0:
                tweetSentiment.append("Neutral")
            elif analyzeSent.polarity_scores(i.full_text)["compound"] <= 0.3333:
                tweetSentiment.append("Positive")
            elif analyzeSent.polarity_scores(i.full_text)["compound"] <= 0.6666:
                tweetSentiment.append("Very Positive")
            else:
                tweetSentiment.append("Extremely Positive")
            overallSentimentNum += analyzeSent.polarity_scores(i.full_text)["compound"]

    total_tweets = len(tweets)
    if total_tweets > 0:
        overallSentimentNum /= total_tweets

    if overallSentimentNum <= (-0.6666 * total_tweets):
        overallSentiment = "Extremely Negative"
    elif overallSentimentNum <= (-0.3333 * total_tweets):
        overallSentiment = "Very Negative"
    elif overallSentimentNum < 0:
        overallSentiment = "Negative"
    elif overallSentimentNum == 0:
        overallSentiment = "Neutral"
    elif overallSentimentNum <= (0.3333 * total_tweets):
        overallSentiment = "Positive"
    elif overallSentimentNum <= (0.6666 * total_tweets):
        overallSentiment = "Very Positive"
    else:
        overallSentiment = "Extremely Positive"

    return render_template('result.html',
                        tweets=tweets,
                        times=time,
                        sentiments=tweetSentiment,
                        scores=tweetSentimentNum,
                        Overall_Sentiment=overallSentiment,
                        Overall_Sentiment_Score=overallSentimentNum)

if __name__ == '__main__':
    CORS(app)
    app.run(debug = True)
