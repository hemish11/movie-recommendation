import ast
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from ast import literal_eval


class Movie(BaseModel):
    id: int
    overview: str
    title: str
    genre: List[str]
    cast: List[str]


class MovieRecommender:
    def __init__(
        self,
        credits_file="assets/tmdb_5000_credits.csv",
        movies_file="assets/tmdb_5000_movies.csv",
    ):
        self.df1 = pd.read_csv(credits_file)
        self.df2 = pd.read_csv(movies_file)
        self.C = None
        self.m = None
        self.correlation = None
        self.indices = None
        self._process_data()

    def _process_data(self):
        self.df1.columns = ["id", "title", "cast", "crew"]
        self.df2 = self.df2.merge(self.df1, on="id")
        self.C = self.df2["vote_average"].mean()
        self.m = self.df2["vote_count"].quantile(0.9)
        self.q_movies = self.df2.loc[self.df2["vote_count"] >= self.m].copy()
        self.q_movies["score"] = self.q_movies.apply(
            self.weighted_rating, axis=1)

        self.tfidf = TfidfVectorizer(stop_words="english")
        self.df2["overview"] = self.df2["overview"].fillna("")
        self.tfidf_matrix = self.tfidf.fit_transform(self.df2["overview"])
        self.correlation = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)
        self.indices = pd.Series(
            self.df2.index, index=self.df2["title_x"]
        ).drop_duplicates()

    def weighted_rating(self, x):
        v = x["vote_count"]
        R = x["vote_average"]
        return (v / (v + self.m) * R) + (self.m / (self.m + v) * self.C)

    def get_recommendations(self, title_x, correlation=None) -> List[Movie]:
        if correlation is None:
            correlation = self.correlation
        idx = self.indices[title_x]
        correlation_scores = list(enumerate(correlation[idx]))
        correlation_scores = sorted(
            correlation_scores, key=lambda x: x[1], reverse=True
        )
        correlation_scores = correlation_scores[1:11]
        movies_indices = [i[0] for i in correlation_scores]
        result = self.df2.loc[
            movies_indices, ["id", "overview", "title_x", "genres", "cast"]
        ]

        recommendations = []
        for _, row in result.iterrows():
            genres_list = ast.literal_eval(row["genres"])
            cast_list = ast.literal_eval(row["cast"])

            recommendation_genres = [obj["name"] for obj in genres_list]
            recommendation_cast = [obj["name"] for obj in cast_list]

            recommendations.append(
                Movie(
                    id=row["id"],
                    overview=row["overview"],
                    title=row["title_x"],
                    genre=recommendation_genres,
                    cast=recommendation_cast,
                )
            )

        return recommendations
