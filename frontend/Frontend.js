// Wait for the form submission to capture the user's input
document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent form from reloading the page

    // Capture the user's input
    const url = document.getElementById("neo4jUrl").value;
    const username = document.getElementById("neo4jUsername").value;
    const password = document.getElementById("neo4jPassword").value;

    // Hide the login form
    document.querySelector('.login-container').style.display = 'none';
    
    // Show the graph container
    document.getElementById('viz').style.display = 'block';

    // Render the graph with the provided credentials
    renderGraph(url, username, password);
});

// Function to render the Neo4j graph using Neovis.js
function renderGraph(url, username, password) {
    const config = {
        container_id: "viz",  // The container ID in HTML
        server_url: url,  // Neo4j URL provided by user
        server_user: username,  // Neo4j username provided by user
        server_password: password,  // Neo4j password provided by user
        labels: {
            "Person": {
                "caption": "name",
                "size": "pagerank",
                "community": "community"
            }
        },
        relationships: {
            "KNOWS": {
                "caption": true,
                "thickness": "weight"
            }
        },
        arrows: true,
    };

    // Create and render the visualization
    const viz = new NeoVis.default(config);
    viz.render();
}
