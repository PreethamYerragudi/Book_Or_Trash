import openai
import os

from openai import OpenAI

loved = []
hated = []

# openai.api_key = os.environ['InternKey']

client = OpenAI(
    # This is the default and can be omitted
    api_key = "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"
)

def makeSummary(title):
    # Make a request to the ChatGPT API
    return client.chat.completions.create(
        model="gpt-3.5-turbo",  # You can also use "gpt-4" if you have access
        messages=[
            {"role": "user",
             "content": "Generate a summary of the following book that is 100 words or less " + title}
     ],
    
    ).choices[0].message.content


def finalReccomendation(booked, trashed):
    return client.chat.completions.create(
        model="gpt-3.5-turbo",  # You can also use "gpt-4" if you have access
        messages=[
            {"role": "user", "content": "Generate a book recomendation based on this list of liked books: "+"".join(booked)+" and this list of disliked books: "+ "".join(trashed)}
     ],
    
    ).choices[0].message.content


def add_book(title, liked):
    if liked:
        loved.append(title + ", ")
    else:
        hated.append(title + ", ")

loved = ["The Hobbit,", "The Magician's Nephew,", "Peter And Wendy,", "RedWall,", "Eragorn,", "A Game Of Thrones,", "Jade City,", "The StarDust Theif,", "The Buried Giant,", "Howl's Moving Castle,"]
hated = ["The Jungle,","Silent Spring,","Follies,","Hidden Figures,"," Into The Wind,","Black Like Me,","In Cold Blood,","A Walk In The Woods,","In The Time Of Butterflies,","Into Thin Air,"]

