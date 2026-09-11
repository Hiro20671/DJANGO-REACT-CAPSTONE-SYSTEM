/**
 * BMV3 Child Care Management System - Interactive Animation Engine
 * - Smooth Lerp Cursor Follower with Auto-Hide and Text Protection
 * - Event-Delegated 3D Perspective Tilt & Bento Spotlight Glow
 * - Contained Fluid Button Ripples & Tactile Feedback
 * - IntersectionObserver Scroll Reveal with MutationObserver for React
 * - Dynamic Cubic Ease-Out Number Counter Engine
 * - Smooth Navigation Progress Bar
 */

(function () {
    'use strict';

    // Check device capability
    const isTouchDevice = window.matchMedia('(pointer: coarse)').matches || window.innerWidth <= 768;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // --- 1. Refined Interactive Cursor Follower with Lerp ---
    if (!isTouchDevice && !prefersReducedMotion) {
        const cursorDot = document.createElement('div');
        const cursorRing = document.createElement('div');
        cursorDot.className = 'custom-cursor-dot';
        cursorRing.className = 'custom-cursor-ring';

        document.documentElement.appendChild(cursorDot);
        document.documentElement.appendChild(cursorRing);

        let mouseX = -200, mouseY = -200;
        let ringX = -200, ringY = -200;
        let isCursorVisible = false;

        window.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;

            if (!isCursorVisible) {
                isCursorVisible = true;
                document.body.classList.remove('cursor-hidden');
            }

            cursorDot.style.transform = `translate(${mouseX}px, ${mouseY}px) translate(-50%, -50%)`;
        });

        document.addEventListener('mouseleave', () => {
            isCursorVisible = false;
            document.body.classList.add('cursor-hidden');
        });

        document.addEventListener('mouseenter', () => {
            isCursorVisible = true;
            document.body.classList.remove('cursor-hidden');
        });

        function renderCursor() {
            if (isCursorVisible) {
                ringX += (mouseX - ringX) * 0.22;
                ringY += (mouseY - ringY) * 0.22;
                cursorRing.style.transform = `translate(${ringX}px, ${ringY}px) translate(-50%, -50%)`;
            }
            requestAnimationFrame(renderCursor);
        }
        requestAnimationFrame(renderCursor);

        // Hover expansions & text input protection via event delegation
        const clickableSelectors = 'a, button, [role="button"], .btn, input[type="submit"], input[type="button"], .card, .stat-card, .dot, .tab-btn';
        const textInputSelectors = 'input[type="text"], input[type="password"], input[type="email"], input[type="search"], textarea, [contenteditable="true"]';

        document.addEventListener('mouseover', (e) => {
            if (e.target.closest(textInputSelectors)) {
                cursorDot.style.opacity = '0';
                cursorRing.style.opacity = '0';
            } else if (e.target.closest(clickableSelectors)) {
                document.body.classList.add('cursor-hover');
                cursorDot.style.opacity = '1';
                cursorRing.style.opacity = '1';
            }
        });

        document.addEventListener('mouseout', (e) => {
            if (e.target.closest(textInputSelectors)) {
                cursorDot.style.opacity = '1';
                cursorRing.style.opacity = '1';
            }
            if (e.target.closest(clickableSelectors)) {
                document.body.classList.remove('cursor-hover');
            }
        });

        document.addEventListener('mousedown', () => document.body.classList.add('cursor-active'));
        document.addEventListener('mouseup', () => document.body.classList.remove('cursor-active'));
    }

    // --- 2. Dynamic Bento Spotlight Glow & 3D Tilt (Event-Delegation Architecture) ---
    const cardSelectors = '.card, .stat-card, .overview-card, .dashboard-card, .feature-card, .modern-card, .stat-card-modern, .gallery-card, .summary-card, #react-teacher-dashboard-root .resp-grid-4 > * > div, #react-parent-dashboard-root .resp-grid-4 > * > div';

    let currentTiltCard = null;

    document.addEventListener('mousemove', (e) => {
        if (prefersReducedMotion) return;

        const card = e.target.closest(cardSelectors);

        if (card) {
            currentTiltCard = card;
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Set spotlight CSS variables for gradient glow
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);

            // Subtle 3D perspective tilt
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -4.5;
            const rotateY = ((x - centerX) / centerX) * 4.5;

            card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px) scale(1.006)`;
        } else if (currentTiltCard) {
            // Reset when leaving card
            currentTiltCard.style.transform = 'perspective(900px) rotateX(0deg) rotateY(0deg) translateY(0px) scale(1)';
            currentTiltCard = null;
        }
    });

    document.addEventListener('mouseout', (e) => {
        const card = e.target.closest(cardSelectors);
        if (card && (!e.relatedTarget || !card.contains(e.relatedTarget))) {
            card.style.transform = 'perspective(900px) rotateX(0deg) rotateY(0deg) translateY(0px) scale(1)';
        }
    });

    // --- 3. Contained Fluid Button Ripples ---
    const buttonSelectors = 'button, .btn, .btn-primary, .btn-secondary, .btn-action, input[type="submit"], .btn-primary-hero, .btn-secondary-hero, .hero-btn';

    document.addEventListener('click', (e) => {
        const btn = e.target.closest(buttonSelectors);
        if (!btn) return;

        btn.classList.add('btn-ripple-container');
        const rect = btn.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 1.8;
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        const wave = document.createElement('span');
        wave.className = 'btn-ripple-wave';
        wave.style.width = `${size}px`;
        wave.style.height = `${size}px`;
        wave.style.left = `${x}px`;
        wave.style.top = `${y}px`;

        btn.appendChild(wave);

        setTimeout(() => {
            if (wave.parentNode) {
                wave.parentNode.removeChild(wave);
            }
        }, 650);
    });

    // --- 4. Scroll-Triggered Reveal Engine (IntersectionObserver + MutationObserver) ---
    const revealSelectors = '.reveal-on-scroll, .reveal-slide-up, .reveal-fade, .reveal-scale, .reveal-slide-left, .reveal-slide-right';

    let revealObserver = null;
    if ('IntersectionObserver' in window && !prefersReducedMotion) {
        revealObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-revealed');
                    // Check if element has count-up
                    if (entry.target.classList.contains('stat-countup')) {
                        animateCountUp(entry.target);
                    }
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: '0px 0px -40px 0px'
        });
    }

    function observeNewRevealElements(rootNode = document) {
        if (!revealObserver) {
            // Fallback: reveal immediately
            rootNode.querySelectorAll(revealSelectors).forEach(el => el.classList.add('is-revealed'));
            return;
        }

        rootNode.querySelectorAll(revealSelectors).forEach(el => {
            if (!el.classList.contains('is-revealed')) {
                revealObserver.observe(el);
            }
        });
    }

    // --- 5. Dynamic Cubic Ease-Out Number Counter Engine ---
    function animateCountUp(el) {
        if (el.dataset.counted === 'true') return;
        el.dataset.counted = 'true';

        const text = el.innerText.trim();
        const match = text.match(/([^\d]*)([\d,.]+)(.*)/);
        if (!match) return;

        const prefix = match[1] || '';
        const targetNum = parseFloat(match[2].replace(/,/g, ''));
        const suffix = match[3] || '';
        const isDecimal = match[2].includes('.');

        if (isNaN(targetNum)) return;

        const duration = 1200; // ms
        const startTime = performance.now();

        function update(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Cubic ease-out curve
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentVal = targetNum * easeOut;

            const formattedVal = isDecimal 
                ? currentVal.toFixed(1) 
                : Math.round(currentVal).toLocaleString();

            el.innerText = `${prefix}${formattedVal}${suffix}`;

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.innerText = text; // Restore exact text
            }
        }

        requestAnimationFrame(update);
    }

    // --- 6. Page Top Loading Progress Bar ---
    document.addEventListener('DOMContentLoaded', () => {
        let progressBar = document.getElementById('page-progress-bar');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.id = 'page-progress-bar';
            document.body.appendChild(progressBar);
        }

        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href]');
            if (link) {
                const href = link.getAttribute('href');
                if (href && !href.startsWith('#') && !href.startsWith('javascript:') && !link.getAttribute('target') && !e.ctrlKey && !e.metaKey) {
                    progressBar.style.opacity = '1';
                    progressBar.style.width = '68%';
                }
            }
        });

        window.addEventListener('beforeunload', () => {
            if (progressBar) {
                progressBar.style.opacity = '1';
                progressBar.style.width = '100%';
            }
        });

        // Initialize scroll reveal on existing DOM elements
        observeNewRevealElements();

        // Attach count-up to static elements marked with .stat-countup
        document.querySelectorAll('.stat-countup').forEach(el => {
            if (!revealObserver) {
                animateCountUp(el);
            }
        });

        // --- 7. Watch for Dynamic React Node Injections (MutationObserver) ---
        if ('MutationObserver' in window) {
            const domObserver = new MutationObserver((mutations) => {
                mutations.forEach(mutation => {
                    if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                        mutation.addedNodes.forEach(node => {
                            if (node.nodeType === 1) {
                                observeNewRevealElements(node);
                            }
                        });
                    }
                });
            });

            domObserver.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    });

})();
