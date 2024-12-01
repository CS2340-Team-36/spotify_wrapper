document.addEventListener("DOMContentLoaded", function () {
    const slides = document.querySelectorAll('.slide');
    let currentSlide = parseInt(sessionStorage.getItem('currentSlide')) || 0;
    const timerElement = document.getElementById('timer');
    const timerBar = document.getElementById('timer-bar');
    const form = document.getElementById('game-form');
    let timer;

    // Genre slide scroll elements
    const genreList = document.getElementById('genre-list');
    const genreItems = document.querySelectorAll('.genre-item');
    const genreItemWidth = genreItems[0].offsetWidth;

    // Top Artists scroll elements
    const topArtistsList = document.getElementById('top-artists-list');
    const topArtistItems = document.querySelectorAll('.artist-item');
    const topArtistItemWidth = topArtistItems[0]?.offsetWidth || 0;

    // Function to reset and animate top artists
    function animateTopArtists() {
        // Remove the 'active' class from all artist items
        topArtistItems.forEach(item => item.classList.remove('active'));

        // Add 'active' class back to artist items with a delay for animation
        topArtistItems.forEach((item, index) => {
            setTimeout(() => {
                item.classList.add('active');
            }, index * 200); // Staggered effect (200ms delay between each item)
        });
    }

    // Auto-scroll genres every 3 seconds
    setInterval(() => {
        genreList.scrollBy({
            left: genreItemWidth,
            behavior: 'smooth',
        });
    }, 3000); // Change time as needed

    // Auto-scroll Top Artists every 3 seconds (optional)
    setInterval(() => {
        topArtistsList.scrollBy({
            left: topArtistItemWidth,
            behavior: 'smooth',
        });
    }, 3000); // Change time as needed

    function showSlide(index) {
        slides.forEach((slide, i) => {
            if (i === index) {
                slide.classList.add('active');
                slide.style.opacity = "1"; // Fade-in effect
                slide.style.transform = "translateX(0)"; // Ensure the slide is fully visible
    
                if (slide.querySelector('.game-info')) {
                    resetTimer();
                }

                // If it's the Top Artists slide, trigger the animation
                if (i === 3) { // Slide 4 is at index 3
                    animateTopArtists();
                }
            } else {
                slide.style.opacity = "0"; // Fade-out effect
                slide.style.transform = "translateX(100%)"; // Move slide out of view
                setTimeout(() => slide.classList.remove('active'), 500); // Match transition duration
                if (slide.querySelector('.game-info')) {
                    clearInterval(timer);
                    resetTimerBar();
                }
            }
        });
    
        sessionStorage.setItem('currentSlide', index);
    }

    // Timer Countdown Logic
    function startTimer(duration) {
        let timeLeft = duration;
        timerElement.textContent = timeLeft;
        timerBar.style.width = "100%";
        timerBar.style.backgroundColor = "green";

        timer = setInterval(() => {
            timeLeft--;
            timerElement.textContent = timeLeft;

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

    showSlide(currentSlide);

    document.getElementById('next').addEventListener('click', () => {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    });

    document.getElementById('prev').addEventListener('click', () => {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(currentSlide);
    });
});