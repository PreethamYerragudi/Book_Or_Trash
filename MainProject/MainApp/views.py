from django.shortcuts import render
import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Create your views here.
def mainPage(request):
    return render(request, 'index.html')


# Load the data
books = pd.read_csv('books.csv')
ratings = pd.read_csv('ratings.csv')
ratings_dict = {}

# userBookRatingsDF = ratings.pivot_table(index='user_id', columns='book_id', values='rating')
# joblib.dump(userBookRatingsDF, "user_book_ratings.pkl")

userBookRatingsDF = joblib.load("user_book_ratings.pkl")

def get_next_book():
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


def update_ratings_dict(book_id, rating):
    ratings_dict[book_id] = rating


def get_book_info(request):
    return render(request, "book.html", get_next_book())