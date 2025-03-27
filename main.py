from flask import Flask, request, jsonify, render_template
from models import db, Task
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/cognitive_load_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Home Route (renders HTML)
@app.route('/')
def dashboard():
    return render_template('index.html')

# API to fetch tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.filter_by(status='active').all()
    return jsonify([task.to_dict() for task in tasks])

# API to add a task
@app.route('/api/tasks', methods=['POST'])

#@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    print("Received Data:", data)  # Debugging line
    return jsonify({'message': 'Received', 'data': data}) # Expecting JSON input
    new_task = Task(
        title=data.get('title'),
        description=data.get('description'),
        complexity=data.get('complexity', 1),
        start_time=datetime.utcnow(),
        status='active'
    )
    db.session.add(new_task)  # Add to session
    #db.session.commit()  # Commit to database
    try:
        db.session.commit()
        return jsonify({'message': 'Task added successfully!', 'task': new_task.to_dict()})


    except Exception as e:
        db.session.rollback()  # Rollback changes on error
        return jsonify({'error': str(e)})



# API to complete a task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.status = 'completed'
        task.end_time = datetime.utcnow()
        task.duration = (task.end_time - task.start_time).seconds // 60  # Calculate duration in minutes
        db.session.commit()
        return jsonify(task.to_dict())
    return jsonify({"error": "Task not found"}), 404

# API to get complexity insights
@app.route('/api/tasks/complexity-insights', methods=['GET'])
def get_complexity_insights():
    total_tasks = Task.query.count()
    active_tasks = Task.query.filter_by(status='active').all()
    avg_complexity = sum(task.complexity for task in active_tasks) / len(active_tasks) if active_tasks else 0
    total_time_spent = sum(task.duration for task in Task.query.filter(Task.duration.isnot(None)).all())

    return jsonify({
        "total_tasks": total_tasks,
        "avg_complexity": round(avg_complexity, 2),
        "total_time_spent": total_time_spent
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures database tables are created
    app.run(port=3000, debug=True)
