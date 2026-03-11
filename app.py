from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
 return "TI OK MAN!"
@app.route('/student')
def get_student():
 return jsonify({
 "name": "Arnolfo Reyes Asidoy Jr.",
 "grade": 101,
 "section": "ANDROID"

 })
