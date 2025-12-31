"""
Test script to verify hashtag generation with NLP keyword extraction
"""

import re
from collections import Counter

# Sample comprehensive hashtag database (smaller for testing)
HASHTAG_DATABASE = {
    'food': ['#foodie', '#delicious', '#yummy', '#foodporn', '#instafood'],
    'travel': ['#travel', '#wanderlust', '#explore', '#adventure', '#travelgram'],
    'fitness': ['#fitness', '#gym', '#workout', '#fitfam', '#health'],
    'technology': ['#tech', '#technology', '#innovation', '#gadgets', '#digital'],
    'business': ['#business', '#entrepreneur', '#marketing', '#success', '#startup'],
    'fashion': ['#fashion', '#style', '#ootd', '#fashionista', '#trendy'],
    'lifestyle': ['#lifestyle', '#life', '#instagood', '#instadaily', '#inspiration'],
    'motivation': ['#motivation', '#inspiration', '#success', '#goals', '#hustle'],
    'photography': ['#photography', '#photooftheday', '#picoftheday', '#camera', '#photo'],
    'instagram': ['#instagood', '#instagram', '#instadaily', '#instalike', '#instapost'],
    'viral': ['#viral', '#trending', '#explorepage', '#explore', '#like4like'],
}

def extract_keywords_from_text(text):
    """Extract important keywords from text"""
    # Clean and preprocess text
    text_clean = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    text_clean = ' '.join(text_clean.split())
    
    # Common stop words
    stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was', 'were', 
                  'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 
                  'should', 'could', 'may', 'might', 'must', 'can', 'of', 'for', 'to', 'in', 
                  'by', 'with', 'from', 'and', 'or', 'but', 'not', 'this', 'that', 'these', 
                  'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
    
    # Extract words
    words = text_clean.split()
    
    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count word frequency
    word_freq = Counter(keywords)
    
    # Get most common keywords
    top_keywords = [word for word, count in word_freq.most_common(15)]
    
    return top_keywords

def match_hashtags(keywords, text):
    """Match hashtags based on keywords"""
    matched = []
    text_lower = text.lower()
    
    # Score categories
    category_scores = {}
    
    for category, hashtags in HASHTAG_DATABASE.items():
        score = 0
        # Direct category match
        if category in text_lower:
            score += 10
        
        # Keyword matches
        for keyword in keywords:
            if keyword in category:
                score += 5
        
        if score > 0:
            category_scores[category] = score
    
    # Sort by score
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Collect hashtags
    for category, score in sorted_categories[:6]:
        hashtags = HASHTAG_DATABASE[category]
        num_hashtags = min(3 if score >= 10 else 2, len(hashtags))
        matched.extend(hashtags[:num_hashtags])
    
    return matched

# Test cases
test_cases = [
    {
        'caption': 'Check out my new workout routine! 💪',
        'content': 'Daily fitness motivation and gym session. Building strength and staying healthy.'
    },
    {
        'caption': 'Delicious homemade pizza 🍕',
        'content': 'Fresh ingredients, amazing taste. Perfect dinner recipe for food lovers!'
    },
    {
        'caption': 'Exploring the mountains this weekend',
        'content': 'Travel adventure, hiking, beautiful nature and stunning views'
    },
    {
        'caption': 'New fashion collection launch',
        'content': 'Trendy outfits, stylish clothing, fashion blogger lifestyle'
    },
    {
        'caption': 'Latest tech gadgets review',
        'content': 'Innovation in technology, new smartphone features and digital trends'
    }
]

print("=" * 80)
print("HASHTAG GENERATION TEST - NLP Keyword Extraction")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\n\nTest Case {i}:")
    print(f"Caption: {test['caption']}")
    print(f"Content: {test['content']}")
    print("-" * 80)
    
    full_text = f"{test['caption']} {test['content']}"
    
    # Extract keywords
    keywords = extract_keywords_from_text(full_text)
    print(f"Extracted Keywords: {keywords[:10]}")
    
    # Match hashtags
    hashtags = match_hashtags(keywords, full_text)
    
    # Add platform and viral tags
    hashtags.extend(['#instagood', '#instadaily', '#viral', '#trending'])
    
    # Remove duplicates
    seen = set()
    unique_hashtags = []
    for tag in hashtags:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            unique_hashtags.append(tag)
    
    result = unique_hashtags[:15]
    
    print(f"Generated Hashtags ({len(result)}): {', '.join(result)}")
    print("=" * 80)
