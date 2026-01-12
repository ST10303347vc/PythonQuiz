import random
import sys
from typing import List, Dict, Optional, Any
from data_manager import DataManager

# Constants
QUESTIONS_FILE = 'questions.json'
ANALYTICS_FILE = 'analytics.json'
DEFAULT_STATS = {"total_attempted": 0, "total_correct": 0, "streak": 0}

class QuizManager:
    """
    Manages the core logic of the Flashcard Quiz application.
    """

    def __init__(self) -> None:
        """
        Initializes the QuizManager by loading questions and analytics data.
        """
        self.questions: List[Dict[str, Any]] = DataManager.load_json(QUESTIONS_FILE, default=[]) or []
        self.stats: Dict[str, Any] = DataManager.load_analytics(ANALYTICS_FILE)

    def display_welcome_message(self) -> None:
        """
        Calculates and displays the welcome message with user statistics.
        """
        streak = self.stats.get("streak", 0)
        
        # Calculate totals from new schema
        total_attempted = 0
        total_correct = 0
        performance = self.stats.get("performance", {})
        
        for cat_data in performance.values():
            total_attempted += cat_data.get("total", 0)
            total_correct += cat_data.get("correct", 0)
        
        accuracy = (total_correct / total_attempted * 100) if total_attempted > 0 else 0.0
        print(f"\nWelcome back! Lifetime Accuracy: {accuracy:.1f}% | Current Streak: {streak}")

    def filter_questions(self) -> List[Dict[str, Any]]:
        """
        Asks the user to select a category and filters the questions.

        Returns:
            List[Dict[str, Any]]: A list of filtered questions.
        """
        if not self.questions:
            print("No questions data available.")
            return []

        while True:
            choice = input("Do you want to practice AWS, Cloud, or All? ").strip().lower()
            if choice == 'all':
                return self.questions
            
            if choice in ['aws', 'cloud']:
                filtered = [q for q in self.questions if q.get('category', '').lower() == choice]
                if not filtered:
                    print(f"No questions found for category: {choice}")
                    continue
                return filtered
            
            print("Invalid choice. Please enter 'AWS', 'Cloud', or 'All'.")

    def get_user_answer(self) -> str:
        """
        Prompts the user for an answer and validates the input.

        Returns:
            str: The user's validated answer (A, B, C, or D).
        """
        while True:
            answer = input("Your answer (A, B, C, or D): ").strip().upper()
            if answer in ['A', 'B', 'C', 'D']:
                return answer
            print("Invalid input. Please enter A, B, C, or D.")

    def run(self) -> None:
        """
        Runs the main game loop.
        """
        if not self.questions:
            print("Exiting due to lack of questions.")
            return

        self.display_welcome_message()
        
        questions_to_play = self.filter_questions()
        if not questions_to_play:
            return

        random.shuffle(questions_to_play)
        
        score = 0
        total_session = len(questions_to_play)
        
        print(f"\nStarting quiz with {total_session} questions...\n")
        
        for i, q in enumerate(questions_to_play, 1):
            print(f"Question {i}/{total_session}: {q['question']}")
            for option in q['options']:
                print(option)
                
            user_answer = self.get_user_answer()
            
            # Update data structure
            category = q.get('category', 'General')
            if "performance" not in self.stats:
                self.stats["performance"] = {}
            if category not in self.stats["performance"]:
                self.stats["performance"][category] = {"correct": 0, "total": 0}
            
            self.stats["performance"][category]["total"] += 1
            
            if user_answer == q['correct_answer']:
                print("Correct!")
                score += 1
                self.stats["performance"][category]["correct"] += 1
                self.stats["streak"] = self.stats.get("streak", 0) + 1
            else:
                print(f"Wrong! The answer was {q['correct_answer']}")
                self.stats["streak"] = 0
            print("-" * 30)
            
        print(f"\nGame Over! Your final score is {score}/{total_session}")
        DataManager.save_json(ANALYTICS_FILE, self.stats)

if __name__ == "__main__":
    app = QuizManager()
    app.run()
