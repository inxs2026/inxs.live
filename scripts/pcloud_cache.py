#!/usr/bin/env python3
"""
ChiChi's pCloud Cache Manager
Searches and stores conversation cache in pCloud via rclone
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import re
from difflib import SequenceMatcher

RCLONE = Path.home() / ".local/bin/rclone"
PCLOUD_ROOT = "pcloud:/clawd"
CACHE_DIR = f"{PCLOUD_ROOT}/cache"
LOGS_DIR = f"{PCLOUD_ROOT}/logs"

def normalize_query(text):
    """Normalize query for comparison"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return ' '.join(text.split())  # Normalize whitespace

def extract_keywords(text, min_len=4):
    """Extract meaningful keywords from text"""
    words = normalize_query(text).split()
    # Filter out common words and keep words >= min_len
    stopwords = {'what', 'when', 'where', 'who', 'how', 'why', 'the', 'is', 'are', 'was', 'were', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may', 'might', 'must'}
    return [w for w in words if w not in stopwords and len(w) >= min_len]

def similarity_score(str1, str2):
    """Calculate similarity between two strings (0-1)"""
    return SequenceMatcher(None, normalize_query(str1), normalize_query(str2)).ratio()

def search_cache(query, threshold=0.8):
    """Search pCloud cache for similar queries"""
    keywords = extract_keywords(query)
    
    # List all cache files
    result = subprocess.run(
        [str(RCLONE), "lsf", f"{CACHE_DIR}/", "--recursive", "--files-only"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        return None
    
    cache_files = [f for f in result.stdout.strip().split('\n') if f.endswith('.json')]
    
    best_match = None
    best_score = 0
    
    for cache_file in cache_files:
        # Download cache file
        cache_path = f"{CACHE_DIR}/{cache_file}"
        result = subprocess.run(
            [str(RCLONE), "cat", cache_path],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            continue
        
        try:
            cache_data = json.loads(result.stdout)
            cached_query = cache_data.get('query', '')
            
            # Check keyword overlap
            cached_keywords = set(extract_keywords(cached_query))
            query_keywords = set(keywords)
            
            if not query_keywords:
                continue
            
            keyword_overlap = len(query_keywords & cached_keywords) / len(query_keywords)
            text_similarity = similarity_score(query, cached_query)
            
            # Combined score (weighted: 60% text similarity, 40% keyword overlap)
            score = (text_similarity * 0.6) + (keyword_overlap * 0.4)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = {
                    'data': cache_data,
                    'score': score,
                    'file': cache_file
                }
        except json.JSONDecodeError:
            continue
    
    return best_match

def store_cache(query, response, keywords=None):
    """Store query/response in pCloud cache"""
    if keywords is None:
        keywords = extract_keywords(query)
    
    cache_data = {
        'query': query,
        'response': response,
        'timestamp': datetime.now().isoformat(),
        'keywords': keywords
    }
    
    # Create date-based subfolder
    date_folder = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%H%M%S')
    
    # Sanitize filename from first few keywords
    filename_base = '_'.join(keywords[:3]) if keywords else 'cache'
    filename_base = re.sub(r'[^\w\-]', '', filename_base)[:30]
    filename = f"{filename_base}_{timestamp}.json"
    
    # Write to temp file
    temp_file = f"/tmp/chichi_cache_{timestamp}.json"
    with open(temp_file, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    # Upload to pCloud
    cache_path = f"{CACHE_DIR}/{date_folder}/"
    
    # Ensure directory exists
    subprocess.run([str(RCLONE), "mkdir", cache_path], capture_output=True)
    
    # Upload file
    result = subprocess.run(
        [str(RCLONE), "copy", temp_file, cache_path],
        capture_output=True, text=True
    )
    
    # Cleanup
    Path(temp_file).unlink()
    
    return result.returncode == 0

def log_query(query, cached=False, cache_file=None):
    """Log query to pCloud for tracking"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'query': query[:200],  # First 200 chars
        'cached': cached,
        'cache_file': cache_file
    }
    
    date = datetime.now().strftime('%Y-%m-%d')
    temp_log = f"/tmp/chichi_log_{datetime.now().strftime('%H%M%S')}.json"
    
    with open(temp_log, 'w') as f:
        json.dump(log_entry, f)
    
    log_path = f"{LOGS_DIR}/{date}/"
    subprocess.run([str(RCLONE), "mkdir", log_path], capture_output=True)
    subprocess.run([str(RCLONE), "copy", temp_log, log_path], capture_output=True)
    Path(temp_log).unlink()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  pcloud_cache.py search 'your query here'")
        print("  pcloud_cache.py store 'query' 'response' ['keyword1,keyword2']")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'search':
        query = sys.argv[2]
        result = search_cache(query)
        
        if result:
            print(json.dumps({
                'found': True,
                'score': result['score'],
                'response': result['data']['response'],
                'cached_query': result['data']['query'],
                'file': result['file']
            }))
        else:
            print(json.dumps({'found': False}))
    
    elif cmd == 'store':
        query = sys.argv[2]
        response = sys.argv[3]
        keywords = sys.argv[4].split(',') if len(sys.argv) > 4 else None
        
        success = store_cache(query, response, keywords)
        print(json.dumps({'stored': success}))
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
