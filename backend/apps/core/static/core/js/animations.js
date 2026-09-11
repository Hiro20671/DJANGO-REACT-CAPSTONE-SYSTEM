/**
 * BMV3 Modern UI Design & Animation System JavaScript
 * - Interactive Custom Mouse Cursor Follower & Click Ripple Waves
 * - Real-time 3D Card Tilt Engine for All Cards
 * - Page Loading Progress Bar
 * - Magnetic Button Cursor Pull
 */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        // --- 1. Custom Interactive Cursor Follower & Click Ripple ---
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
                ringX += (mouseX - ringX) * 0.2;
                ringY += (mouseY - ringY) * 0.2;
                cursorRing.style.left = `${ringX}px`;
                cursorRing.style.top = `${ringY}px`;
                requestAnimationFrame(renderCursor);
            }
            requestAnimationFrame(renderCursor);

            // Add hover effect listeners on all interactive elements
            const interactiveSelectors = 'a, button, input, select, textarea, .card, .stat-card, .btn, .sidebar a, [role="button"]';
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

            document.addEventListener('mousedown', (e) => {
                document.body.classList.add('cursor-active');

                // Spawn click ripple wave
                let ripple = document.createElement('div');
                ripple.className = 'click-ripple';
                ripple.style.left = `${e.clientX}px`;
                ripple.style.top = `${e.clientY}px`;
                document.body.appendChild(ripple);

                setTimeout(() => {
                    if (ripple.parentNode) ripple.parentNode.removeChild(ripple);
                }, 600);
            });

            document.addEventListener('mouseup', () => document.body.classList.remove('cursor-active'));
        }

        // --- 2. Real-Time 3D Tilt Card Engine (Targets All Cards Automatically) ---
        const tiltCardSelectors = '.card, .stat-card, .form-wrapper, .overview-card, .announcement-card, .feature-card, .dashboard-card';
        const tiltCards = document.querySelectorAll(tiltCardSelectors);
        
        tiltCards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = ((y - centerY) / centerY) * -6; // Pitch max 6deg
                const rotateY = ((x - centerX) / centerX) * 6;   // Yaw max 6deg

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px) translateZ(10px)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px) translateZ(0px)';
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
    });
})();
