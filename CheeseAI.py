import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the cheese data
df = pd.read_csv("C:/Users/withe/OneDrive/Desktop/CheeseAIProjectPrePrototype/cheeses.csv")

# Display the info of the data
print("\nBase .csv file info\n")
print(df.info())
print("\n")



# Convert all boolean columns to string before concatenation
df['vegetarian'] = df['vegetarian'].astype(str)
df['vegan'] = df['vegan'].astype(str)

# Fill missing values with empty strings for the features we're interested in (cheese,url,region,family,fat_content,calcium_content,synonyms,alt_spellings,producers omitted)
df['milk'] = df['milk'].fillna('')
df['country'] = df['country'].fillna('')
df['region'] = df['region'].fillna('')
df['family'] = df['family'].fillna('')
df['type'] = df['type'].fillna('')
df['texture'] = df['texture'].fillna('')
df['rind'] = df['rind'].fillna('')
df['color'] = df['color'].fillna('')
df['flavor'] = df['flavor'].fillna('')
df['aroma'] = df['aroma'].fillna('')

# Combine important features into a single 'features' column
df['features'] = (df['milk']
    + ' ' + df['country']
    + ' ' + df['region']
    + ' ' + df['family']
    + ' ' + df['type']
    + ' ' + df['texture']
    + ' ' + df['rind']
    + ' ' + df['color']
    + ' ' + df['flavor']
    + ' ' + df['aroma']
    + ' ' + df['vegetarian']
    + ' ' + df['vegan'])

# Display the combined features for the first few rows
print("\nCombined features head:\n")
print(df[['cheese', 'features']].head())
print("\n")







# Cosine Similarity: This method measures the similarity between two items based on their attributes (for example, flavor, milk type).
# Uses TF-IDF Vectorizer to convert the combined text features into numerical values, and cosine similarity to measure how similar the cheeses are to the user's preferences.

# Initialize the TF-IDF Vectorizer
tfidf = TfidfVectorizer()

# Fit and transform the 'features' column into a matrix of numerical values
tfidf_matrix = tfidf.fit_transform(df['features'])

# Calculate the cosine similarity between all cheeses
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Function to recommend new cheeses based on the name of a preferred cheese
def recommend_cheese(user_input_cheese, cosine_sim=cosine_sim):
    
    # Get the index of the cheese that matches the user_input_cheese
    idx = df.index[df['cheese'] == user_input_cheese].tolist()[0]
    
    # Get the pairwise similarity scores for all cheeses with the input cheese
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort the cheeses by similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get the indices of the most similar cheeses
    sim_indices = [i[0] for i in sim_scores[1:6]]  # Top 5 similar cheeses
    
    # Return the top 5 most similar cheeses
    return df['cheese'].iloc[sim_indices]



def recommend_based_on_preferences(milk_pref, country_pref, region_pref, family_pref, type_pref, texture_pref, rind_pref, flavor_pref, aroma_pref, vegetarian_pref, vegan_pref):
    # Initialize an empty list to store the attributes that are not 'Any'
    user_pref_list = []
    
    # Add attributes to the list only if they are not 'Any'
    if milk_pref != 'Any':
        user_pref_list.append(milk_pref)
    if country_pref != 'Any':
        user_pref_list.append(country_pref)
    if region_pref != 'Any':
        user_pref_list.append(region_pref)
    if family_pref != 'Any':
        user_pref_list.append(family_pref)
    if type_pref != 'Any':
        user_pref_list.append(type_pref)
    if texture_pref != 'Any':
        user_pref_list.append(texture_pref)
    if rind_pref != 'Any':
        user_pref_list.append(rind_pref)
    if flavor_pref != 'Any':
        user_pref_list.append(flavor_pref)
    if aroma_pref != 'Any':
        user_pref_list.append(aroma_pref)
    if vegetarian_pref != 'Any':
        user_pref_list.append(vegetarian_pref)
    if vegan_pref != 'Any':
        user_pref_list.append(vegan_pref)
    
    # Combine all non-'Any' preferences into a single string for the user
    user_preferences = ' '.join(user_pref_list)
    
    # Transform the user's preferences into a tf-idf matrix
    user_tfidf = tfidf.transform([user_preferences])
    
    # Calculate the cosine similarity between the user's preferences and all cheeses
    sim_scores = cosine_similarity(user_tfidf, tfidf_matrix)
    
    # Sort the cheeses by similarity scores
    sim_scores = list(enumerate(sim_scores[0]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get the indices of the most similar cheeses
    sim_indices = [i[0] for i in sim_scores[:5]]  # Top 5 recommendations
    
    # Return the top 5 most similar cheeses
    return df['cheese'].iloc[sim_indices]





# Example usage: recommending cheeses similar to 'Abbaye de Belloc'
preferred_cheese = 'Abbaye de Belloc'

print("\nRecommend cheese similar to another cheese:\n")
print(recommend_cheese(preferred_cheese))
print("\n")



# Example: User inputs their preferences
milk_input = 'cow'
country_input = 'Any'  # The user has no preference for country
region_input = 'Any'   # No region preference
family_input = 'Blue'
type_input = 'semi-soft'
texture_input = 'creamy'
rind_input = 'Any'     # No preference for rind
flavor_input = 'sweet'
aroma_input = 'buttery'
vegetarian_input = 'TRUE'
vegan_input = 'Any'    # No preference for vegan

# Get recommendations based on the inputs
recommended_cheeses = recommend_based_on_preferences(milk_input, country_input, region_input, family_input, type_input, texture_input, rind_input, flavor_input, aroma_input, vegetarian_input, vegan_input)
print("\nRecommended cheeses based preferences:\n")
print(recommended_cheeses)
print('\n')








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


#Things to Note:
#The program is counting lists of attributes as a single attribute (e.g., 'semi-soft, artisan, brined' is a single "type" attribute that likely isn't shared by any other cheese, but each individual attribute might.).
    #Can be fixed with the following after all "df['milk'] = df['milk'].fillna('')" statements towards start of code.
        ##Split multi-attribute fields into individual components
        #df['milk'] = df['milk'].apply(lambda x: ' '.join(x.split(',')))
        #df['country'] = df['country'].apply(lambda x: ' '.join(x.split(',')))
        #df['type'] = df['type'].apply(lambda x: ' '.join(x.split(',')))
        #df['texture'] = df['texture'].apply(lambda x: ' '.join(x.split(',')))
        #df['flavor'] = df['flavor'].apply(lambda x: ' '.join(x.split(',')))
        #df['aroma'] = df['aroma'].apply(lambda x: ' '.join(x.split(',')))
        #...

        #However, this may make cheeses with more attributes rarer to be recommended. This is because there will be even more attributes that will make it more dissimilar from every other cheese. (maybe)
            #e.g.   User preference: "brined"
            #       Cheese 1: "artisan, brined" (2 matching words)
            #       Cheese 2: "semi-soft, artisan, brined" (3 words, only 2 match)
            #Cheese 1 might score slightly higher than Cheese 2, even though Cheese 2 should still be a good match.

            #This can be band-aid resolved by boosting match scores. This ensures that cheeses with a higher number of matching attributes are rewarded.
                #If a cheese has many attributes but matches the user’s preferences on key attributes (like "brined"), it will still receive a boost and rank higher.

#Producer value can come back with the "Any" option, since most people would likely pick any.

#Give program good UI

#Dropdown boxes? (or at least some kind of list the user can select from) that includes all values displayed from cheeses.csv file
    #What about multi-valued attributes? (discussed in point above)
    #Program doesn't necessarily discriminate between attributes. "cow" under "milk" would have no difference than if "cow" were to somehow be under "color"

#Make program output the reasons it picked the similar cheeses (what attributes did it share with your preferences?)


