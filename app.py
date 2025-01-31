from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timesheet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    hours_worked = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __init__(self, date, start_time, end_time, description):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.hours_worked = self.calculate_hours(start_time, end_time)
        self.description = description

    def calculate_hours(self, start, end):
        fmt = "%H:%M"
        start_dt = datetime.strptime(start, fmt)
        end_dt = datetime.strptime(end, fmt)
        delta = end_dt - start_dt
        return f"{delta.seconds // 3600}h {delta.seconds % 3600 // 60} min"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        date = request.form["date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        description = request.form["description"]

        new_entry = Timesheet(date, start_time, end_time, description)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for("index"))

    entries = Timesheet.query.all()
    return render_template("index.html", entries=entries)

@app.route("/delete/<int:id>")
def delete(id):
    entry = Timesheet.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures the database is created inside an application context
    app.run(debug=True)
