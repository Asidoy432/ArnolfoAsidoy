-- Student Grade Evaluation System
CREATE TABLE IF NOT EXISTS students (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL,
    grade   INTEGER NOT NULL CHECK (grade >= 0 AND grade <= 100),
    section TEXT    NOT NULL
);

INSERT INTO students (name, grade, section) VALUES ('Juan',  85, 'Stallman');
INSERT INTO students (name, grade, section) VALUES ('Maria', 90, 'Stallman');
INSERT INTO students (name, grade, section) VALUES ('Pedro', 70, 'Zechariah');
