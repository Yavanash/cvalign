// Get elements
  const responseBox = document.getElementById('response');
  const uploadBtn = document.getElementById('uploadBtn');
  const clearBtn = document.getElementById('clearBtn');
  const fileInput = document.getElementById('pdfFile');
  const jobInput = document.getElementById('job_desc');
  const unselectBtn = document.getElementById('unselectBtn');

  // Clear function
  clearBtn.addEventListener('click', function() {
      responseBox.textContent = 'Response cleared.';
      responseBox.className = 'response-box';
  });
  

  unselectBtn.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    fileInput.value = '';

    responseBox.textContent = 'File unselected. Ready to upload a new file.';
    responseBox.className = 'response-box';
    
  });

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
          responseBox.className = 'response-box success';
          
      } catch (err) {
          console.error("Fetch error:", err);
          responseBox.textContent = 'Upload failed: ' + err.message;
          responseBox.className = 'response-box error';
      } finally {
          uploadBtn.disabled = false;
          uploadBtn.textContent = 'Upload PDF';
      }
  });