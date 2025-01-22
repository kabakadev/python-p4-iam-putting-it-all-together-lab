from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import ForeignKey
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    # Define columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False, default="default-hash")  # Default value
    image_url = db.Column(db.String(200), default="")
    bio = db.Column(db.String(500), default="")

    # One-to-Many relationship with back_populates
    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan', lazy=True)

    # Hybrid property to get/set password (hashed)
    @hybrid_property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def set_password(self, password):
        self.password = password  # Shortcut for clarity

    # Method to verify password
    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    # Validation for username (unique and non-null)
    @validates('username')
    def validate_username(self, key, value):
        if not value:
            raise ValueError("Username cannot be empty.")
        return value


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    # Define columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.String(500), nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    # Foreign Key for User
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)

    # Relationship with User using back_populates
    user = db.relationship('User', back_populates='recipes', lazy=True)

    # Validations
    @validates('title')
    def validate_title(self, key, value):
        if not value:
            raise ValueError("Title cannot be empty.")
        return value

    @validates('instructions')
    def validate_instructions(self, key, value):
        if len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value
