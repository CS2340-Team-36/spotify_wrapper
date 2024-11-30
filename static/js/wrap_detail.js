document.addEventListener("DOMContentLoaded", function () {
    const slides = document.querySelectorAll('.slide');
    let currentSlide = parseInt(sessionStorage.getItem('currentSlide')) || 0;
    let score = parseInt(sessionStorage.getItem('score')) || 0; // Retrieve score from sessionStorage or default to 0
    const timerElement = document.getElementById('timer');
    const timerBar = document.getElementById('timer-bar');
    const scoreElement = document.getElementById('score');
    const form = document.getElementById('game-form');
    let timer;

    // Initialize the score
    if (scoreElement) {
        scoreElement.textContent = score;
    }

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.toggle('active', i === index);

            // If the game slide is active, start the timer
            if (slide.querySelector('.game-info') && i === index) {
                resetTimer();
            } else {
                clearInterval(timer); // Stop the timer for non-game slides
                resetTimerBar(); // Reset timer bar for non-game slides
            }
        });

        sessionStorage.setItem('currentSlide', index); // Save the current slide index
    }

    // Timer Countdown Logic
    function startTimer(duration) {
        let timeLeft = duration;
        timerElement.textContent = timeLeft;

        // Initialize the timer bar
        timerBar.style.width = "100%";
        timerBar.style.backgroundColor = "green";

        timer = setInterval(() => {
            timeLeft--;
            timerElement.textContent = timeLeft;

            // Update the timer bar width and color
            const widthPercentage = (timeLeft / duration) * 100;
            timerBar.style.width = `${widthPercentage}%`;
            if (timeLeft <= 10) {
                timerBar.style.backgroundColor = "red"; // Change to red when 10 seconds remain
            }

            if (timeLeft <= 0) {
                clearInterval(timer);
                handleGameTimeout(); // Handle timeout scenario
            }
        }, 1000);
    }

    function resetTimer() {
        clearInterval(timer);
        startTimer(30); // Start a new 30-second timer
    }

    function resetTimerBar() {
        timerBar.style.width = "100%"; // Reset the bar's width
        timerBar.style.backgroundColor = "green"; // Reset the bar's color
    }

    function handleGameTimeout() {
        // If the user doesn't answer in time, proceed to the next question
        alert("Time's up! Moving to the next question.");
        form.submit(); // Submit the form to load the next question
    }

    // Update score
    function updateScore(points) {
        score += points;
        if (scoreElement) scoreElement.textContent = score;
        sessionStorage.setItem('score', score); // Save score to sessionStorage
    }

    // Initialize the correct slide and timer
    showSlide(currentSlide);

    // Handle form submission
    if (form) {
        form.addEventListener('submit', function (event) {
            // Stop the timer
            clearInterval(timer);

            // Check the result from the server
            const resultElement = document.getElementById('result');
            if (resultElement && resultElement.textContent.includes('Correct')) {
                updateScore(10); // Add 10 points for a correct answer
            } else {
                updateScore(-5); // Deduct points for a wrong answer (optional)
            }

            // Allow the form to submit normally (reloads the page)
        });
    }

    // Navigation Buttons
    document.getElementById('next').addEventListener('click', () => {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    });

    document.getElementById('prev').addEventListener('click', () => {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(currentSlide);
    });
});
