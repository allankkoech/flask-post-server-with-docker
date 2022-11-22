from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

import platform
import datetime

app = Flask(__name__)

# Confirgurations
if platform.system() == 'Windows':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_db.sqlite3'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////db/flask_db.sqlite3'

app.config['SECRET_KEY'] = 'secret'

import os

print('>> ', os.listdir("/db"))
print('DB: ', app.config['SQLALCHEMY_DATABASE_URI'])


db = SQLAlchemy()
ma = Marshmallow(app)

db.init_app(app=app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    post_info = db.Column(db.String, nullable = False)
    post_date = db.Column(db.DateTime, nullable = False)
    post_likes = db.Column(db.Integer)

    def __init__(self, info, date, likes=0):
        self.post_info = info
        self.post_date = date
        self.post_likes = likes


class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'post_info', 'post_date', 'post_likes')


post_schema = PostSchema()
posts_schema = PostSchema(many=True)

# Endpoints
# / (Root)
@app.route('/')
def root():
    return '<h1>Thank you for visiting our API Homepage</h1>'

@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'GET':
        # Get all posts
        posts = db.session.query(Post).all()
        posts = posts_schema.dump(posts)
        return posts

    else:
        # Add a new post
        body = request.get_json(force=True)
        _info = body['post_info']

        post = Post(_info, datetime.datetime.now(), 0)

        # print(post, post_schema.dump(post))

        db.session.add(post)
        db.session.commit()

        return post_schema.dump(post), 201

@app.route('/post/<id>', methods=['GET', 'PUT', 'DELETE'])
def post_id(id):
    post = db.session.query(Post).filter(Post.id==id).one()

    print(request.method, ' < -- > ', post_schema.dump(post))

    if not post:
        return "No such post id found!", 404

    if request.method == 'GET':
        return post_schema.dump(post)

    elif request.method == 'PUT':
        # Update the post details
        body = request.get_json(force=True)

        post.post_info = body['post_info']
        post.post_likes = body['post_likes']

        db.session.commit()

        return post_schema.dump(post)

    else:
        db.session.delete(post)
        db.session.commit()

        return post_schema.dump(post)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    print('>> ', os.listdir("/db"))
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    print('>> ', os.listdir("/db"))
    