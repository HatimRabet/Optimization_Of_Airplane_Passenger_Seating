document.addEventListener('DOMContentLoaded', () => {
    createSeatMap();
    animateSeats();
    const submitButton = document.getElementById('submit-seats');
    submitButton.addEventListener('click', submitSelectedSeats);
});

let cnt = 0;
let selected_seats = []
function submitSelectedSeats() {
    fetch('/update_tabu', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            selected_seats: selected_seats
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        if (data.message === 'Tabu list updated successfully') {
            window.location.href = '/';
        }
    });
}


function createSeatMap() {
    const plane = document.getElementById('plane');
    const numRows = 29;
    const numCols = 7;

    for (let i = 0; i < numRows; i++) {
        const row = document.createElement('div');

        for (let j = 0; j < numCols; j++) {
            const seat = document.createElement('div');
            const seatLabel =  (i + 1) + String.fromCharCode(65 + j);
            seat.classList.add('seat');
            seat.dataset.label = seatLabel;
            seat.innerHTML = seatLabel;
            row.appendChild(seat);
        }

        plane.appendChild(row);
    }
}

function animateSeats() {
    const seats = document.querySelectorAll('.seat');
    console.log(takenSeats)
    seats.forEach(seat => {
        //console.log(String(seat.dataset.label))
        //console.log(String(seat.dataset.label))
        //console.log(takenSeats.includes(String(seat.dataset.label)))
        if (takenSeats.includes(String(seat.dataset.label))) {
            //console.log('here')
            seat.classList.add('taken');
        } else {
            seat.classList.add('available');
            seat.addEventListener('click', () => {
                handleSeatSelection(seat);
                });
                }
                });
            
                }
                
                function handleSeatSelection(seat) {
                if (seat.classList.contains('selected')) {
                seat.classList.remove('selected');
                seat.classList.add('available');
                selected_seats = selected_seats.filter(item => item !== seat.dataset.label)
                cnt -=1
                // Perform any additional actions required when a seat is deselected, e.g., update the selected seats list
                } else {
                    if(cnt==0){
                seat.classList.remove('available');
                seat.classList.add('selected');
                selected_seats.push(seat.dataset.label);
                cnt+=1
                }
                
                // Perform any additional actions required when a seat is selected, e.g., update the selected seats list
                }
                }