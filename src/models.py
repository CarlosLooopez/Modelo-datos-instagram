

import enum
from sqlalchemy import (
    Column, Integer, String, ForeignKey, Table, Text, DateTime, Boolean, Enum, create_engine
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from eralchemy2 import render_er  # requiere eralchemy2

Base = declarative_base()

# Tabla intermedia para seguidores (N:M)
follower_table = Table(
    "follower",
    Base.metadata,
    Column("user_from_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("user_to_id", Integer, ForeignKey("user.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    firstname = Column(String(80))
    lastname = Column(String(80))
    email = Column(String(120), unique=True, nullable=False)
    bio = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relaciones
    posts = relationship("Post", back_populates="author",
                         cascade="all, delete-orphan")
    comments = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan")

    # seguidores / siguiendo (usando la tabla follower)
    followers = relationship(
        "User",
        secondary=follower_table,
        primaryjoin=id == follower_table.c.user_to_id,
        secondaryjoin=id == follower_table.c.user_from_id,
        backref="following",
        viewonly=True
    )

    def __repr__(self):
        return f"<User(username={self.username})>"


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    caption = Column(Text)
    location = Column(String(120))
    created_at = Column(DateTime, default=datetime.utcnow)

    # relaciones
    author = relationship("User", back_populates="posts")
    media = relationship("Media", back_populates="post",
                         cascade="all, delete-orphan")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id})>"


class MediaType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True)
    type = Column(Enum(MediaType), nullable=False)
    url = Column(String(250), nullable=False)
    post_id = Column(Integer, ForeignKey("post.id"))

    # relación
    post = relationship("Post", back_populates="media")

    def __repr__(self):
        return f"<Media(type={self.type}, url={self.url})>"


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    comment_text = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("user.id"))
    post_id = Column(Integer, ForeignKey("post.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # relaciones
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id})>"


if __name__ == "__main__":
    # 1) Crea la base de datos SQLite local (example.db)
    sqlite_url = "sqlite:///example.db"
    engine = create_engine(sqlite_url)
    Base.metadata.create_all(engine)
    print("✅ SQLite DB creada: example.db (con las tablas declaradas)")

    # 2) Genera el diagrama a partir de la DB creada
    output_file = "diagram.png"
    try:
        render_er(sqlite_url, output_file)
        print(f"✅ Diagrama generado: {output_file}")
    except Exception as e:
        print("❌ Error generando diagrama:", e)
        raise
