document.addEventListener('DOMContentLoaded', () => {
  const resumeInput = document.getElementById('resumeFiles');
  const jobDescInput = document.getElementById('jobDescription');
  
  // Submit button click event handler
  document.getElementById('submitBtn').addEventListener('click', () => {
    const selectedResumes = Array.from(resumeInput.files);
    const selectedJobDesc = jobDescInput.files[0];
    
    // Send selected data to the server
    const formData = new FormData();
    formData.append('jobDescription', selectedJobDesc);
    
    selectedResumes.forEach((file, index) => {
      formData.append(`resume_${index}`, file);
    });
    
    fetch('/rank', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      // Display the sorted resume list
      const resultDiv = document.getElementById('result');
      resultDiv.innerHTML = '';

      const heading = document.createElement('h2');
      heading.textContent = 'Sorted Resume List';
      resultDiv.appendChild(heading);

      const table = document.createElement('table');
      const thead = document.createElement('thead');
      const tbody = document.createElement('tbody');
      const headerRow = document.createElement('tr');

      //  colums
      const nameHeader = document.createElement('th');
      nameHeader.textContent = 'PDF File Name';
      const scoreHeader = document.createElement('th');
      scoreHeader.textContent = 'Score';
      const expHeader = document.createElement('th');
      expHeader.textContent = 'Year Of Exp';

      headerRow.appendChild(nameHeader);
      headerRow.appendChild(scoreHeader);
      headerRow.appendChild(expHeader);
      thead.appendChild(headerRow);
      table.appendChild(thead);

      data.forEach(item => {
        const row = document.createElement('tr');
        const nameCell = document.createElement('td');
        const scoreCell = document.createElement('td');
        const expCell = document.createElement('td');

        nameCell.textContent = item[0];
        scoreCell.textContent = item[1].toFixed(2);
        expCell.textContent = item[2];

        row.appendChild(nameCell);
        row.appendChild(scoreCell);
        row.appendChild(expCell);
        tbody.appendChild(row);
      });

      table.appendChild(tbody);
      resultDiv.appendChild(table);
    })
    .catch(error => console.error('Error:', error));
  });
});
