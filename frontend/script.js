// DOM Elements
const uploadBtn = document.getElementById('uploadBtn');
const clearBtn = document.getElementById('clearBtn');
const unselectBtn = document.getElementById('unselectBtn');
const fileInput = document.getElementById('pdfFile');
const jobDescInput = document.getElementById('job_desc');
const CandidateInput = document.getElementById('candidate')
const responseBox = document.getElementById('response');
const leaderboardList = document.getElementById('leaderboardList');
const refreshBtn = document.getElementById('refreshLeaderboard');

let leaderboardData = [];

// Upload function
uploadBtn.addEventListener('click', async function(event) {
    
    // Prevent any default behavior
    event?.preventDefault();
    
    // Check file selection
    if (!fileInput.files || !fileInput.files[0]) {
        responseBox.textContent = 'Please select a PDF file first.';
        responseBox.className = 'response-box error';
        return;
    }
    if (!jobInput.value) {
        responseBox.textContent = 'Job description cannot be blank';
        responseBox.className = 'response-box error';
        return;
    }
    
    const selectedFile = fileInput.files[0];
    // Disable button
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';
    
    // Show upload start
    responseBox.textContent = `Starting upload of: ${selectedFile.name}\nSize: ${selectedFile.size} bytes\nType: ${selectedFile.type}`;
    responseBox.className = 'response-box';
    
    // Create FormData
    const formData = new FormData();
    formData.append('pdf', selectedFile);
    formData.append('job_desc', jobInput.value);
    formData.append('candidate_name', CandidateInput.value);
    
    try {
        const res = await fetch('http://localhost:8080/v1/upload', {
            method: 'POST',
            body: formData,
        });
        if (!res.ok) {
            const errText = await res.text();
            responseBox.textContent = `Server error: ${res.status}\n${errText}`;
            responseBox.className = 'response-box error';
            return;
        }
        
        const data = await res.json();
        // Set response with extra debug info
        const fullResponse = {
            serverResponse: data,
        };
        responseBox.textContent = JSON.stringify(fullResponse, null, 2);
        leaderboardData.push({
            username: CandidateInput.values,
            score: fullResponse.serverResponse.relevance_score
        })
        responseBox.className = 'response-box success';
        renderLeaderboard()
    } catch (err) {
        console.error("Fetch error:", err);
        responseBox.textContent = 'Upload failed: ' + err.message;
        responseBox.className = 'response-box error';
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload PDF';
    }
});

// Clear response
clearBtn.addEventListener('click', function(e) {
    e.preventDefault();
    responseBox.textContent = 'Response cleared. Ready to upload.';
    responseBox.className = 'response-box';
});

// Unselect file
unselectBtn.addEventListener('click', function(e) {
    e.preventDefault();
    fileInput.value = '';
    responseBox.textContent = 'File unselected. Ready to upload a new file.';
    responseBox.className = 'response-box';
});

// Leaderboard functions
function renderLeaderboard() {
    // Sort by score descending
    const sortedData = [...leaderboardData].sort((a, b) => b.score - a.score);
    
    leaderboardList.innerHTML = '';
    
    if (sortedData.length === 0) {
        leaderboardList.innerHTML = '<li class="empty-state">No submissions yet</li>';
        return;
    }
    
    sortedData.forEach((user, index) => {
        const rank = index + 1;
        const listItem = document.createElement('li');
        listItem.className = `leaderboard-item${rank <= 3 ? ` rank-${rank}` : ''}`;
        
        listItem.innerHTML = `
            <div class="rank">#${rank}</div>
            <div class="user-info">
                <div class="username">${user.username}</div>
                <div class="job-title">${user.jobTitle}</div>
            </div>
            <div class="score">${user.score}%</div>
        `;
        
        leaderboardList.appendChild(listItem);
    });
}

function addToLeaderboard(username, jobTitle, score) {
    leaderboardData.push({ username, jobTitle, score });
    renderLeaderboard();
}

// Refresh leaderboard
refreshBtn.addEventListener('click', function() {
    // In a real app, you'd fetch fresh data from your backend
    // For demo, we'll just re-render
    renderLeaderboard();
    
    // Add a small animation effect
    refreshBtn.style.transform = 'rotate(360deg)';
    setTimeout(() => {
        refreshBtn.style.transform = 'rotate(0deg)';
    }, 500);
});

async function fetchLeaderboardFromServer() {
    try {
        const res = await fetch('http://localhost:8080/v1/leaderboard');
        if (!res.ok) {
            console.error('Failed to fetch leaderboard:', res.statusText);
            return;
        }

        const json = await res.json();

        if (!Array.isArray(json.data)) {
            console.error('Unexpected response format:', json);
            return;
        }

        leaderboardData = json.data.map(item => ({
            username: item.name || 'Unknown',
            score: item.score || 0
        }));

        renderLeaderboard();
    } catch (err) {
        console.error('Error fetching leaderboard:', err);
    }
}

// Initialize leaderboard
fetchLeaderboardFromServer();
