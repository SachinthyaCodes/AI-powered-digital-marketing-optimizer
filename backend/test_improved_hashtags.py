"""
Test script to verify improved hashtag generation with real content matching
"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Test cases with diverse content
test_cases = [
    {
        "name": "Fitness Workout Post",
        "caption": "Morning workout session complete! 💪 Feeling strong and energized",
        "content": "Daily gym routine, strength training, fitness motivation, healthy lifestyle",
        "platform": "Instagram"
    },
    {
        "name": "Food - Pizza Post",
        "caption": "Homemade pizza night 🍕 Fresh ingredients, amazing taste!",
        "content": "Delicious pizza, Italian food, cooking at home, foodie life, tasty dinner",
        "platform": "Instagram"
    },
    {
        "name": "Travel - Beach Vacation",
        "caption": "Paradise found! 🏖️ Beach vacation vibes",
        "content": "Beach sunset, tropical island, ocean views, summer vacation, travel adventure",
        "platform": "Instagram"
    },
    {
        "name": "Fashion - New Outfit",
        "caption": "Today's outfit of the day ✨",
        "content": "Trendy fashion, stylish clothing, new dress, fashion blogger, style inspiration",
        "platform": "Instagram"
    },
    {
        "name": "Technology - New Gadget",
        "caption": "Checking out the latest tech gadget 📱",
        "content": "New smartphone, innovation, technology review, latest gadgets, digital trends",
        "platform": "Instagram"
    },
    {
        "name": "Business - Startup Launch",
        "caption": "Excited to announce our startup launch! 🚀",
        "content": "New business, entrepreneur journey, startup life, success, growth mindset",
        "platform": "Instagram"
    },
    {
        "name": "Nature - Mountain Hiking",
        "caption": "Exploring the mountains this weekend ⛰️",
        "content": "Hiking adventure, outdoor activities, nature photography, mountain views, wilderness",
        "platform": "Instagram"
    },
    {
        "name": "Motivation - Daily Inspiration",
        "caption": "Never give up on your dreams 💫",
        "content": "Motivation quotes, inspiration, success mindset, goals, positive vibes",
        "platform": "Instagram"
    }
]

def test_hashtag_generation():
    """Test hashtag generation for different content types"""
    
    print("=" * 100)
    print("TESTING IMPROVED HASHTAG GENERATION")
    print("=" * 100)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n\n{'='*100}")
        print(f"Test Case {i}: {test['name']}")
        print(f"{'='*100}")
        print(f"Caption: {test['caption']}")
        print(f"Content: {test['content']}")
        print(f"Platform: {test['platform']}")
        print("-" * 100)
        
        # Prepare request data
        data = {
            "caption": test['caption'],
            "content": test['content'],
            "platform": test['platform'],
            "postDate": "2025-12-29",
            "postTime": "14:00",
            "followers": "5000",
            "adBoost": False
        }
        
        try:
            # Make API request
            response = requests.post(f"{BASE_URL}/api/predict", json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract hashtags
                hashtags = result.get('hashtags', [])
                
                print(f"\n✅ Generated {len(hashtags)} Hashtags:")
                print("-" * 100)
                
                # Display hashtags in a formatted way
                for j in range(0, len(hashtags), 5):
                    print("  " + "  ".join(hashtags[j:j+5]))
                
                # Analyze relevance
                print("\n📊 Relevance Analysis:")
                caption_words = test['caption'].lower().split()
                content_words = test['content'].lower().split()
                all_text = test['caption'].lower() + " " + test['content'].lower()
                
                relevant_count = 0
                for hashtag in hashtags:
                    hashtag_word = hashtag.replace('#', '').lower()
                    if hashtag_word in all_text or any(word in hashtag_word for word in caption_words + content_words):
                        relevant_count += 1
                
                relevance_percentage = (relevant_count / len(hashtags)) * 100 if hashtags else 0
                print(f"  • Directly relevant hashtags: {relevant_count}/{len(hashtags)} ({relevance_percentage:.1f}%)")
                
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"\n❌ Exception: {e}")
        
        print("=" * 100)

if __name__ == "__main__":
    print("\n🚀 Starting Hashtag Generation Tests...\n")
    print("Make sure the backend is running on http://localhost:5000\n")
    
    try:
        # Check if backend is running
        response = requests.get(f"{BASE_URL}/api/history")
        if response.status_code == 200:
            print("✅ Backend is running!\n")
            test_hashtag_generation()
        else:
            print("❌ Backend is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")
