document.addEventListener("DOMContentLoaded", function () {
    const slides = document.querySelectorAll('.slide');
    let currentSlide = parseInt(sessionStorage.getItem('currentSlide')) || 0;
    const timerElement = document.getElementById('timer');
    const timerBar = document.getElementById('timer-bar');
    const form = document.getElementById('game-form');
    let timer;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.toggle('active', i === index);

            // If the game slide is active, start the timer
            if (slide.querySelector('.game-info') && i === index) {
                resetTimer();
            } else {
                clearInterval(timer);
                resetTimerBar();
            }
        });

        sessionStorage.setItem('currentSlide', index);
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
                timerBar.style.backgroundColor = "red";
            }

            if (timeLeft <= 0) {
                clearInterval(timer);
                handleGameTimeout();
            }
        }, 1000);
    }

    function resetTimer() {
        clearInterval(timer);
        startTimer(30);
    }

    function resetTimerBar() {
        timerBar.style.width = "100%";
        timerBar.style.backgroundColor = "green";
    }

    function handleGameTimeout() {
        alert("Time's up! Moving to the next question.");
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'timeout';
        hiddenInput.value = 'true';
        form.appendChild(hiddenInput);
        form.submit();
    }

    // Initialize the correct slide and timer
    showSlide(currentSlide);

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
