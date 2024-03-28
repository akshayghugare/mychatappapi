from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from app.models.models import User, Post, Like, Comment, Reply, Save, Share
import os
import shutil
router = APIRouter( tags=["posts"])

UPLOAD_FOLDER = 'uploads'

# Route for creating a new post
@router.post('/create_post')
def create_post(payload: dict, db: Session = Depends(get_db)):
    user_id = payload.get('user_id')
    text_content = payload.get('text_content')
    link_url = payload.get('link_url')
    image_url = payload.get('image_url')  # Assuming this is now just a URL as a string, not a file upload

    # Validate user_id is an integer
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="user_id must be an integer")

    new_post = Post(user_id=user_id, text_content=text_content, image_url=image_url, link_url=link_url)
    db.add(new_post)
    db.commit()

    return {'message': 'Post created successfully', 'text_content': text_content, 'image_url': image_url, 'link_url': link_url}
# Route for viewing a specific post
@router.get('/view_post/{post_id}')
def view_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post:
        return {'post_id': post.post_id, 'text_content': post.text_content, 'image_url': post.image_url, 'link_url': post.link_url}
    else:
        raise HTTPException(status_code=404, detail='Post not found')

# Route for viewing comments of a specific post
@router.get('/view_comments/{post_id}')
def view_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    comments_data = [{'comment_id': comment.comment_id, 'content': comment.content} for comment in comments]
    return {'comments': comments_data}

# Route for getting all posts
@router.get('/get-posts')
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    posts_data = [{'post_id': post.post_id, 'text_content': post.text_content, 'image_url': post.image_url, 'link_url': post.link_url} for post in posts]
    return {'posts': posts_data}

# FastAPI route to view all posts
@router.get('/view_all_posts')
async def view_all_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    all_posts = []
    for post in posts:
        post_data = {
            'post_id': post.post_id,
            'user_id': post.user_id,
            'username': post.user.username,  # Assuming a back-reference from Post to User
            'text_content': post.text_content,
            'image_url': post.image_url,
            'link_url': post.link_url
        }
        all_posts.append(post_data)  # Create PostResponse objects
    return all_posts

# Route for searching posts by keyword
@router.get('/search-posts')
def search_posts(keyword: str, db: Session = Depends(get_db)):
    if not keyword:
        raise HTTPException(status_code=400, detail='Keyword is required')

    posts = db.query(Post).filter(Post.text_content.ilike(f'%{keyword}%')).all()
    posts_data = [{'post_id': post.post_id, 'text_content': post.text_content, 'image_url': post.image_url, 'link_url': post.link_url} for post in posts]
    return {'posts': posts_data}

# Route for creating a new comment
@router.post('/create_comment')
def create_comment(data: dict, db: Session = Depends(get_db)):
    new_comment = Comment(post_id=data['post_id'], user_id=data['user_id'], content=data['content'])
    db.add(new_comment)
    db.commit()

    return {'message': 'Comment created successfully', 'content': data['content'],"post id":data['post_id'],"user id":data['user_id']}

# Route for replying to a comment
@router.post('/reply_to_comment/{comment_id}')
def reply_to_comment(comment_id: int, data: dict, db: Session = Depends(get_db)):
    new_reply = Reply(comment_id=comment_id, user_id=data['user_id'], content=data['content'])
    db.add(new_reply)
    db.commit()

    return {'message': 'Reply posted successfully', 'content': data['content'],"user id":data['user_id'],"comment id":comment_id}

# Route for editing a post
@router.post('/edit_post/{post_id}')
def edit_post(post_id: int, data: dict, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post:
        if 'text_content' in data:
            post.text_content = data['text_content']
        if 'image_url' in data:
            post.image_url = data['image_url']
        if 'link_url' in data:
            post.link_url = data['link_url']

        db.commit()
        return {'message': 'Post updated successfully', 'text_content': data.get('text_content'), 'image_url': data.get('image_url'), 'link_url': data.get('link_url')}
    else:
        raise HTTPException(status_code=404, detail='Post not found')
    
# Route for liking a post
@router.post('/like_post/{post_id}')
def like_post(post_id: int, user_id: int, db: Session = Depends(get_db)):
    print("fffffxxx",post_id,user_id)
    existing_like = db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    if existing_like:
        return {'user_id': user_id, 'message': 'You have already liked this post'}

    new_like = Like(user_id=user_id, post_id=post_id)
    db.add(new_like)
    db.commit()

    return {'user_id': user_id, 'message': 'Post liked successfully'}

# Route for sharing a post
@router.post('/share_post/{post_id}')
def share_post(post_id: int, user_id: int, db: Session = Depends(get_db)):
    new_share = Share(user_id=user_id, post_id=post_id)
    db.add(new_share)
    db.commit()

    return {'user_id': user_id, 'message': 'Post shared successfully'}

# Route for saving a post
@router.post('/save_post/{post_id}')
def save_post(post_id: int, user_id: int, db: Session = Depends(get_db)):
    new_save = Save(user_id=user_id, post_id=post_id)
    db.add(new_save)
    db.commit()

    return {'user_id': user_id, 'message': 'Post saved successfully'}

# Route for viewing likes of a post
@router.get('/view_likes/{post_id}')
def view_likes(post_id: int, db: Session = Depends(get_db)):
    likes = db.query(Like).filter(Like.post_id == post_id).all()
    return likes

# Route for viewing shares of a post
@router.get('/view_shares/{post_id}')
def view_shares(post_id: int, db: Session = Depends(get_db)):
    shares = db.query(Share).filter(Share.post_id == post_id).all()
    return shares

# Route for viewing saves of a post
@router.get('/view_saves/{post_id}')
def view_saves(post_id: int, db: Session = Depends(get_db)):
    saves = db.query(Save).filter(Save.post_id == post_id).all()
    return saves

# FastAPI route to delete a post and its associated comments and likes
@router.post('/delete_post/{post_id}', status_code=200)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    # First, retrieve the post to ensure it exists
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    # Begin a transaction
    try:
        # Delete comments associated with the post
        db.query(Comment).filter(Comment.post_id == post_id).delete(synchronize_session=False)
        # Delete likes associated with the post
        db.query(Like).filter(Like.post_id == post_id).delete(synchronize_session=False)
        # Now, delete the post
        db.delete(post)
        db.commit()
        return {'message': 'Post and its associated comments and likes successfully deleted'}
    except Exception as e:
        db.rollback()  # Rollback the transaction in case of error
        raise HTTPException(status_code=500, detail=f'Error deleting post: {str(e)}')






