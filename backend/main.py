from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from flask_migrate import Migrate
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
CORS(app)

db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db)

class TodoItem(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)

    ##### เพิ่มส่วน relationship  ซึ่งตรงนี้จะไม่กระทบ schema database เลย (เพราะว่าไม่มีการ map ไปยังคอลัมน์ใดๆ)
    comments: Mapped[list["Comment"]] = relationship(back_populates="todo")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "comments": [
                comment.to_dict() for comment in self.comments
            ]
        }

class Comment(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message: Mapped[str] = mapped_column(String(250))
    todo_id: Mapped[int] = mapped_column(ForeignKey('todo_item.id'))

    todo: Mapped["TodoItem"] = relationship(back_populates="comments")

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "todo_id": self.todo_id
        }

# with app.app_context():
#     db.create_all()

INITIAL_TODOS = [
    TodoItem(title='Learn Flask'),
    TodoItem(title='Build a Flask App'),
]

with app.app_context():
    if TodoItem.query.count() == 0:
        for item in INITIAL_TODOS:
            db.session.add(item)
        db.session.commit()

@app.route('/api/todos/', methods=['GET'])
def get_todos():
    todos = TodoItem.query.all()
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/api/todos/', methods=['POST'])
def add_todo():
    data = request.get_json()
    todo = new_todo(data)
    if todo:
        db.session.add(todo)                       # บรรทัดที่ปรับใหม่
        db.session.commit()                        # บรรทัดที่ปรับใหม่ 
        return jsonify(todo.to_dict())             # บรรทัดที่ปรับใหม่
    else:
        # return http response code 400 for bad requests
        return (jsonify({'error': 'Invalid todo data'}), 400)

@app.route('/api/todos/<int:id>/toggle/', methods=['PATCH'])
def toggle_todo(id):
    todo = TodoItem.query.get_or_404(id)
    todo.done = not todo.done
    db.session.commit()
    return jsonify(todo.to_dict())

@app.route('/api/todos/<int:id>/', methods=['DELETE'])
def delete_todo(id):
    todo = TodoItem.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted successfully'})

def new_todo(data):
    return TodoItem(title=data['title'], 
                    done=data.get('done', False))

if __name__ == '__main__':
    app.run(debug=True)