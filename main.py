from fastapi import FastAPI, Depends
from app.routes import user_routes, post_routes, page_routes, friend_route
from database import engine, get_db, SessionLocal
from sqlalchemy.orm import Session
import uvicorn
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware

app = FastAPI()

# Dependency to get the database session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add CORSMiddleware to the application
# This is a list of origins that are allowed to communicate with the API
# You can adjust the list according to your needs or use "*" to allow all origins
origins = [
    "http://localhost:3000",  # Assuming your front-end runs on this origin
    "https://example.com",
    # Add more origins as needed
]

# Configure CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routes here
app.include_router(user_routes.router)
app.include_router(post_routes.router)
app.include_router(page_routes.router)
app.include_router(friend_route.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
