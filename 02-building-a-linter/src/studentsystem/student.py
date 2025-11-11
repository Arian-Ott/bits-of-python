from datetime import date
import random


class Student:
    
    

    def __init__(self, 
                 first_name, 
                 last_name, 
                 date_of_birth):
        
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        
      
        self.subjects = {}

    def add_subject(self, subject):
        if subject in self.subjects:
            raise ValueError(f"Subject '{subject}' is already added to student.")
        
        self.subjects[subject] = []

    def add_grade(self, subject, grade):


        if subject not in self.subjects:
            raise ValueError(f"Subject '{subject}' is not added. Call add_subject() first.")
        
        self.subjects[subject].append(grade)

    def get_grades(self, subject):

        if subject not in self.subjects:
            raise ValueError(f"Subject '{subject}' not found.")
        return self.subjects[subject]

    def get_subjects(self):
        return self.subjects

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth.isoformat(),
            "subjects": self.subjects
        }
        
    @classmethod
    def random_student():
        