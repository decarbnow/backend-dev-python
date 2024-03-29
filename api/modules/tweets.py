from datetime import datetime
import logging

from flask import Blueprint, jsonify, Response, render_template, abort
from flask_cors import cross_origin
from .auth import login_exempt

from lib.tweets_base import readTweetsApiJson
from lib.Tweet import Tweet
from lib.TweetForest import TweetForest

bp = Blueprint('tweets', __name__, url_prefix='/tweets')

@bp.route('/')
@cross_origin()
@login_exempt
def root():
    return jsonify({
        'date': int(datetime.timestamp(datetime.now())),
        'tweets': readTweetsApiJson()
    })


@bp.route('/<int:id>')
def tweet(id):
    tweet = Tweet.loadFromFile(id)
    return jsonify(tweet.data)

@bp.route('/forest')
def forest_show():
    return render_template('forest.html.j2', forest = TweetForest.fromFolder())
    #return Response(str(forest), mimetype='text/plain')

@bp.route('/forest/renew')
def forest_create():
    logging.warning('Manual invocation of creating forest!')
    # renew forest
    forest = TweetForest.fromFolder()
    forest.saveApiJson()
    return jsonify(readTweetsApiJson())

@bp.route('/add/<int:id>')
def add(id):
    logging.warning('Manual invocation of adding tweet (id: {})!'.format(id))
    tweet = Tweet.loadFromTwitter(id)
    tweet.save()
    # renew forest
    forest = TweetForest.fromFolder()
    forest.saveApiJson()
    return jsonify({
        'message': 'added',
        'tweet': {
            'id': id,
            'data': tweet.data
        }
    })

@bp.route('/delete/<int:id>')
def delete(id):
    logging.warning('Manual invocation of deleting tweet (id: {})!'.format(id))
    tweet = Tweet.loadFromFile(id)
    tweet.delete()
    # renew forest
    forest = TweetForest.fromFolder()
    forest.saveApiJson()
    return jsonify({
        'message': 'deleted',
        'tweet': {
            'id': id,
            'data': tweet.data
        }
    })

@bp.route('/all')
def all():
    tweets = Tweet.loadFromFolder()
    tweets.sort(key = lambda x: x.getDateTime(), reverse = True)
    # [Tweet(i) for i in tweets]
    return render_template('all.html.j2', tweets = tweets)

@bp.route('/stories')
def info():
    tweets = readTweetsApiJson()
    stories = {};
    for id, info in tweets.items():
        if 'story' in info:
            storyId = info['story']
            if storyId not in stories:
                stories[storyId] = []
            stories[storyId].append(Tweet.loadFromFile(id))
    return render_template('stories.html.j2', stories = stories)
