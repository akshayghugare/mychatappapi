from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.models.models import User, Topic, Page, PageTopic, UserInterest

router = APIRouter(tags=["pages"])

# Route for creating a page
@router.post('/users/{user_id}/pages')
def create_page(user_id: int, title: str, content: str, topic_names: list[str] = [], db: Session = Depends(get_db)):
    if not all([title, content]):
        raise HTTPException(status_code=400, detail='Title and content are required')

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    existing_topics = db.query(Topic).filter(Topic.name.in_(topic_names)).all()
    if len(existing_topics) != len(topic_names):
        raise HTTPException(status_code=404, detail='One or more topics not found')

    new_page = Page(title=title, content=content, user_id=user.user_id)
    db.add(new_page)
    db.commit()

    for topic in existing_topics[:5]:
        new_page_topic = PageTopic(page_id=new_page.page_id, topic_id=topic.topic_id)
        db.add(new_page_topic)

    db.commit()

    return {'message': 'Page created successfully', 'page_id': new_page.page_id, 'title': title, 'content': content}, 201

# Route for getting page recommendations for a user
@router.get('/users/{user_id}/recommendations')
def get_page_recommendations(user_id: int, db: Session = Depends(get_db)):
    user_interests = db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
    
    if not user_interests:
        recommended_pages = db.query(Page)\
            .filter(Page.user_id != user_id)\
            .order_by(Page.created_at.asc())\
            .limit(5)\
            .all()
    
    else:
        interest_ids = [interest.topic_id for interest in user_interests]

        recommended_pages = db.query(Page)\
            .join(PageTopic)\
            .filter(PageTopic.topic_id.in_(interest_ids), Page.user_id != user_id)\
            .distinct(Page.page_id)\
            .all()

    recommendations = [{
        'page_id': page.page_id,
        'title': page.title,
        'content': page.content,
        'created_at': page.created_at.isoformat()
    } for page in recommended_pages]

    return recommendations
