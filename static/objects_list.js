document.addEventListener('DOMContentLoaded', async () => {
    const tableBody = document.querySelector('#objects-table tbody');
    const loadingMessage = document.getElementById('loading-message');
    const errorMessage = document.getElementById('error-message');

    try {
        loadingMessage.style.display = 'block'; // Show loading message
        errorMessage.textContent = ''; // Clear previous errors

        const response = await fetch('/api/v1/objects');
        const objects = await response.json();

        if (!response.ok) {
            // Handle API errors (e.g., 4xx, 5xx)
            let errorText = `Error fetching objects: ${response.statusText}`;
             if (objects.detail) {
                 if (Array.isArray(objects.detail)) {
                    errorText += " - " + objects.detail.map(err => `${err.loc.join('.')} - ${err.msg}`).join(', ');
                 } else {
                    errorText += ` - ${objects.detail}`;
                 }
            }
            throw new Error(errorText);
        }

        tableBody.innerHTML = ''; // Clear existing rows (if any)

        if (objects.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7">No objects found.</td></tr>'; // Updated colspan
        } else {
            objects.forEach(obj => {
                const row = tableBody.insertRow();

                // Format dates nicely (optional)
                const createdAt = new Date(obj.created_at).toLocaleString();
                const updatedAt = new Date(obj.updated_at).toLocaleString();

                row.insertCell().textContent = obj.id;
                row.insertCell().textContent = obj.name;
                row.insertCell().textContent = obj.description || '-'; // Display '-' if null/empty
                // Display attributes as formatted JSON
                const attributesCell = row.insertCell();
                const pre = document.createElement('pre');
                pre.textContent = JSON.stringify(obj.attributes, null, 2); // Pretty print JSON
                attributesCell.appendChild(pre);

                row.insertCell().textContent = createdAt;
                row.insertCell().textContent = updatedAt;

                // Add Actions cell with Edit button
                const actionsCell = row.insertCell();
                const editButton = document.createElement('a');
                editButton.href = `/object/edit/${obj.id}`;
                editButton.textContent = 'Edit';
                editButton.style.color = '#7af'; // Style link for visibility
                editButton.style.textDecoration = 'none';
                editButton.style.padding = '5px 10px';
                editButton.style.border = '1px solid #555';
                editButton.style.borderRadius = '4px';
                editButton.style.backgroundColor = '#333';
                editButton.onmouseover = () => { editButton.style.backgroundColor = '#444'; };
                editButton.onmouseout = () => { editButton.style.backgroundColor = '#333'; };
                actionsCell.appendChild(editButton);
            });
        }

    } catch (error) {
        console.error('Failed to load objects:', error);
        errorMessage.textContent = `Failed to load objects: ${error.message}`;
        tableBody.innerHTML = '<tr><td colspan="7">Error loading data.</td></tr>'; // Updated colspan
    } finally {
        loadingMessage.style.display = 'none'; // Hide loading message
    }
});