from fastapi import APIRouter, Depends, HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from database import get_db
from app.models.models import User, UserInterest, Topic
from emailverify import send_verification_email
import random

router = APIRouter( tags=["users"])

verification_store = {}
    
@router.post('/users/sign-in', status_code=200)
async def sign_in(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.get('email')).first()
    if user and check_password_hash(user.password_hash, data['password']):
        return {'message': 'Login successful', 'user_id':user.user_id,'username': user.username, 'email': user.email}
    else:
        raise HTTPException(status_code=401, detail='Invalid username or password')

@router.post('/users/reset-password', status_code=200)
async def reset_password(data: dict, db: Session = Depends(get_db)):
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not all([username, old_password, new_password]):
        raise HTTPException(status_code=400, detail='Username, old password, and new password are required')

    # Check if user exists
    user = db.query(User).filter_by(username=username).first()
    if user is None:
        raise HTTPException(status_code=404,
         detail='User not found')

    # Verify the old password
    if not check_password_hash(user.password_hash, old_password):
        raise HTTPException(status_code=401, detail='Invalid old password')

    # Update the password
    user.password = new_password
    user.password_hash = generate_password_hash(new_password)
    db.commit()

    return {'message': 'Password changed successfully'}

@router.post('/users/forgot-password', status_code=201)
async def forgot_password(data: dict, db: Session = Depends(get_db)):
    email = data.get('email')
    user = db.query(User).filter_by(email=email).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')

    # Generate verification token
    verification_token = str(random.randint(1000, 9999))
    print("Token at change password: ", verification_token)

    # Send verification email
    #with app.app_context():
    send_verification_email(data.get('email'), verification_token)

    store_verification_code(data.get('email'), verification_token, data)

    return {'message': 'Verification token sent, please check your email'}

@router.post('/users/set-password', status_code=200)
async def set_password(data: dict, db: Session = Depends(get_db)):
    email = data.get('email')
    new_password = data.get('new_password')
    input_verification_code = data.get('verification_code')

    if not all([new_password, email, input_verification_code]):
        raise HTTPException(status_code=400, detail='Email, new password, and verification code are required')

    # Retrieve stored data based on the email
    stored_data = retrieve_verification_data(email)
    if not stored_data or stored_data['verification_code'] != input_verification_code:
        raise HTTPException(status_code=400, detail='Invalid or expired verification code')

    # Update password
    user = db.query(User).filter_by(email=email).first()
    user.password = new_password
    user.password_hash = generate_password_hash(new_password)
    db.commit()

    # Clear the temporary storage for this email
    clear_verification_code(email)

    return {'message': 'Password changed successfully'}

@router.post('/users/sign-up', status_code=201)
async def sign_up(data: dict, db: Session = Depends(get_db)):
    # Check for existing user
    if db.query(User).filter_by(username=data.get('username')).first() is not None:
        raise HTTPException(status_code=400, detail='Username already exists')

    # Generate verification token
    verification_token = str(random.randint(1000, 9999))
    print("Token at Signup: ", verification_token)

    # Send verification email
    #with app.app_context():
    send_verification_email(data.get('email'), verification_token)
    print("ddd",data)
    store_verification_code(data.get('email'), verification_token, data)

    return {'message': 'Verification token sent, please check your email'}

def store_verification_code(email, verification_code, user_data):
    verification_store[email] = {
        'verification_code': verification_code,
        'user_data': user_data
    }

def retrieve_verification_data(email):
    return verification_store.get(email)

def clear_verification_code(email):
    if email in verification_store:
        del verification_store[email]

@router.post('/users/verify-email', status_code=201)
async def verify_email(data: dict, db: Session = Depends(get_db)):
    user = data.get('user')
    email = user.get('email')
    input_verification_code = data.get('token')
    stored_data = retrieve_verification_data(email)
    if not stored_data or stored_data['verification_code'] != input_verification_code:
        raise HTTPException(status_code=400, detail='Invalid or expired verification code')
    # Now that the email is verified, create the user account
    user_data = stored_data['user_data']
    hashed_password = generate_password_hash(user_data['password'])
    new_user = User(
    #    firstname=user_data['first_name'],
    #    lastname=user_data['last_name'],
        username=user_data['username'],
        password=user_data['password'],
        email=email,
        password_hash=hashed_password,
        email_verified=True
    )
    db.add(new_user)
    db.commit()
    clear_verification_code(email)
    return {'message': 'User created successfully', 'username': user_data['username'], 'email': email}

@router.post('/users/{user_id}/update-interests', status_code=200)
async def update_user_interests(user_id: int, data: dict, db: Session = Depends(get_db)):
    topic_names = data.get('topic_names', [])

    # Check if the user exists
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Validate the existence of each topic by name and get their IDs
    existing_topics = db.query(Topic).filter(Topic.name.in_(topic_names)).all()
    existing_topic_ids = {topic.topic_id for topic in existing_topics}

    if len(existing_topic_ids) != len(topic_names):
        raise HTTPException(status_code=404, detail='One or more topics not found')

    # Remove current interests
    db.query(UserInterest).filter_by(user_id=user_id).delete()

    # Add new interests, ensuring not to exceed the limit of 5 interests
    for topic_id in list(existing_topic_ids)[:5]:
        new_interest = UserInterest(user_id=user_id, topic_id=topic_id)
        db.add(new_interest)

    db.commit()

    return {'message': 'User interests updated successfully', 'changes': data}
