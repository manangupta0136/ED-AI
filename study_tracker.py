from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

MAX_HOURS_PER_DAY = 10

tasks = []
schedule = defaultdict(list)

class Task:
    def __init__(self, subject, topic, deadline, priority):
        self.subject = subject
        self.topic = topic
        self.deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
        self.priority = priority
        self.remaining_hours = None  # To be assigned by the agent

@app.route('/')
def home():
    return "🧠 Task Scheduler Agent Backend is Running!"

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    subject = data['subject']
    topic = data['topic']
    deadline = data['deadline']
    priority = int(data['priority'])

    task = Task(subject, topic, deadline, priority)
    tasks.append(task)
    return jsonify({"message": "Task added successfully!"})

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    global schedule
    schedule = defaultdict(list)

    # Sort tasks by deadline first, then priority descending
    sorted_tasks = sorted(tasks, key=lambda x: (x.deadline, -x.priority))

    today = datetime.today().date()
    total_priority = sum(task.priority for task in sorted_tasks)

    for task in sorted_tasks:
        # Calculate proportion of time this task gets
        priority_ratio = task.priority / total_priority
        total_days = (task.deadline - today).days + 1

        if total_days <= 0:
            continue  # skip past deadlines

        total_hours = int(priority_ratio * MAX_HOURS_PER_DAY * total_days)
        task.remaining_hours = total_hours

        for i in range(total_days):
            current_day = today + timedelta(days=i)
            hours_today = min(task.remaining_hours, round(total_hours / total_days))

            # Ensure we don’t exceed max hours per day
            used_hours = sum([entry['hours'] for entry in schedule[current_day]])
            if used_hours + hours_today > MAX_HOURS_PER_DAY:
                hours_today = MAX_HOURS_PER_DAY - used_hours
            if hours_today <= 0:
                continue

            schedule[current_day].append({
                "subject": task.subject,
                "topic": task.topic,
                "hours": round(hours_today)
            })
            task.remaining_hours -= hours_today
            if task.remaining_hours <= 0:
                break

    # Format date keys as strings for JSON
    schedule_json = {str(k): v for k, v in schedule.items()}
    return jsonify(schedule_json)

@app.route('/view_schedule', methods=['GET'])
def view_schedule():
    return jsonify({str(k): v for k, v in schedule.items()})

@app.route('/clear_all', methods=['POST'])
def clear_all():
    global tasks, schedule
    tasks = []
    schedule = defaultdict(list)
    return jsonify({"message": "All tasks and schedules cleared!"})

if __name__ == '__main__':
    app.run(debug=True)
