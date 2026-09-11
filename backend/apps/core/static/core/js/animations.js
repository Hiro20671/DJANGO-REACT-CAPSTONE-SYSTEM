/**
 * BMV3 Modern UI Design & Animation System JavaScript
 * - Interactive Custom Mouse Cursor Follower
 * - Real-time 3D Card Tilt Engine
 * - Page Loading Progress Bar
 * - Scroll Intersection Observer
 */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        // --- 1. Custom Interactive Cursor Follower ---
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && window.innerWidth > 768) {
            let cursorDot = document.createElement('div');
            let cursorRing = document.createElement('div');
            cursorDot.className = 'custom-cursor-dot';
            cursorRing.className = 'custom-cursor-ring';

            document.body.appendChild(cursorDot);
            document.body.appendChild(cursorRing);

            let mouseX = -100, mouseY = -100;
            let ringX = -100, ringY = -100;

            document.addEventListener('mousemove', (e) => {
                mouseX = e.clientX;
                mouseY = e.clientY;
                cursorDot.style.left = `${mouseX}px`;
                cursorDot.style.top = `${mouseY}px`;
            });

            function renderCursor() {
                ringX += (mouseX - ringX) * 0.18;
                ringY += (mouseY - ringY) * 0.18;
                cursorRing.style.left = `${ringX}px`;
                cursorRing.style.top = `${ringY}px`;
                requestAnimationFrame(renderCursor);
            }
            requestAnimationFrame(renderCursor);

            // Add hover effect listeners on interactive elements
            const interactiveSelectors = 'a, button, input, select, textarea, .card-3d-tilt, .btn, [role="button"]';
            document.body.addEventListener('mouseover', (e) => {
                if (e.target.closest(interactiveSelectors)) {
                    document.body.classList.add('cursor-hover');
                }
            });

            document.body.addEventListener('mouseout', (e) => {
                if (e.target.closest(interactiveSelectors)) {
                    document.body.classList.remove('cursor-hover');
                }
            });

            document.addEventListener('mousedown', () => document.body.classList.add('cursor-active'));
            document.addEventListener('mouseup', () => document.body.classList.remove('cursor-active'));
        }

        // --- 2. Real-Time 3D Tilt Card Engine ---
        const tiltCards = document.querySelectorAll('.card-3d-tilt');
        tiltCards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = ((y - centerY) / centerY) * -8; // Pitch max 8deg
                const rotateY = ((x - centerX) / centerX) * 8;   // Yaw max 8deg

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(8px)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
            });
        });

        // --- 3. Page Top Loading Progress Bar ---
        let progressBar = document.createElement('div');
        progressBar.id = 'page-progress-bar';
        document.body.appendChild(progressBar);

        document.querySelectorAll('a[href]').forEach(link => {
            const href = link.getAttribute('href');
            if (href && !href.startsWith('#') && !href.startsWith('javascript:') && !link.getAttribute('target')) {
                link.addEventListener('click', () => {
                    progressBar.style.opacity = '1';
                    progressBar.style.width = '70%';
                });
            }
        });

        window.addEventListener('beforeunload', () => {
            progressBar.style.opacity = '1';
            progressBar.style.width = '100%';
        });

        // --- 4. Intersection Observer for Scroll Animations ---
        const observerOptions = {
            threshold: 0.12,
            rootMargin: '0px 0px -50px 0px'
        };

        const scrollObserver = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    obs.unobserve(entry.target);
                }
            });
        }, observerOptions);

        document.querySelectorAll('.fade-in-up, .zoom-in-entrance, .slide-in-left, .slide-in-right').forEach(el => {
            scrollObserver.observe(el);
        });
    });
})();
