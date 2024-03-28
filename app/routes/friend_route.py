from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.models.models import Friendship, User

router = APIRouter( tags=["friends"])

# Route for making friends
@router.post('/make_friends', status_code=201)
def make_friends(data: dict, db: Session = Depends(get_db)):
    user1_id = data.get('user1_id')
    user2_id = data.get('user2_id')

    # Check if the friendship already exists
    existing_friendship = db.query(Friendship).filter(
        ((Friendship.user1_id == user1_id) & (Friendship.user2_id == user2_id)) |
        ((Friendship.user1_id == user2_id) & (Friendship.user2_id == user1_id))
    ).first()

    if existing_friendship:
        raise HTTPException(status_code=400, detail='Friendship already exists')

    # Create a new friendship
    new_friendship = Friendship(user1_id=user1_id, user2_id=user2_id, status='active')
    db.add(new_friendship)
    db.commit()

    return {'message': 'Friendship created successfully', 'user1_id': user1_id, 'user2_id': user2_id}

# Route for removing friends
@router.post('/remove_friends', status_code=200)
def remove_friends(data: dict, db: Session = Depends(get_db)):
    user1_id = data.get('user1_id')
    user2_id = data.get('user2_id')

    # Check if the friendship exists
    friendship = db.query(Friendship).filter(
        ((Friendship.user1_id == user1_id) & (Friendship.user2_id == user2_id)) |
        ((Friendship.user1_id == user2_id) & (Friendship.user2_id == user1_id))
    ).first()

    if not friendship:
        raise HTTPException(status_code=404, detail='Friendship does not exist')

    # Delete the friendship
    db.delete(friendship)
    db.commit()

    return {'message': 'Friendship removed successfully', 'user1_id': user1_id, 'user2_id': user2_id}

# Route for updating friend's status when they go offline
@router.post('/update_friend_status_offline', status_code=200)
def update_friend_status_offline(data: dict, db: Session = Depends(get_db)):
    user_id = data.get('user_id')

    # Find all friendships where the user is involved
    friendships = db.query(Friendship).filter((Friendship.user1_id == user_id) | (Friendship.user2_id == user_id)).all()

    for friendship in friendships:
        if friendship.status == 'active':
            friendship.status = 'inactive'

    db.commit()

    return {'message': 'Friend status updated to inactive', 'user_id': user_id}

# Route for updating friend's status when they come online
@router.post('/update_friend_status_online', status_code=200)
def update_friend_status_online(data: dict, db: Session = Depends(get_db)):
    user_id = data.get('user_id')

    # Find all friendships where the user is involved
    friendships = db.query(Friendship).filter((Friendship.user1_id == user_id) | (Friendship.user2_id == user_id)).all()

    for friendship in friendships:
        if friendship.status == 'inactive':
            friendship.status = 'active'

    db.commit()

    return {'message': 'Friend status updated to active', 'user_id': user_id}

# Route for viewing friends of a user
@router.get('/view_friends/{user_id}', status_code=200)
def view_friends(user_id: int, db: Session = Depends(get_db)):
    friendships = db.query(Friendship).filter((Friendship.user1_id == user_id) | (Friendship.user2_id == user_id)).all()
    friends = []
    for friendship in friendships:
        friend_id = friendship.user2_id if friendship.user1_id == user_id else friendship.user1_id
        friend = db.query(User).get(friend_id)
        if friend:
            friends.append({'user_id': friend.user_id, 'username': friend.username})
    return {'friends': friends}

# Route for viewing active friends of a user
@router.get('/view_active_friends/{user_id}', status_code=200)
def view_active_friends(user_id: int, db: Session = Depends(get_db)):
    active_friendships = db.query(Friendship).filter(
        ((Friendship.user1_id == user_id) | (Friendship.user2_id == user_id)) &
        (Friendship.status == 'active')
    ).all()
    active_friends_data = []
    for friendship in active_friendships:
        friend_id = friendship.user2_id if friendship.user1_id == user_id else friendship.user1_id
        friend = db.query(User).get(friend_id)
        if friend:
            active_friends_data.append({'user_id': friend.user_id, 'username': friend.username})
    return {'active_friends': active_friends_data}

# Route for recommending friends
@router.get('/recommend_friends/{user_id}', status_code=200)
def recommend_friends(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Find all users who are not already friends with the specified user
    potential_friends = db.query(User).filter(User.user_id != user_id).all()

    # Filter out users who are already friends with the specified user
    existing_friends = [friendship.user2_id for friendship in user.friendships]
    potential_friends = [friend for friend in potential_friends if friend.user_id not in existing_friends]

    # You can add additional logic here to customize the recommendation criteria
    # For example, you can filter potential friends based on common interests, location, etc.

    recommended_friends = [{'user_id': friend.user_id, 'username': friend.username} for friend in potential_friends]

    return {'recommended_friends': recommended_friends}