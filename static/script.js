document.getElementById('create-object-form').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent default form submission

    const name = document.getElementById('name').value;
    const description = document.getElementById('description').value;
    const attributesInput = document.getElementById('attributes').value;
    const responseMessageDiv = document.getElementById('response-message');
    responseMessageDiv.textContent = ''; // Clear previous messages
    responseMessageDiv.className = ''; // Clear previous classes

    let attributes = {};
    try {
        // Only parse if the input is not empty
        if (attributesInput.trim() !== '') {
            attributes = JSON.parse(attributesInput);
        }
        // Basic validation: Ensure it's an object if not empty
        if (attributesInput.trim() !== '' && (typeof attributes !== 'object' || attributes === null || Array.isArray(attributes))) {
             throw new Error("Attributes must be a valid JSON object (e.g., {\"key\": \"value\"}).");
        }
    } catch (error) {
        responseMessageDiv.textContent = `Error parsing attributes JSON: ${error.message}`;
        responseMessageDiv.classList.add('error');
        return; // Stop submission if JSON is invalid
    }

    const objectData = {
        name: name,
        description: description || null, // Send null if description is empty
        attributes: attributes
    };

    try {
        const response = await fetch('/api/v1/objects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(objectData),
        });

        const result = await response.json();

        if (response.ok) {
            responseMessageDiv.textContent = `Object created successfully! ID: ${result.id}`;
            responseMessageDiv.classList.add('success');
            // Optionally clear the form
            // event.target.reset();
        } else {
            // Handle potential FastAPI validation errors or other server errors
            let errorMessage = `Error creating object: ${response.statusText}`;
            if (result.detail) {
                 if (Array.isArray(result.detail)) {
                    errorMessage += " - " + result.detail.map(err => `${err.loc.join('.')} - ${err.msg}`).join(', ');
                 } else {
                    errorMessage += ` - ${result.detail}`;
                 }
            }
            responseMessageDiv.textContent = errorMessage;
            responseMessageDiv.classList.add('error');
        }
    } catch (error) {
        console.error('Network or other error:', error);
        responseMessageDiv.textContent = `Network error or other issue: ${error.message}`;
        responseMessageDiv.classList.add('error');
    }
});