const fs = require('fs');
const path = require('path');

const filename = "UserInfo.txt";

// User class
class User {
    constructor(username, password) {
        this.username = username;
        this.password = password;
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
            const [username, password] = line.split(',');
            users.push(new User(username, password));
        });
        console.log("User data loaded from file.");
    } catch (err) {
        console.error("Error loading user data:", err.message);
    }
}

// Check if a username is already taken
function isUsernameTaken(username) {
    return users.some(user => user.username === username);
}

// Create a new user
function createUser(username, password) {
    if (isUsernameTaken(username)) {
        console.log("Username already exists. Please choose a different username.");
        return;
    }
    const newUser = new User(username, password);
    users.push(newUser);

    // Append user to file
    try {
        const filePath = path.resolve(__dirname, filename);
        fs.appendFileSync(filePath, `${username},${password}\n`);
        console.log(`User '${username}' created successfully!`);
    } catch (err) {
        console.error("Error saving user data:", err.message);
    }
}

// Login user by checking credentials
function login(username, password) {
    const user = users.find(user => user.username === username && user.password === password);
    if (user) {
        console.log(`Welcome back, ${username}!`);
        return true;
    }
    console.log("Invalid username or password.");
    return false;
}

// Main function
function main() {
    loadUsersFromFile();

    // Test creating users
    createUser("Alice", "password123");
    createUser("Bob", "securepassword");
    createUser("Alice", "newpassword"); // Duplicate username

    // Test logging in
    login("Alice", "password123"); // Valid login
    login("Alice", "wrongpassword"); // Invalid login
    login("Charlie", "doesnotexist"); // Username doesn't exist

    // Print all users for verification
    console.log("\nAll Users:");
    users.forEach(user => console.log(`Username: ${user.username}, Password: ${user.password}`));
}

// Run the program
main();
