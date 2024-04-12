from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import movie_recommendation

app = FastAPI()


class MovieQuery(BaseModel):
    title: str


@app.post("/recommend")
async def recommend_movie(movie_query: MovieQuery):
    try:
        title = movie_query.title
        recommender = movie_recommendation.MovieRecommender()
        recommendations = recommender.get_recommendations(title)


        if recommendations:
            return recommendations
        else:
            raise HTTPException(
                status_code=404, detail="Sorry, no movie found with the specified title."
            )
    except Exception:
        raise HTTPException(
            status_code=404, detail="Sorry, no movie found with the specified title."
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
