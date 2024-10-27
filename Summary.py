import openai
import PyPDF2
import os


openai.api_key = os.environ['InternKey']


def makeSummary(input):
    # Make a request to the ChatGPT API
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can also use "gpt-4" if you have access
        messages=[
            {"role": "user", "content": "Generate a summary of the following book that is 50 words or less "+ input}
     ]
    
    )

def finalReccomendation(booked, trashed):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can also use "gpt-4" if you have access
        messages=[
            {"role": "user", "content": "Generate a book recomendation based on this list of liked books: "+"".join(booked)+" and this list of disliked books: "+ "".join(trashed)+" make the output just the title of the reccomendation"}
     ]
    
    )

loved = ["The Hobbit,", "The Magician's Nephew,", "Peter And Wendy,", "RedWall,", "Eragorn,", "A Game Of Thrones,", "Jade City,", "The StarDust Theif,", "The Buried Giant,", "Howl's Moving Castle,"]
hated = ["The Jungle,","Silent Spring,","Follies,","Hidden Figures,"," Into The Wind,","Black Like Me,","In Cold Blood,","A Walk In The Woods,","In The Time Of Butterflies,","Into Thin Air,"]
print(finalReccomendation(loved,hated)['choices'][0]['message']['content'])

