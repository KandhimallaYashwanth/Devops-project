const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('farming-action'); // Add farming action animation
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);


// Observe all cards and sections
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.importance-card, .fact-card');
    animatedElements.forEach(el => observer.observe(el));
});

// Dynamic crop growing animation
function createCrops() {
    const crops = document.querySelector('.crops');
    const numberOfCrops = Math.floor(window.innerWidth / 40); // Adjust spacing
    
    crops.innerHTML = '';
    for (let i = 0; i < numberOfCrops; i++) {
        const crop = document.createElement('div');
        crop.className = 'crop';
        crop.style.animationDelay = `${i * 0.1}s`;
        crops.appendChild(crop);
    }
}

// Initialize and handle resize
createCrops();
window.addEventListener('resize', createCrops);

// Smooth scroll for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});