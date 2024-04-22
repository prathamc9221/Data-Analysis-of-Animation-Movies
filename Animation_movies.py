from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient 
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import re

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client['Animation_movies']
collection = db['scores']

positive_words_list = ["awesome", "awe-inspiring", "authentic", "beautifully crafted", "best", "bold",
                  "brilliance",
                  "brilliant", "captivating", "charming", "charming", "cinematic excellence", "clever", "cleverness", "compelling", "courageous", "creatively", "delight", "delightful", "dazzling", "discerning", "dynamic", "emotional depth", "energetic", "engaging", "entertaining", "enthralling", "enchanting", "enjoyable", "enthralling", "exceptional", "exceptional", "excitement", "exciting", "excellent", "exhilarating", "expertly executed", "extraordinary", "fantastic", "flawless", "fulfilling", "fun", "good", "great", "gripping", "heartwarming", "hilarious", "humorous", "impactful", "impressive", "ingenious", "ingenious", "insightful", "inspiring", "inspirational", "intuitive", "invigorating", "joyful", "llyrical", "magical", "masterpiece", "memorable", "mesmerizing", "minds", "monumental", "must-watch", "nostalgic", "nuanced", "optimistic", "original", "outstanding", "outstanding", "peerless", "perfect", "performance", "performances", "phenomenal", "poignant", "popular", "powerful", "profound", "progressive", "radiant", "refreshing", "relevant", "remarkable", "resonant", "revolutionary", "resonant", "riveting", "satisfying", "seamless storytelling", "sincere", "stellar", "stellar performances", "strange", "strange powers", "stunning", "success", "successful", "superb", "suspenseful", "sweet", "talented", "thought-provoking", "thoughtful", "thrilling", "timely", "touching", "transcendent", "unforgettable", "unimaginative", "unparalleled", "unrivaled", "unsurpassed", "uplifting", "visionary", "visuals", "visually stunning", "witty"]

negative_words_list = ["abominable", "absurd", "absurd", "amateurish", "annoying", "appalling", "appalling", 
                "atrocious", "awkward", "bad", "bland", "boring", "cheesy", "childish", "clichéd", "clumsy", "confusing", "contrived", "contrived", "corny", "cringe-worthy", "cynical", "deplorable", "despondent", "detestable", "diabolical", "disappointing", "disgusting", "dismal", "dreadful", "dull", "dumb", "execrable", "forgettable", "forced", "ghastly", "grim", "gross", "grating", "hackneyed", "haphazard", "horrendous", "irksome", "irritating", "juvenile", "laughable", "ludicrous", "lackluster", "lifeless", "miserable", "messy", "melancholy", "monstrous", "obnoxious", "offensive", "offensive", "off-putting", "overrated", "pointless", "ponderous", "poorly executed", "predictable", "preposterous", "pretentious", "repellent", "repugnant", "repulsive", "repulsive", "ridiculous", "silly", "sloppy", "sordid", "stale", "stupid", "subpar", "sucky", "sucks", "suspenseful", "tacky", "tedious", "terrible", "thoughtless", "tragic", "trite", "unappealing", "unconvincing", "underwhelming", "unimaginative", "uninspiring", "unpleasant", "unrealistic", "unrewarding", "unsatisfying", "unsophisticated", "unwatchable", "weak plot", "worse", "worst", "worst", "wretched"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/task1.html")
def task1():
    return render_template("task1.html")

@app.route("/task2.html")
def task2():
    return render_template("task2.html")

@app.route("/task3.html")
def task3():
    return render_template("task3.html")

@app.route("/task4.html")
def task4():
    return render_template("task4.html")

@app.route('/submit-task-1', methods=['POST'])
def get_genre_result():
    selected_year = request.form.get('selected_year')
  
    pipeline = [
    {"$match": {"release_date": {"$regex": selected_year}, "genres": {"$ne": ""}}},
    {"$addFields": {"genre_words": {"$split": ["$genres", ", "]}}},  # Split genres into an array
    {"$unwind": "$genre_words"},  # Deconstruct the array to get separate documents for each genre
    {"$match": {"genre_words": {"$not": {"$regex": "Animation"}}}},  # Exclude documents with "Animation" genre
    {"$project": {"genre_name": "$genre_words", "overview": 1, "popularity": 1, "revenue": 1}},
    {"$addFields": {"review_content_array": {"$ifNull": ["$overview", ""]}}},  # Replace null with empty array
    {"$addFields": {
        "positive_words_count": {
            "$size": {
                "$filter": {
                    "input": {"$split": [{"$toString": "$review_content_array"}, ", "]},
                    "as": "word",
                    "cond": {"$in": ["$$word", positive_words_list]}
                }
            }
        },
        "score": {
            "$add": [
                {"$multiply": ["$popularity", 0.89]},  # Popularity contributes 89%
                {"$sum": ["$positive_words_count", 0.10]},  # Positive words count contributes 10%
                {"$multiply": [{"$ifNull": ["$revenue", 0]}, 0.01]}  # Revenue contributes 1%
            ]
        }
    }},
    {"$group": {"_id": "$genre_name", "total_score": {"$sum": "$score"}}},
    {"$addFields": {"genre_name": {"$ifNull": ["$_id", "Unknown"]}}},
    {"$project": {"_id": 0, "genre_name": 1, "total_score": 1}},
    {"$sort": {"total_score": -1}}
]

    result = list(collection.aggregate(pipeline))

    try:
        result = list(db.scores.aggregate(pipeline))
        #print(result)
    except Exception as e:
        print("An error occurred:", e)

    # Execute the aggregation pipeline
    result = list(collection.aggregate(pipeline))


    # Process the selected year (you can replace this with your own logic)
    response_data = {'result': result, 'message': 'Task 1 data sent successfully'}

    print(response_data)
    
    # Return the response in JSON format
    return jsonify(response_data)

@app.route('/submit-task-2', methods=['POST'])
def get_actor_data():
    production_companies = request.form.get('selected_actor')

    pipeline = [
    {"$match": {"production_companies": {"$regex": production_companies}, "genres": {"$ne": ""}}},  # Filter by production company and ensure genres is not empty
    {"$addFields": {"genre_words": {"$split": ["$genres", ", "]}}},  # Split genres into an array
    {"$unwind": "$genre_words"},  # Unwind the array to create separate documents for each genre
    {"$match": {"genre_words": {"$not": {"$regex": "Animation"}}}},  # Exclude documents with "Animation" genre
    {"$project": {"genre_name": "$genre_words", "tagline": 1, "popularity": 1, "revenue": 1}},
    {"$addFields": {"review_content_array": {"$ifNull": ["$tagline", ""]}}},  # Replace null with empty array
    {"$addFields": {
        "positive_words_count": {
            "$size": {
                "$filter": {
                    "input": {"$split": [{"$toString": "$review_content_array"}, " "]},
                    "as": "word",
                    "cond": {"$in": ["$$word", positive_words_list]}
                }
            }
        },
        "score": {
            "$add": [
                {"$multiply": ["$popularity", 0.89]},  # Popularity contributes 89%
                {"$multiply": [{"$ifNull": ["$revenue", 0]}, 0.01]}  # Revenue contributes 1%
            ]
        }
    }},
    {"$group": {"_id": "$genre_name", "total_score": {"$sum": "$score"}}},
    {"$addFields": {"genre_name": {"$ifNull": ["$_id", "Unknown"]}}},
    {"$project": {"_id": 0, "genre_name": 1, "total_score": 1}},
    {"$sort": {"total_score": -1}}
]

#     pipeline = [
#     {"$match": {"production_companies": {"$regex": production_companies}, "genres": {"$ne": ""}}},  # Filter by production company and ensure genres is not empty
#     {"$addFields": {"first_genre_word": {"$arrayElemAt": [{"$split": ["$genres", " "]}, 0]}}},
#     {"$match": {"first_genre_word": {"$not": {"$regex": "Animation"}}}},  # Exclude documents with "Animation" genre
#     {"$project": {"first_genre_word": 1, "tagline": 1, "popularity": 1, "revenue": 1}},
#     {"$addFields": {"review_content_array": {"$ifNull": ["$tagline", ""]}}},  # Replace null with empty array
#     {"$addFields": {
#         "positive_words_count": {
#             "$size": {
#                 "$filter": {
#                     "input": {"$split": [{"$toString": "$review_content_array"}, " "]},
#                     "as": "word",
#                     "cond": {"$in": ["$$word", positive_words_list]}
#                 }
#             }
#         },
#         "score": {
#             "$add": [
#                 {"$multiply": ["$popularity", 0.89]},  # Popularity contributes 89%
#                 {"$sum": ["$positive_words_count", 0.10]},  # Positive words count contributes 10%
#                 {"$multiply": [{"$ifNull": ["$revenue", 0]}, 0.01]}  # Revenue contributes 1%
#             ]
#         }
#     }},
#     {"$group": {"_id": "$first_genre_word", "total_score": {"$sum": "$score"}}},
#     {"$addFields": {"genre_name": {"$ifNull": ["$_id", "Unknown"]}}},
#     {"$project": {"_id": 0, "genre_name": 1, "total_score": 1}},
#     {"$sort": {"total_score": -1}}
# ]

    # Execute the aggregation pipeline
    result = list(collection.aggregate(pipeline))

    try:
        result = list(db.scores.aggregate(pipeline))
        #print(result)
    except Exception as e:
        print("An error occurred:", e)    

    # Process the selected year (you can replace this with your own logic)
    response_data = {'result': result, 'message': 'Task 2 data sent successfully'}
    
    print(response_data)

    # Return the response in JSON format
    return jsonify(response_data)

@app.route('/submit-task-3', methods=['POST'])
def get_movie_data():
    selected_movie = request.form.get('selected_movie')

#     pipeline = [
#     {"$match": {"original_title": {"$regex": f"^{selected_movie}$", "$options": "i"}}},  # Exact match on movie title
#     {"$project": {"_id": 0, "vote_average": 1, "percentage_profit": {
#         "$cond": {
#             "if": {"$eq": ["$budget", 0]},  # Check if budget is zero to avoid division by zero
#             "then": None,  # Set percentage_profit to null if budget is zero
#             "else": {"$subtract": [{"$divide": [{"$ifNull": ["$revenue", 0]}, "$budget"]}, 1]}  # Calculate percentage_profit
#         }
#     }}},  # Project necessary fields, excluding _id
# ]

    pipeline = [
    {"$match": {"original_title": {"$regex": f"^{selected_movie}$", "$options": "i"}}},  # Exact match on movie title
    {"$addFields": {
        "languages": {"$size": {"$split": [{"$ifNull": ["$spoken_languages", ""]}, ","]}}  # Count the number of languages and convert to string separated by commas
    }},
    {"$project": {"_id": 0, "vote_average": 1, "percentage_profit": {
        "$cond": {
            "if": {"$eq": ["$budget", 0]},  # Check if budget is zero to avoid division by zero
            "then": None,  # Set percentage_profit to null if budget is zero
            "else": {"$subtract": [{"$divide": [{"$ifNull": ["$revenue", 0]}, "$budget"]}, 1]}  # Calculate percentage_profit
        }
    }, "languages": {"$toString": "$languages"}}},  # Convert languages to string separated by commas
]

    # Execute the aggregation pipeline
    result = list(collection.aggregate(pipeline))

    # Process the selected year (you can replace this with your own logic)
    response_data = {'result': result, 'message': 'Task 3 data sent successfully'}

    print(response_data)

    from bson import ObjectId

# Assuming response_data is the dictionary containing the result
    # for item in response_data['result']:
        # item['_id'] = str(item['_id'])  # Convert ObjectId to string
    
    # Return the response in JSON format
    return jsonify(response_data)

@app.route('/submit-task-4', methods=['POST'])
def get_movie_with_keyword():
    selected_actor = request.form.get('selected_actor')
    selected_keyword = request.form.get('selected_keyword')
    print(selected_actor)
    print(selected_keyword)

    # Define the lists for each genre
    keyword_lists = {
        "kill": ["kill", "crime", "criminal", "hunted", "murder", "avenge", "attackers", "assaulted", "spy", 
                 "fight", "money", "accused", "prison",
                "mysterious", "death", "police", "agent", "mission", "mystery", "detective", "victim", "steals", "revenge", "cop", "rape",
                "gangster", "drug", "plan", "enemy", "rob", "violence", "mafia", "action", "violent", "abused", "crime", "theif", "desperate"],
        
        "love": ["love", "romantic", "romance", "relationship", "girlfriend", "boyfriend", "happy", "loves", 
                 "loved", "interested", "heart",
                "crush", "like", "friendship", "dumped"],
        
        "horror": ["vampire", "supernatural", "dark", "hunger", "zombies", "danger", "horrific", "murders",
                    "suspicious", "corpses",
                "monster", "death", "bloody", "soul", "rebirth", "deceased", "suicide", "frightening", "sinister", "suspect", "killer",
                "cop", "killed", "hunt", "hunter"],
        
        "documentary": ["history", "community", "territory", "fighter", "warrior", "mankind", "victory", 
                        "war", "historic", "rebels", "government",
                "historical", "believers", "honorary", "brave", "national", "festival" ,"force", "struggle", "ancestral", "dignity","legacy",
                "legendary", "power", "century", "politics", "culture","mission", "mockumentary"],
        
        "thrill": ["adventure", "thrill", "magical", "creatures", "team", "discover", "agent", "mystical", 
                   "heroic", "fate", "boxer", "weapon",
                "survivor", "journey", "storm", "mission", "shooting", "living", "remote", "tale", "mountaineer", "mob", "age", 
                "opportunity", "relocate", "fortune", "misaventure" ,"revenge"]
    }

    # Get user input for the desired genre
    selected_list =  []
    if selected_keyword not in keyword_lists.keys():
        print("no genre in dict")
    else:
        selected_list = keyword_lists[selected_keyword]
    
    # MongoDB aggregation pipeline
    pipeline = [
        {
            "$match": {
                "title": {"$regex": selected_actor, "$options": "i"},
                "overview": {
                    "$regex": "|".join(selected_list),
                    "$options": "i"
                }
            }
        },
        {
            "$group": {
                "_id": "$movie_title",
                "vote_average": {"$first": "$vote_average"}
            }
        },
        {
            "$project": {
                "movie_title": "$_id",
                "vote_average": 1,
                "_id": 0
            }
        },
        {
            "$sort": {"vote_average": -1}
        },
        {
            "$limit": 5
        }
    ]

    # Execute the query
    result = list(collection.aggregate(pipeline))

    # Process the selected year (you can replace this with your own logic)
    response_data = {'result': result, 'message': 'Task 4 data sent successfully'}

    print(response_data)
    
    # Return the response in JSON format
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True,port=5000)
