import json
import os
import sys
import random

ANALYTICS_FILE = 'analytics.json'

def load_analytics():
    if not os.path.exists(ANALYTICS_FILE):
        return {"total_attempted": 0, "total_correct": 0, "streak": 0}
    
    try:
        with open(ANALYTICS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Corrupt analytics file '{ANALYTICS_FILE}'. resetting stats.")
        return {"total_attempted": 0, "total_correct": 0, "streak": 0}

def save_analytics(stats):
    try:
        with open(ANALYTICS_FILE, 'w+') as f:
            json.dump(stats, f, indent=4)
    except IOError as e:
        print(f"Error saving analytics: {e}")

def load_questions(filename='questions.json'):
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        return []
    
    try:
        with open(filename, 'r') as f:
            questions = json.load(f)
            return questions
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{filename}'.")
        return []

def filter_questions(questions):
    while True:
        choice = input("Do you want to practice AWS, Cloud, or All? ").strip().lower()
        if choice in ['aws', 'cloud', 'all']:
            if choice == 'all':
                return questions
            
            filtered = [q for q in questions if q.get('category', '').lower() == choice]
            if not filtered:
                print(f"No questions found for category: {choice}")
                # Optional: ask again or return empty
                continue
            return filtered
        else:
            print("Invalid choice. Please enter 'AWS', 'Cloud', or 'All'.")

def get_user_answer():
    while True:
        answer = input("Your answer (A, B, C, or D): ").strip().upper()
        if answer in ['A', 'B', 'C', 'D']:
            return answer
        print("Invalid input. Please enter A, B, C, or D.")

def play_game():
    stats = load_analytics()
    
    # Calculate lifetime accuracy
    total = stats["total_attempted"]
    correct = stats["total_correct"]
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print(f"\nWelcome back! Lifetime Accuracy: {accuracy:.1f}% | Current Streak: {stats['streak']}")
    
    questions = load_questions()
    if not questions:
        return

    questions_to_play = filter_questions(questions)
    
    # Shuffle questions for randomness
    random.shuffle(questions_to_play)
    
    score = 0
    total_session = len(questions_to_play)
    
    print(f"\nStarting quiz with {total_session} questions...\n")
    
    for i, q in enumerate(questions_to_play, 1):
        print(f"Question {i}/{total_session}: {q['question']}")
        for option in q['options']:
            print(option)
            
        user_answer = get_user_answer()
        stats["total_attempted"] += 1
        
        if user_answer == q['correct_answer']:
            print("Correct!")
            score += 1
            stats["total_correct"] += 1
            stats["streak"] += 1
        else:
            print(f"Wrong! The answer was {q['correct_answer']}")
            stats["streak"] = 0
        print("-" * 30)
        
    print(f"\nGame Over! Your final score is {score}/{total_session}")
    save_analytics(stats)

if __name__ == "__main__":
    play_game()
