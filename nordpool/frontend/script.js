// API endpoint
const API_BASE_URL = 'http://localhost:8000';

// DOM elements
const dataSource = document.getElementById('dataSource');
const currentMonth = document.getElementById('currentMonth');
const prevMonth = document.getElementById('prevMonth');
const nextMonth = document.getElementById('nextMonth');
const calendarDays = document.getElementById('calendarDays');
const selectedDate = document.getElementById('selectedDate');
const pricesTableBody = document.getElementById('pricesTableBody');
const minPrice = document.getElementById('minPrice');
const maxPrice = document.getElementById('maxPrice');
const avgPrice = document.getElementById('avgPrice');

// State variables
let currentDate = new Date();
let displayedMonth = currentDate.getMonth();
let displayedYear = currentDate.getFullYear();
let availableDates = [];

// Initialize the application
async function init() {
    try {
        // Fetch available dates
        const response = await fetch(`${API_BASE_URL}/prices/available-dates`);
        const data = await response.json();
        availableDates = data.dates || [];
        
        // Generate calendar
        generateCalendar();
        
        // Load prices for current date
        loadPrices(formatDate(currentDate));
    } catch (error) {
        console.error('Error initializing application:', error);
    }
}

// Format date to YYYY-MM-DD
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Parse date string to Date object
function parseDate(dateString) {
    const [year, month, day] = dateString.split('-').map(Number);
    return new Date(year, month - 1, day);
}

// Generate calendar
function generateCalendar() {
    // Update month display
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    currentMonth.textContent = `${monthNames[displayedMonth]} ${displayedYear}`;
    
    // Clear calendar days
    calendarDays.innerHTML = '';
    
    // Get first day of month and number of days
    const firstDay = new Date(displayedYear, displayedMonth, 1).getDay();
    const daysInMonth = new Date(displayedYear, displayedMonth + 1, 0).getDate();
    
    // Adjust first day (0 = Sunday, 1 = Monday, etc.)
    const adjustedFirstDay = firstDay === 0 ? 6 : firstDay - 1;
    
    // Add empty cells for days before first day of month
    for (let i = 0; i < adjustedFirstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day empty';
        calendarDays.appendChild(emptyDay);
    }
    
    // Add days of month
    for (let i = 1; i <= daysInMonth; i++) {
        const day = document.createElement('div');
        day.className = 'calendar-day';
        day.textContent = i;
        
        // Check if date is available
        const dateString = `${displayedYear}-${String(displayedMonth + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
        const isAvailable = availableDates.includes(dateString);
        
        // Check if date is current date
        const isCurrentDate = currentDate.getDate() === i && 
                             currentDate.getMonth() === displayedMonth && 
                             currentDate.getFullYear() === displayedYear;
        
        // Check if date is selected date
        const selectedDateStr = selectedDate.textContent;
        const isSelectedDate = selectedDateStr === dateString;
        
        if (isCurrentDate) {
            day.classList.add('current');
        }
        
        if (isSelectedDate) {
            day.classList.add('selected');
        }
        
        if (isAvailable) {
            day.addEventListener('click', () => {
                // Remove selected class from all days
                document.querySelectorAll('.calendar-day.selected').forEach(el => {
                    el.classList.remove('selected');
                });
                
                // Add selected class to clicked day
                day.classList.add('selected');
                
                // Load prices for selected date
                loadPrices(dateString);
            });
        } else {
            day.style.opacity = '0.5';
        }
        
        calendarDays.appendChild(day);
    }
}

// Load prices for a specific date
async function loadPrices(date) {
    try {
        // Update selected date display
        selectedDate.textContent = date;
        
        // Show loading state
        pricesTableBody.innerHTML = `
            <tr>
                <td colspan="3" style="text-align: center; padding: 20px;">
                    Loading prices...
                </td>
            </tr>
        `;
        
        // Fetch prices
        const response = await fetch(`${API_BASE_URL}/prices/date/${date}`);
        
        if (!response.ok) {
            throw new Error(`Failed to load prices for ${date}`);
        }
        
        const data = await response.json();
        
        // Update data source
        dataSource.textContent = `Data source: ${data.source}`;
        
        // Update price summary
        minPrice.textContent = `${data.min_price.toFixed(2)} EUR/MWh`;
        maxPrice.textContent = `${data.max_price.toFixed(2)} EUR/MWh`;
        avgPrice.textContent = `${data.avg_price.toFixed(2)} EUR/MWh`;
        
        // Generate price table
        pricesTableBody.innerHTML = '';
        
        data.prices.forEach(price => {
            const row = document.createElement('tr');
            
            // Add color class based on price
            if (price.price <= 50) {
                row.className = 'low-price';
            } else if (price.price >= 70) {
                row.className = 'high-price';
            } else {
                row.className = 'normal-price';
            }
            
            // Format hour display (00:00 - 01:00, etc.)
            const hourStart = String(price.hour).padStart(2, '0');
            const hourEnd = String((price.hour + 1) % 24).padStart(2, '0');
            
            row.innerHTML = `
                <td>${hourStart}:00 - ${hourEnd}:00</td>
                <td>${price.price.toFixed(2)}</td>
                <td>${price.price_kwh.toFixed(2)}</td>
            `;
            
            pricesTableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading prices:', error);
        
        // Show error message
        pricesTableBody.innerHTML = `
            <tr>
                <td colspan="3" style="text-align: center; padding: 20px; color: #e74c3c;">
                    Failed to load prices for ${date}. Please try again later.
                </td>
            </tr>
        `;
    }
}

// Event listeners
prevMonth.addEventListener('click', () => {
    displayedMonth--;
    if (displayedMonth < 0) {
        displayedMonth = 11;
        displayedYear--;
    }
    generateCalendar();
});

nextMonth.addEventListener('click', () => {
    displayedMonth++;
    if (displayedMonth > 11) {
        displayedMonth = 0;
        displayedYear++;
    }
    generateCalendar();
});

// Initialize the application
document.addEventListener('DOMContentLoaded', init);
