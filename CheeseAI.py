import pandas as pd
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer



# Global variable for the dataset
df = None





# Load dataset
def load_dataset():
    global df  # Declare df as global
    df = pd.read_csv("cheeses.csv")
    return df





# Preprocess dataset for feature extraction
def preprocess_data():
    global df  # Declare df as global
    attributes_to_process = [
        'milk', 'country', 'region', 'family', 'type', 
        'texture', 'rind', 'color', 'flavor', 'aroma'
    ] 

    # Fill missing values or 'NA' with 'Unknown' for all attributes
    for attr in attributes_to_process:
        df[attr] = df[attr].replace(['NA', ''], 'Unknown').fillna('Unknown')

    # Convert boolean columns to string for concatenation
    df['vegetarian'] = df['vegetarian'].astype(str)
    df['vegan'] = df['vegan'].astype(str)

    # Combine important features into a single 'features' column
    df['features'] = df[attributes_to_process].apply(lambda row: ' '.join(row.values), axis=1)
    df['features'] += ' ' + df['vegetarian'] + ' ' + df['vegan']  # Optionally include 'vegetarian' and 'vegan'
    
    return df





# Initialize TF-IDF vectorizer and compute cosine similarity
def compute_cosine_similarity():
    global df  # Declare df as global
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return tfidf, cosine_sim, tfidf_matrix





# Recommend cheeses based on user preferences
def recommend_based_on_preferences(preferences):
    global df  # Declare df as global
    user_pref_list = [value for key, value in preferences.items() if value != 'N/A']
    user_preferences = ' '.join(user_pref_list)

    # Call compute_cosine_similarity() to get tfidf and cosine_sim
    tfidf, cosine_sim, tfidf_matrix = compute_cosine_similarity()

    # Transform user preferences into TF-IDF space
    user_tfidf = tfidf.transform([user_preferences])
    sim_scores = cosine_similarity(user_tfidf, tfidf_matrix)
    
    # Enumerate similarities
    sim_scores = list(enumerate(sim_scores[0]))
    sim_indices = [i[0] for i in sim_scores]  # All indices
    
    # Compute the number of matching attributes
    recommendations = []
    for sim_idx in sim_indices:
        cheese_name = df['cheese'].iloc[sim_idx]
        shared_attributes = [
            f"{attr}: {df.iloc[sim_idx][attr]}" 
            for attr, value in preferences.items() 
            if value != 'N/A' and value in df.iloc[sim_idx][attr]
        ]
        # Only consider cheeses that match at least one attribute
        if shared_attributes:
            recommendations.append((cheese_name, shared_attributes))
    
    # Sort by the number of shared attributes (descending), then by cosine similarity
    recommendations = sorted(recommendations, key=lambda x: (-len(x[1]), sim_scores[df.index[df['cheese'] == x[0]].tolist()[0]][1]))

    # Return the top 5 recommendations
    return recommendations[:5]





# Group cheeses by a specific attribute type
def group_cheeses_by_attribute(attribute):
    global df  # Declare df as global
    if attribute not in df.columns:
        return f"Attribute '{attribute}' not found in the dataset."

    grouped_cheeses = {}
    
    for _, row in df.iterrows():
        # Multi-value attributes are stored in quotes, split while respecting quotes
        attribute_values = [value.strip() for value in row[attribute].split(', ') if value != 'Unknown']
        for value in attribute_values:
            if value not in grouped_cheeses:
                grouped_cheeses[value] = []
            grouped_cheeses[value].append(row['cheese'])
    
    # Sort the cheeses in each group for better readability
    for group in grouped_cheeses:
        grouped_cheeses[group] = sorted(grouped_cheeses[group])
    
    return grouped_cheeses





# Example usage function for recommending based on preferences
def example_recommendations():
    # Example user preferences
    preferences = {
        'milk': 'cow',
        'country': 'N/A',
        'region': 'N/A',
        'family': 'Blue',
        'type': 'semi-soft',
        'texture': 'creamy',
        'rind': 'N/A',
        'flavor': 'sweet',
        'aroma': 'buttery',
        'vegetarian': 'TRUE',
        'vegan': 'N/A'
    }

    # Get recommendations based on preferences
    recommendations = recommend_based_on_preferences(preferences)
    
    # Display the recommendations
    print("\nRecommended cheeses based on preferences:\n")
    for cheese, shared_attrs in recommendations:
        print(f"- {cheese} (shared attributes: {', '.join(shared_attrs)})")





# Example usage function for grouping cheeses by attribute
def example_grouping():
    # Example attribute type
    attribute_type = "milk"  # Change to other attributes like "country", "texture", etc.
    
    # Group cheeses by attribute
    grouped_cheeses = group_cheeses_by_attribute(attribute_type)

    # Display the grouped cheeses
    print(f"\nCheeses grouped by '{attribute_type}':\n")
    for group, cheeses in grouped_cheeses.items():
        print(f"{group}: {', '.join(cheeses)}")





# Run examples
if __name__ == "__main__":
    
    # Load and preprocess dataset
    load_dataset()
    preprocess_data()

    example_recommendations()  # Display example recommendations
    example_grouping()  # Display example grouping






"""
# Program Notes:
"""

"""
INITIALIZATION:
Upon Initialization of the first page, Call the following functions:

    load_dataset()
    preprocess_data()

    This will load the dataset into a filereader then process/clean the data.
"""



"""
LOGIN/REGISTER:
Enter a username and password into login screen. 
   If it exists in a file, go to homepage.
   If it doesn't, throw exception.

On sign up page, enter any username or password to create one.
   If username already exists in file, throw exception.
   If not, add username/password to file.
"""



"""
BOTH RECOMMENDING + CLASSIFYING
Ensure all attributes and attribute types are listed as options (case sensitive).
    I recommend writing code to return every attribute and attribute type (separating each attribute for multi-valued attributes. This part may be more complicated than it sounds)
"""



"""
GROUP/CLASSIFY CHEESES:
When user selects an attribute type, it should be sent as the parameter to the following function:

    grouped_cheeses = group_cheeses_by_attribute(attribute_type)

        This returns a long string containing all cheeses sorted into groups based on that attribute type.

        You can follow the parameter and return formatting established by the example_grouping() function.

!!! Currently, the backend code does not support allowing multiple attribute types to be selected at a time.
    Pick 1 of 2 options to resolve this:
    1. Allow code to sort based on 2 different attribute types.
    2. Only allow 1 selection from the website page.

    I recommend 2 (only allowing 1 selection) because there is already a LONG string that returns from sorting based on a single attribute type.
    Allowing multiple selections would make it longer.
"""



"""
RECOMMEND CHEESES:
When a user selects attributes, they should be sent as the parameter to the following function:

    recommendations = recommend_based_on_preferences(preferences)

        This returns a list of 5 similar cheeses along with the attributes that makes them similar.

        You can follow the parameter and return formatting established by the example_recommendations() function.
"""



"""
BACKEND MAIN FUNCTION
Upon completion of the program, delete the following functions since they were just for examples:
if __name__ == "__main__"
def example_recommendations()
def example_grouping()
"""





# Dataset Notes:

#1187 total cheeses with 19 total attributes
#1. Omit Cheese because it is the actual cheese rather than an attribute.
#2. Omit Url because it obviously has nothing to do with its attributes.
#3. Include Milk because there are 1151 non-null values with 21 unique, thus sorting nearly all cheeses very effectively.
#4. Include Country because there are 1176 non-null values with 82 unique values, thus sorting nearly all cheeses effectively.
#5. Include Region because there are 885 non-null values with 350 unique values, thus sorting most cheeses somewhat well (67 are wisconsin).
#6. Include Family because, while there is only 489 entries, 22 of them are unique, thus it will sort those 489 cheeses effectively.
#7. Include Type because it has 1174 non-null values with 85 unique values, thus sorting nearly all cheeses effectively.
#8 & 9. Omit Fat_Content and Calcium_Content because they use integer values, and if we are selecting from a selection of integer values it may look weird (selection 31%, 52%, 66%, 68%, ...). The program wouldn't be able to understand a value that isn't from the list because it doesnt understand the number, only the literal string.
    #There are also not many entries for them, thus most cheese similarities aren't effected and the program wouldn't be very effected.
    #There are also not many overlapping values (86/248 are unique for fat, and 25/25 are unique for calcium).
#10. Include Texture because there are 1129 non-null values with 309 unique values, thus sorting nearly all cheeses somewhat decently. It is also an important attribute.
#11. Include Rind because there are 945 non-null values with 13 unique, thus sorting most cheeses very effectively.
#12. Include Color because there are 1045 non-null values with 18 unique values, thus sorting nearly all cheeses very effectively.
#13. Include Flavor because there are 1089 non-null values with 627 unique values, thus sorting nearly all cheeses somewhat poorly. But it is an important attribute.
#14. Include Aroma because there are 929 non-null values with 331 unique values, thus sorting most cheeses somewhat poorly. But it is an important attribute.
#15 & 16. Include Vegetarian and Vegan because they both have 748 non-null values, with only 2 unique values (T/F), thus sorting those 748 very well.
    #Remove from AI, and instead make it a hard-filter? If someone adds they prefer vegan or vegetarian cheese, they likely wouldn't accept non-vegan or vegetarian options, even if they are otherwise similar.
        #However, also note that not every vegan or vegetarian cheese is marked as such. Thus it may filter some cheeses that actually ARE vegan or vegetarian.
#17. Omit Synonyms because it obviously has nothing to do with its attributes.
#18. Omit Alt_spellings because it obviously has nothing to do with its attributes.
#19. Omit producers because there are 787 non-null values, with 319 of them unique. While, a decent amount of the cheeses have a producer value, each producer only produces 2 cheeses on average.


