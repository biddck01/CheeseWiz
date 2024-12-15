const fs = require('fs');
const path = require('path');

const filename = "UserInfo.txt";

// User class
class User {
    constructor(username, password, history = []) {
        this.username = username;
        this.password = password;
        this.history = history;
    }
}

// In-memory users list
let users = [];

// Load users from the file into memory
function loadUsersFromFile() {
    try {
        const filePath = path.resolve(__dirname, filename);
        if (!fs.existsSync(filePath)) {
            console.log("No user data file found. Starting fresh.");
            return;
        }
        const data = fs.readFileSync(filePath, 'utf-8');
        const lines = data.split('\n').filter(line => line.trim() !== '');
        lines.forEach(line => {
            const [username, password, historyString] = line.split(',');
            const history = historyString ? historyString.split('|') : [];
            users.push(new User(username, password, history));
        });
        console.log("User data loaded from file.");
    } catch (err) {
        console.error("Error loading user data:", err.message);
    }
}

// Login user by checking credentials
function login(username, password) {
    const user = users.find(user => user.username === username && user.password === password);
    if (user) {
        console.log(`Welcome back, ${username}!`);
        return user.username; // Return the username for further operations
    }
    console.log("Invalid username or password.");
    return null; // Return null if login fails
}

// Save information (e.g., search history) for a user
function saveInformation(username, info) {
    const user = users.find(user => user.username === username);
    if (!user) {
        console.log(`User '${username}' not found.`);
        return null;
    }

    // Append the info to the user's history
    user.history.push(info);

    // Update the file
    try {
        const filePath = path.resolve(__dirname, filename);
        const updatedData = users.map(user => {
            const historyString = user.history.join('|'); // Convert history to string
            return `${user.username},${user.password},${historyString}`;
        }).join('\n');
        fs.writeFileSync(filePath, updatedData, 'utf-8');
        console.log(`Information '${info}' saved for user '${username}'.`);
    } catch (err) {
        console.error("Error updating user information:", err.message);
    }
}

// Load and display a user's history
function loadHistory(username) {
    const user = users.find(user => user.username === username);
    if (!user) {
        console.log(`User '${username}' not found.`);
        return;
    }

    console.log(`History for '${username}':`);
    if (user.history.length === 0) {
        console.log("No history available.");
    } 
    else {
        user.history.forEach((item, index) => {
            console.log(`${index + 1}. ${item}`);
        });
    }
}

// Main function
function main() {
    loadUsersFromFile();

    const username = login("Alice", "password123");
    if (username) { 
        saveInformation(username, "search history");
        loadHistory(username);
    } 
    else {
        console.log("Login failed. Cannot save or load information.");
    }
}

main();
