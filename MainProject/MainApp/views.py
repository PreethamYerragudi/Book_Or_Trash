from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
import random
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os

from openai import OpenAI

# Load the data
books = pd.read_csv('books.csv')
ratings = pd.read_csv('ratings.csv')
ratings_dict = []
userBookRatingsDF = ratings.pivot_table(index='user_id', columns='book_id', values='rating')
pd.options.display.max_colwidth = None
count = 0


loved = []
hated = []

# openai.api_key = os.environ['InternKey']

client = OpenAI(
    # This is the default and can be omitted
    api_key = "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"
)

def makeSummary(title):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # You can also use "gpt-4" if you have access
            messages=[
                {"role": "user",
                 "content": "Generate a summary of the following book that is 100 words or less: " + title}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None


def finalReccomendation(booked, trashed):
    return client.chat.completions.create(
        model="gpt-3.5-turbo",  # You can also use "gpt-4" if you have access
        messages=[
            {"role": "user", "content": "Generate a book recomendation based on this list of liked books: "+str(booked)+" and this list of disliked books: "+str(trashed)}
     ],
    
    ).choices[0].message.content


def add_book(title, liked):
    if liked:
        loved.append(title + ", ")
    else:
        hated.append(title + ", ")



def get_title_author(id_num):
    return {
        "title": books[books['book_id'] == id_num]['title'].to_string(index=False),
        "authors": books[books['book_id'] == id_num]['authors'].to_string(index=False),
    }

def get_random_book():
    recommended_book_id = random.randint(1,10000)
    return {"book_id": recommended_book_id,
            "title": books[books['book_id'] == recommended_book_id]['title'].to_string(index=False),
            "authors": books[books['book_id'] == recommended_book_id]['authors'].to_string(index=False),
            "original_publication_year": books[books['book_id'] == recommended_book_id]['original_publication_year'].to_string(index=False),
            "image_url": books[books['book_id'] == recommended_book_id]['image_url'].to_string(index=False)}

def get_next_book():
    print("During Method Call")
    ratings_series = pd.Series(ratings_dict, name='user_ratings')
    ratings_aligned = ratings_series.reindex(userBookRatingsDF.columns)

    similarities = []
    for _, row in userBookRatingsDF.iterrows():
        # Combine the user ratings and the current row to find non-NaN columns
        combined = pd.concat([ratings_aligned, row], axis=1, keys=['user', 'other_user'])
        combined_non_nan = combined.dropna()  # Remove columns with NaN in either user ratings or other user

        # If there are no columns left after dropping NaNs, similarity is undefined; set to 0
        if combined_non_nan.empty:
            similarities.append(0)
        else:
            # Calculate cosine similarity for non-NaN columns
            sim = cosine_similarity([combined_non_nan['user']], [combined_non_nan['other_user']])[0, 0]
            similarities.append(sim)

    cosine_sim_df = pd.DataFrame(similarities, index=userBookRatingsDF.index, columns=['similarity_with_user'])

    unrated_books = userBookRatingsDF.columns.difference(ratings_series.dropna().index)
    weighted_scores = {}

    for book in unrated_books:
        # Get ratings for this book from other users and corresponding similarity scores
        book_ratings = userBookRatingsDF[book]
        mask = ~book_ratings.isna()  # Only include users who have rated this book
        relevant_similarities = cosine_sim_df.loc[mask, 'similarity_with_user']

        if relevant_similarities.sum() == 0:
            weighted_scores[book] = 0  # Avoid division by zero if no similarities
        else:
            # Compute the weighted average rating for the book
            weighted_scores[book] = (book_ratings[mask] * relevant_similarities).sum() / relevant_similarities.sum()

    # Find the book with the highest weighted score
    recommended_book_id = max(weighted_scores, key=weighted_scores.get)
    return {"book_id": recommended_book_id,
            "title": books[books['book_id'] == recommended_book_id]['title'].to_string(index=False),
            "authors": books[books['book_id'] == recommended_book_id]['authors'].to_string(index=False),
            "original_publication_year": books[books['book_id'] == recommended_book_id]['original_publication_year'].to_string(index=False),
            "image_url": books[books['book_id'] == recommended_book_id]['image_url'].to_string(index=False)}

global book_info
book_info = get_random_book()
global summary
summary = makeSummary(book_info["title"])
global counter
counter = 0
# Create your views here.
def mainPage(request):
    global counter
    counter = 0
    content = {
        "image":book_info["image_url"],
        "title":book_info["title"],
        "author":book_info["authors"],
        "id":book_info['book_id'],
        "summary": summary
    }
    return render(request, 'book.html',content)


def update_counter(request):
    global counter
    global is_left_side, received_id
    global summary
    if request.method == 'POST':
        # Extracting the `isLeftSide` and `id` from POST data
        is_left_side = request.POST.get('isLeftSide') == 'true'
        received_title = request.POST.get('title')  # Get the id as a string
        if is_left_side:
            loved.append(received_title)
        else:
            hated.append(received_title)

        global book_info
        book_info = get_random_book()

        
        summary = "Summary not available."  # Provide a default message

        return JsonResponse({'status': 'success', 'message': 'Book updated successfully.'})
    else:
        # If not a POST request, return an error response
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

def final_book(request):
    recco = finalReccomendation(loved, hated)
    return render(request, 'final-book.html', {"rec":recco})



 
# joblib.dump(userBookRatingsDF, "user_book_ratings.pkl")

# userBookRatingsDF = joblib.load("user_book_ratings.pkl")


def update_ratings_dict(book_id, rating):
    ratings_dict[book_id] = rating


def get_book_info(request):
    return render(request, "book.html", get_next_book())
