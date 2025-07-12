import json
import time
import random
import os
from datetime import datetime

def load_flashcards(filename="flashcards.json"):
    """
    Load flashcards from JSON file
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            flashcards = json.load(f)
        print(f"Loaded {len(flashcards)} flashcards from {filename}")
        return flashcards
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error loading flashcards: {e}")
        return None

def display_flashcard(flashcard, card_number, total_cards):
    """
    Display a single flashcard with formatting
    """
    # Clear screen (works on Unix-like systems)
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("=" * 60)
    print(f"FLASHCARD {card_number}/{total_cards}")
    print("=" * 60)
    print()
    
    # Display hanzi prominently
    print(f"汉字 (Hanzi):")
    print(f"  {flashcard['Hanzi']}")
    print()
    
    # Display pinyin
    print(f"拼音 (Pinyin):")
    print(f"  {flashcard['Pinyin']}")
    print()
    
    # Display meaning if available
    if flashcard.get('Meaning'):
        print(f"意思 (Meaning):")
        print(f"  {flashcard['Meaning']}")
        print()
    
    # Display description if available (truncated for readability)
    if flashcard.get('Description'):
        desc = flashcard['Description']
        if len(desc) > 200:
            desc = desc[:200] + "..."
        print(f"描述 (Description):")
        print(f"  {desc}")
        print()
    
    print("=" * 60)
    print(f"Next card in 10 seconds... (Press Ctrl+C to stop)")
    print("=" * 60)

def countdown_timer(seconds):
    """
    Display a countdown timer
    """
    for i in range(seconds, 0, -1):
        # Clear the last line and update countdown
        print(f"\rNext card in {i} seconds... (Press Ctrl+C to stop)", end="", flush=True)
        time.sleep(1)
    print(f"\rNext card in 0 seconds... (Press Ctrl+C to stop)")

def main():
    """
    Main function to run the hanzi display program
    """
    print("Loading flashcards...")
    flashcards = load_flashcards()
    
    if not flashcards:
        print("Failed to load flashcards. Exiting.")
        return
    
    print(f"\nStarting hanzi display program...")
    print(f"Total flashcards: {len(flashcards)}")
    print(f"Display interval: 10 seconds")
    print(f"Press Ctrl+C to stop the program")
    print("\n" + "="*60)
    
    # Shuffle flashcards for variety
    shuffled_cards = flashcards.copy()
    random.shuffle(shuffled_cards)
    
    try:
        card_index = 0
        while True:
            # Get current flashcard
            current_card = shuffled_cards[card_index]
            
            # Display the flashcard
            display_flashcard(current_card, card_index + 1, len(shuffled_cards))
            
            # Start countdown timer
            countdown_timer(10)
            
            # Move to next card (cycle back to beginning if needed)
            card_index = (card_index + 1) % len(shuffled_cards)
            
    except KeyboardInterrupt:
        print("\n\nProgram stopped by user.")
        print("Thanks for studying hanzi!")

if __name__ == "__main__":
    main() 