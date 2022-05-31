from tornado.web import url
import tornado.web
from tornado import httpclient
from .base import BaseHandler,BaseManage
from .models import User,Category,Course,Order
from .config import site_domain
from utils.alipay import AliPay
from utils.decorators import jwt_async,auth_validated,role_validated
import peewee
import random
import io
import json

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from keras.models import load_model
import nltk
import ssl
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import pickle

intents = {"intents": [
        {"tag": "打招呼",
         "patterns": ["你好", "您好", "请问", "有人吗", "师傅","不好意思","hi"],
         "responses": ["您好", "又是您啊", "你好","您有事吗","您好在的","请问有什么需要帮助的"],
         "context": [""]
        },
        {"tag": "告别",
         "patterns": ["再见", "拜拜", "88", "回见", "回头见"],
         "responses": ["再见", "一路顺风", "下次见", "祝您好运"],
         "context": [""]
        },
   ]
}
words = ['88', 'hi', '不好意思', '你好', '再见', '回头见', '回见', '师傅', '您好', '拜拜', '有人吗', '请问']
['88', 'hi', '不好意思', '你好', '再见', '回头见', '回见', '师傅', '您好', '拜拜', '有人吗', '请问']
classes = ['告别', '打招呼']


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

async def classify_local(sentence,model):
    ERROR_THRESHOLD = 0.25
    
    # generate probabilities from the model
    input_data = pd.DataFrame([bow(sentence, words)], dtype=float, index=['input'])
    results = model.predict([input_data])[0]
    # filter out predictions below a threshold, and provide intent index
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], str(r[1])))
    # return tuple of intent and probability
    
    return return_list

async def get_response(word):

    model = load_model(os.path.join(BASE_DIR,'scripts/chat.h5'))
    wordlist = await classify_local(word,model)
    a = ""
    for intent in intents['intents']:
        if intent['tag'] == wordlist[0][0]:
            a = random.choice(intent['responses'])
    return a


