from enum import Enum

class TypeOfTransaction(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Category(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    SHOPPING = "shopping"
    TRAVEL = "travel"
    OTHER = "other"

class Status(str, Enum):
    in_progress =  "In Progress"
    finished = "Finished"
    
