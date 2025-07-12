import requests
import json
from datetime import datetime

def download_flashcards():
    """
    Download flashcards from the API endpoint and save to JSON file
    """
    url = "https://5ecvq3d6ri.execute-api.eu-west-2.amazonaws.com/api/sheet/hanzi/hero"
    
    try:
        print("Downloading flashcards from API...")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        flashcards = response.json()
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flashcards_{timestamp}.json"
        
        # Save to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(flashcards, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully downloaded {len(flashcards)} flashcards")
        print(f"Saved to: {filename}")
        
        # Print some basic info about the flashcards
        if flashcards:
            print(f"\nSample flashcard structure:")
            sample = flashcards[0]
            for key, value in sample.items():
                print(f"  {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
        
        return filename
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading flashcards: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    download_flashcards() 