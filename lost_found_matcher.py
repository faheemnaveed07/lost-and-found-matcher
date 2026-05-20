from datetime import datetime

# ---------- SAMPLE DATA ----------
lost_items = [
    {"id": 1, "item": "black wallet", "location": "cafeteria",
     "time": "2026-05-10 01:00 PM"},
    {"id": 2, "item": "silver iphone", "location": "library",
     "time": "2026-05-10 03:00 PM"},
]

found_items = [
    {"id": 101, "item": "black leather wallet", "location": "cafeteria",
     "time": "2026-05-10 02:30 PM"},
    {"id": 102, "item": "silver phone", "location": "library hall",
     "time": "2026-05-10 03:45 PM"},
    {"id": 103, "item": "red umbrella", "location": "parking",
     "time": "2026-05-10 09:00 AM"},
]

# Common colors that typically appear in item descriptions
COLORS = {"black", "white", "red", "blue", "green", "silver",
          "gold", "yellow", "brown", "grey", "gray", "pink"}


# ---------- HELPER FUNCTIONS ----------

def get_words(text):
    """Convert text into a set of lowercase words for easy comparison."""
    return set(text.lower().split())


def description_similarity(lost_desc, found_desc):
    """
    Calculate Jaccard Similarity between two descriptions.
    Formula: common words / total unique words

    Example: "black wallet" vs "black leather wallet"
        common = {black, wallet} = 2
        total  = {black, wallet, leather} = 3
        score  = 2/3 = 0.67
    """
    words_lost = get_words(lost_desc)
    words_found = get_words(found_desc)

    common = words_lost & words_found       # intersection
    total = words_lost | words_found        # union

    if not total:
        return 0
    return len(common) / len(total)


def color_similarity(lost_desc, found_desc):
    """Extract colors from both descriptions and compare them."""
    lost_colors = get_words(lost_desc) & COLORS
    found_colors = get_words(found_desc) & COLORS

    # If either description has no color, return a neutral score
    if not lost_colors or not found_colors:
        return 0.5

    # If any color matches, return a full score
    if lost_colors & found_colors:
        return 1.0
    return 0.0


def location_similarity(loc1, loc2):
    """
    Compare two locations:
    - Exactly the same       -> 1.0
    - Partial match          -> 0.7  (e.g. "library" vs "library hall")
    - Completely different   -> 0.0
    """
    loc1, loc2 = loc1.lower(), loc2.lower()

    if loc1 == loc2:
        return 1.0
    if loc1 in loc2 or loc2 in loc1:
        return 0.7
    return 0.0


def time_similarity(time1, time2):
    """
    Score based on the time gap between two timestamps:
    - Within 1 hour   -> 1.0
    - Within 3 hours  -> 0.7
    - Within 6 hours  -> 0.4
    - More than 6 hrs -> 0.1
    """
    fmt = "%Y-%m-%d %I:%M %p"
    t1 = datetime.strptime(time1, fmt)
    t2 = datetime.strptime(time2, fmt)

    diff_hours = abs((t2 - t1).total_seconds()) / 3600

    if diff_hours <= 1:
        return 1.0
    if diff_hours <= 3:
        return 0.7
    if diff_hours <= 6:
        return 0.4
    return 0.1


# ---------- MAIN MATCHING FUNCTION ----------

def match_score(lost, found):
    """Calculate the final weighted match score between a lost and a found item."""
    desc_score = description_similarity(lost["item"], found["item"])
    color_score = color_similarity(lost["item"], found["item"])
    loc_score = location_similarity(lost["location"], found["location"])
    time_score = time_similarity(lost["time"], found["time"])

    # Weighted total (description has the highest weight as it is the strongest signal)
    total = (0.4 * desc_score +
             0.2 * color_score +
             0.2 * loc_score +
             0.2 * time_score)

    return {
        "found_id": found["id"],
        "found_item": found["item"],
        "score": round(total, 2),
        "breakdown": {
            "description": round(desc_score, 2),
            "color": round(color_score, 2),
            "location": round(loc_score, 2),
            "time": round(time_score, 2),
        }
    }


def find_matches(lost_list, found_list, threshold=0.4):
    """For each lost item, return possible matches sorted by score (highest first)."""
    results = {}

    for lost in lost_list:
        matches = []
        for found in found_list:
            result = match_score(lost, found)
            if result["score"] >= threshold:
                matches.append(result)

        # Best match should appear at the top
        matches.sort(key=lambda x: x["score"], reverse=True)
        results[lost["id"]] = {
            "lost_item": lost["item"],
            "matches": matches
        }
    return results


# ---------- RUN & PRINT ----------

if __name__ == "__main__":
    results = find_matches(lost_items, found_items)

    for lost_id, data in results.items():
        print(f"\nLost Item #{lost_id}: {data['lost_item']}")
        print("-" * 50)
        if not data["matches"]:
            print("  No match found")
            continue
        for m in data["matches"]:
            print(f"  Found #{m['found_id']}: {m['found_item']}")
            print(f"    Total Score: {m['score']}")
            print(f"    Breakdown  : {m['breakdown']}")
