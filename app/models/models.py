from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    #firstname = Column(String(50), nullable=False)
    #lastname = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(30), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(300), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
    posts = relationship("Post", back_populates="user")
    friendships_initiated = relationship("Friendship", foreign_keys="[Friendship.user1_id]", backref="initiator")
    friendships_received = relationship("Friendship", foreign_keys="[Friendship.user2_id]", backref="friend")
    
    @property
    def friendships(self):
        # Combine friendships_initiated and friendships_received
        return self.friendships_initiated + self.friendships_received


class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    text_content = Column(Text)
    user = relationship("User", back_populates="posts")
    image_url = Column(String(255))
    link_url = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.now)

    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)

    post = relationship("Post", back_populates="comments")
    replies = relationship("Reply", back_populates="comment", cascade="all, delete-orphan")  # Define the back-reference here

class Reply(Base):
    __tablename__ = 'replies'
    reply_id = Column(Integer, primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.comment_id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)

    comment = relationship("Comment", back_populates="replies")  # This line establishes the relationship with Comment

class Like(Base):
    __tablename__ = 'likes'
    like_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.post_id'), nullable=False)

class Share(Base):
    __tablename__ = 'shares'
    share_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.post_id'), nullable=False)

class Save(Base):
    __tablename__ = 'saves'
    save_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.post_id'), nullable=False)
    
class Friendship(Base):
    __tablename__ = 'friendships'
    friendship_id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    status = Column(String(10), nullable=False)  # Status can be "active" or "inactive"

class AIMaster(Base):
    __tablename__ = 'ai_masters'
    ai_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    topic_expertise = Column(Text, nullable=False)

    knowledge_base = relationship("KnowledgeBase", back_populates="ai_master")

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'
    knowledge_id = Column(Integer, primary_key=True)
    ai_id = Column(Integer, ForeignKey('ai_masters.ai_id', ondelete='CASCADE'))
    content = Column(Text, nullable=False)

    ai_master = relationship("AIMaster", back_populates="knowledge_base")

class Tag(Base):
    __tablename__ = 'tags'
    tag_id = Column(Integer, primary_key=True)
    tag_name = Column(String(50), unique=True, nullable=False)

class PostTag(Base):
    __tablename__ = 'post_tags'
    post_id = Column(Integer, ForeignKey('posts.post_id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.tag_id', ondelete='CASCADE'), primary_key=True)

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.tag_id', ondelete='CASCADE'), primary_key=True)

class UserInteraction(Base):
    __tablename__ = 'user_interactions'
    interaction_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    post_id = Column(Integer, ForeignKey('posts.post_id', ondelete='CASCADE'))
    interaction_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)

class Topic(Base):
    __tablename__ = 'topics'
    topic_id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

class Page(Base):
    __tablename__ = 'pages'
    page_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    created_at = Column(TIMESTAMP, default=datetime.now)

class UserInterest(Base):
    __tablename__ = 'user_interests'
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), primary_key=True)

class PageTopic(Base):
    __tablename__ = 'page_topics'
    page_id = Column(Integer, ForeignKey('pages.page_id', ondelete='CASCADE'), primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'), primary_key=True)
