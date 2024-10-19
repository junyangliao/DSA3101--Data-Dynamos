// Registration Logic
document.getElementById("registerForm")?.addEventListener("submit", function(event) {
    event.preventDefault();
    const newUsername = document.getElementById("newUsername").value;
    const newPassword = document.getElementById("newPassword").value;

    // Save credentials in localStorage (for demo purposes)
    localStorage.setItem("username", newUsername);
    localStorage.setItem("password", newPassword);

    // Redirect to login page
    alert("Registration successful! Redirecting to login page.");
    window.location.href = "index.html";
});

// Login Logic
document.getElementById("loginForm")?.addEventListener("submit", function(event) {
    event.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // Check credentials
    const savedUsername = localStorage.getItem("username");
    const savedPassword = localStorage.getItem("password");

    if (username === savedUsername && password === savedPassword) {
        localStorage.setItem("isLoggedIn", true);  // Store login status
        window.location.href = "home.html";  // Redirect to home page
    } else {
        alert("Invalid credentials, try again!");
    }
});


// Logout Logic
document.getElementById("logout")?.addEventListener("click", function() {
    localStorage.removeItem("isLoggedIn");
    window.location.href = "index.html";
});

// Display Username on Home Page
if (localStorage.getItem("isLoggedIn")) {
    document.getElementById("user").innerText = localStorage.getItem("username");
} else if (document.body.contains(document.getElementById("user"))) {
    window.location.href = "index.html"; // Redirect to login if not logged in
}

// Query Page Logic - Neo4j Visualization
document.getElementById("runQuery")?.addEventListener("click", function() {
    const cypherQuery = document.getElementById("cypherQuery").value;
    
    // Define Neo4j connection details
    const config = {
        container_id: "viz",
        server_url: "neo4j+s://c26a60a3.databases.neo4j.io",
        server_user: "neo4j",
        server_password: "hsH-EM_e9LBZS3gdpUdMMakjrxytC839zvGQmpmWpU8",
    labels: {
        "Person": { "caption": "name" }
    },
    initial_cypher: cypherQuery  // User-inputted Cypher query
    };

    // Render Neo4j graph visualization
    const viz = new NeoVis.default(config);
    viz.render();
});
document.getElementById("job-search-form").addEventListener("submit", function(event) {
    event.preventDefault();

    const jobTitle = document.getElementById("job-title").value;
    const location = document.getElementById("location").value;
    const industry = document.getElementById("industry").value;

    // Example: Send the data to the backend API to query Neo4j
    const data = {
        jobTitle: jobTitle,
        location: location,
        industry: industry
    };

  // Assuming you have an HTML form with the ID 'recommendationForm'
document.getElementById('recommendationForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Get user input
    const jobTitle = document.getElementById('jobTitle').value;

    // Send the input to the backend
    fetch('/get-recommendations', { // Endpoint to handle the request
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ jobTitle: jobTitle }) // Sending user input as JSON
    })
    .then(response => response.json()) // Parse the JSON response
    .then(data => {
        // Handle the data received from the backend
        displayRecommendations(data); // Call a function to display recommendations
    })
    .catch(error => {
        console.error('Error:', error); // Handle any errors
    });
});

// Function to display the recommendations in the HTML
function displayRecommendations(data) {
    // Assuming you have an HTML element to display results
    const resultDiv = document.getElementById('recommendationResults');
    resultDiv.innerHTML = ''; // Clear previous results

    if (data.length > 0) {
        data.forEach(item => {
            const div = document.createElement('div');
            div.innerHTML = `<strong>${item.title}</strong>: ${item.details}`; // Customize based on your data structure
            resultDiv.appendChild(div);
        });
    } else {
        resultDiv.innerHTML = '<p>No recommendations found.</p>';
    }
}
});