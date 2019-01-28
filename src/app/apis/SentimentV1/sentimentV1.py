'''
Created on Jan 22, 2019

Web service for Sentiment Analysis

@author: manu
'''
import uuid
import json
import time

# flask
from flask import jsonify
from flask import Blueprint, request

from app import app
from app import db
import logging
# michaniki app
from ...tasks import *

# temp folder save image files downloaded from S3
TEMP_FOLDER = os.path.join('./tmp')

blueprint = Blueprint('sentimentV1', __name__)

@blueprint.route('/predict', methods=['POST'])
def pred_sentiment():
    """
    Run the pre-trained base Sentiment analysis model
    and send sentence to queue

    Listening user submitted sentences and
    stack them in a Redis queue
    """

    logging.info("Inside pred_Sentence")
    data = {"success": False}

    model_name = 'base'

    message = request.form.get('textv')
    print "Received message:{}".format(message)
    #sentence = Sentence(message)

    # create a image id
    this_id = str(uuid.uuid4())

    d = {"id": this_id, "text": message, "model_name": model_name}

    # push to the redis queue
    db.rpush(SENTIMENT_TEXT_QUEUE, json.dumps(d))

    while True:
        # check if the response has been returned
        output = db.get(this_id)
        if output is not None:
            output = output.decode('utf-8')
            data["prediction"] = json.loads(output)

            db.delete(this_id)
            break
        else:
            #print "* Waiting for the Sentiment Inference Server..."
            time.sleep(CLIENT_SLEEP)

        data['success'] = True
    return jsonify({
        "data": data
        }), 200
