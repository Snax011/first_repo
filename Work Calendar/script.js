const calendar = document.getElementById('calendar');
const monthDisplay = document.getElementById('monthDisplay');

// 1. Instead of fetching a file, we put your Excel data here for now
const myEvents = [
    { date: '2026-01-28', type: 'doordash', info: '5pm-9pm Shift' },
    { date: '2026-01-29', type: 'job', info: 'Apply to 5 jobs' },
    { date: '2026-01-30', type: 'interview', info: 'Tech Interview' }
];

function renderCalendar() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    
    monthDisplay.innerText = now.toLocaleString('default', { month: 'long', year: 'numeric' });

    // Clear previous calendar content
    calendar.innerHTML = '';

    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    for (let i = 1; i <= daysInMonth; i++) {
        const dayDiv = document.createElement('div');
        dayDiv.classList.add('day-card');
        dayDiv.innerHTML = `<strong>${i}</strong>`;
        
        // Format date to match: YYYY-MM-DD
        const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
        
        // Look for events
        const todaysEvents = myEvents.filter(e => e.date === dateString);
        
        todaysEvents.forEach(e => {
            const eventEl = document.createElement('div');
            eventEl.classList.add('event', e.type);
            eventEl.innerText = e.info;
            dayDiv.appendChild(eventEl);
        });

        calendar.appendChild(dayDiv);
    }
}

renderCalendar();
