// app.js

// Array to store leads
const leads = [];

// Get form and list elements
const leadForm = document.getElementById('leadForm');
const leadsList = document.getElementById('leadsList');

// Function to render leads in the list
const renderLeads = () => {
  leadsList.innerHTML = ''; // Clear current list

  // Use .forEach to iterate over leads and display them
  leads.forEach(({ name, email, phone }, index) => {
    const li = document.createElement('li');
    li.textContent = `${name} - ${email} - ${phone}`;
    leadsList.appendChild(li);
  });
};

// Handle form submission
leadForm.addEventListener('submit', (event) => {
  event.preventDefault();

  // Get input values
  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  const phone = document.getElementById('phone').value.trim();

  // Create lead object
  const lead = { name, email, phone };

  // Add lead to array
  leads.push(lead);

  // Render updated leads list
  renderLeads();

  // Reset form
  leadForm.reset();
});

// Existing code here...

// Show all emails using .map
document.getElementById('showEmails').addEventListener('click', () => {
  const emails = leads.map(lead => lead.email);
  alert('Emails:\n' + emails.join('\n'));
});

// Filter leads with names starting with 'A' using .filter
document.getElementById('filterByNameA').addEventListener('click', () => {
  const filteredLeads = leads.filter(lead => lead.name.toLowerCase().startsWith('a'));
  if (filteredLeads.length === 0) {
    alert('No leads with names starting with "A".');
  } else {
    const names = filteredLeads.map(lead => lead.name);
    alert('Leads with names starting with "A":\n' + names.join('\n'));
  }
});

// Count leads using .reduce
document.getElementById('countLeads').addEventListener('click', () => {
  const count = leads.reduce((acc) => acc + 1, 0);
  alert(`Total leads: ${count}`);
});
