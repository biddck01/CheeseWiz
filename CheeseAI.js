/*
TO RUN:
Check if NodeJS is installed using "node -v" in the terminal.
    If NodeJS is not installed, install it.

Check if npm is installed using "npm -v" in the terminal.
    If npm is not installed, install it.
    If if node -v gives an error, type the following code into the terminal:
        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
            This allows scripts to run only for the current session.

Enter "npm install csv-parser natural" into the terminal to install the proper libraries.

Run the script using "node CheeseAI.js" in the terminal.

View the .html output file using "./cheese_output.html" in the terminal.
*/ 


const fs = require('fs');
const csv = require('csv-parser');
const natural = require('natural');
const { TfIdf } = natural;



// Global variable for the dataset
let df = [];



// Load dataset
function loadDataset() {
    return new Promise((resolve, reject) => {
        const data = [];
        fs.createReadStream('cheeses.csv')
            .pipe(csv())
            .on('data', (row) => data.push(row))
            .on('end', () => {
                df = data;
                resolve(df);
            })
            .on('error', (err) => reject(err));
    });
}





// Preprocess dataset for feature extraction
function preprocessData() {
    const attributesToProcess = [
        'milk', 'country', 'region', 'family', 'type', 
        'texture', 'rind', 'color', 'flavor', 'aroma'
    ];

    // Fill missing values or 'NA' with 'Unknown' for all attributes
    df.forEach((row) => {
        attributesToProcess.forEach((attr) => {
            if (!row[attr] || row[attr] === 'NA') {
                row[attr] = 'Unknown';
            }
        });

        // Convert boolean columns to string for concatenation
        row['vegetarian'] = String(row['vegetarian']);
        row['vegan'] = String(row['vegan']);

        // Combine important features into a single 'features' column
        row['features'] = attributesToProcess.map(attr => row[attr]).join(' ') + ' ' + row['vegetarian'] + ' ' + row['vegan'];
    });

    return df;
}





// Manually compute cosine similarity between two vectors
function cosineSimilarity(vec1, vec2) {
    const dotProduct = vec1.reduce((acc, val, i) => acc + val * vec2[i], 0);
    const magnitude1 = Math.sqrt(vec1.reduce((acc, val) => acc + val * val, 0));
    const magnitude2 = Math.sqrt(vec2.reduce((acc, val) => acc + val * val, 0));
    
    if (magnitude1 && magnitude2) {
        return dotProduct / (magnitude1 * magnitude2);
    } else {
        return 0;
    }
}

// Initialize TF-IDF vectorizer and compute cosine similarity
function computeCosineSimilarity() {
    const tfidf = new TfIdf();

    // Add documents for the cheeses
    df.forEach((row) => {
        tfidf.addDocument(row['features']);
    });

    // Calculate the cosine similarity matrix between all documents
    const cosineSim = [];
    for (let i = 0; i < df.length; i++) {
        cosineSim[i] = [];
        for (let j = 0; j < df.length; j++) {
            const termsI = tfidf.listTerms(i).map(term => term.tf);
            const termsJ = tfidf.listTerms(j).map(term => term.tf);
            const similarity = cosineSimilarity(termsI, termsJ);
            cosineSim[i].push(similarity);
        }
    }

    return { tfidf, cosineSim };
}





// Recommend cheeses based on user preferences
function recommendBasedOnPreferences(preferences) {
    const userPrefList = Object.keys(preferences).map(key => preferences[key] !== 'N/A' ? preferences[key] : '').filter(Boolean);
    const userPreferences = userPrefList.join(' ');

    // Compute cosine similarity
    const { tfidf, cosineSim } = computeCosineSimilarity();

    // Transform user preferences into TF-IDF space
    const userTfidf = new TfIdf();
    userTfidf.addDocument(userPreferences);
    const userTfidfList = userTfidf.listTerms(0).map(term => term.tf);

    const simScores = [];
    df.forEach((_, idx) => {
        const similarity = cosineSimilarity(userTfidfList, tfidf.listTerms(idx).map(term => term.tf));
        simScores.push({ index: idx, score: similarity });
    });

    // Sort by cosine similarity (descending)
    simScores.sort((a, b) => b.score - a.score);

    // Gather recommendations
    const recommendations = [];
    simScores.forEach(({ index }) => {
        const cheeseName = df[index]['cheese'];
        const sharedAttributes = Object.keys(preferences).map(attr => {
            if (preferences[attr] !== 'N/A' && df[index][attr].includes(preferences[attr])) {
                return `${attr}: ${df[index][attr]}`;
            }
        }).filter(Boolean);

        if (sharedAttributes.length > 0) {
            recommendations.push({ cheeseName, sharedAttributes });
        }
    });

    // Return the top 5 recommendations
    return recommendations.slice(0, 5);
}





// Group cheeses by a specific attribute type
function groupCheesesByAttribute(attribute) {
    if (!df[0].hasOwnProperty(attribute)) {
        return `Attribute '${attribute}' not found in the dataset.`;
    }

    const groupedCheeses = {};

    df.forEach((row) => {
        const attributeValues = row[attribute].split(', ').map(value => value.trim()).filter(value => value !== 'Unknown');
        attributeValues.forEach((value) => {
            if (!groupedCheeses[value]) {
                groupedCheeses[value] = [];
            }
            groupedCheeses[value].push(row['cheese']);
        });
    });

    // Sort the cheeses in each group for better readability
    Object.keys(groupedCheeses).forEach((group) => {
        groupedCheeses[group] = groupedCheeses[group].sort();
    });

    return groupedCheeses;
}





// Write output to HTML file
function writeToHtmlFile(recommendations, groupedCheeses) {
    let htmlContent = `<!DOCTYPE html>
<html>
<head>
    <title>Cheese Recommendations and Groupings</title>
</head>
<body>
    <h1>Cheese Recommendations</h1>
    <ul>
        ${recommendations.map(r => `<li>${r.cheeseName} (${r.sharedAttributes.join(', ')})</li>`).join('')}
    </ul>
    <h1>Cheeses Grouped by Attribute</h1>
    ${Object.entries(groupedCheeses).map(([key, value]) => `
        <h2>${key}</h2>
        <ul>
            ${value.map(cheese => `<li>${cheese}</li>`).join('')}
        </ul>
    `).join('')}
</body>
</html>`;

    fs.writeFileSync('cheese_output.html', htmlContent);
    console.log('Output written to cheese_output.html');
}





// Example usage
(async function () {
    await loadDataset();
    preprocessData();

    const preferences = {
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
    };
    const recommendations = recommendBasedOnPreferences(preferences);

    const attributeType = 'milk'; // Change as needed
    const groupedCheeses = groupCheesesByAttribute(attributeType);

    writeToHtmlFile(recommendations, groupedCheeses);
})();




/*
WHAT NEEDS TO BE DONE:

INITIALIZATION:
Upon Initialization of the first page, Call the following functions:

    load_dataset()
    preprocess_data()

    This will load the dataset into a filereader then process/clean the data.





LOGIN/REGISTER:
Enter a username and password into login screen. 
   If it exists in a file, go to homepage.
   If it doesn't, throw exception.

On sign up page, enter any username or password to create one.
   If username already exists in file, throw exception.
   If not, add username/password to file.





BOTH RECOMMENDING + CLASSIFYING
Ensure all attributes and attribute types are listed as options (case sensitive).
    (Cayla has all options listed out in discord)





RECOMMEND CHEESES:
When a user selects attributes, they should be sent as the parameter to the following function:

    recommendations = recommendBasedOnPreferences(preferences);

        This returns a list of 5 similar cheeses along with the attributes that makes them similar.

        You can follow the parameter and return formatting established by the main method.




GROUP/CLASSIFY CHEESES:
When user selects an attribute type, it should be sent as the parameter to the following function:

    groupedCheeses = groupCheesesByAttribute(attributeType);

        This returns a long string containing all cheeses sorted into groups based on that attribute type.

        You can follow the parameter and return formatting established by the main method.

!!! Currently, the backend code does not support allowing multiple attribute types to be selected at a time.
    To fix this, only allow 1 selection from the website page.
    
    

    
    
CURRENT WRITING TO FILE:
Currently, the program calls to the following function which writes to a new html file called "cheese_output.html"
    function writeToHtmlFile(recommendations, groupedCheeses)





CURRENT BACKEND MAIN FUNCTION
Upon completion of the program, delete the examples used in the main function.
*/