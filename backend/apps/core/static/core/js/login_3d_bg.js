/**
 * BMV3 Child Care Management System - 3D School & Daycare Visual Engine
 * High-performance WebGL 3D scene using Three.js tailored specifically for Early Childhood Education & Daycare
 * Features:
 * - 3D Wooden ABC & 123 Alphabet Learning Blocks with friendly illustrated face textures
 * - 3D Origami Paper Airplane gliding and banking gracefully in 3D flight paths
 * - 3D Beveled Golden Achievement Star (Milestone Reward)
 * - 3D Montessori Educational Sensory Counting Rings
 * - Soft Floating Classroom Soap Bubbles with gentle harmonic sway
 * - Interactive 3D Camera Parallax Depth reacting to mouse position
 * - Responsive ResizeObserver and Visibility Lifecycle Management
 */

(function () {
    'use strict';

    // Respect reduced motion
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    function initDaycare3DBackground() {
        const container = document.getElementById('left-panel-container');
        const canvas = document.getElementById('canvas-3d-bg');

        if (!container || !canvas || typeof THREE === 'undefined') {
            return;
        }

        let width = container.clientWidth;
        let height = container.clientHeight;

        if (width <= 0 || height <= 0) {
            setTimeout(initDaycare3DBackground, 100);
            return;
        }

        // --- 1. Scene, Camera, Renderer & Lighting ---
        const scene = new THREE.Scene();

        const camera = new THREE.PerspectiveCamera(55, width / height, 1, 1200);
        camera.position.z = 400;

        let renderer;
        try {
            renderer = new THREE.WebGLRenderer({
                canvas: canvas,
                alpha: true,
                antialias: true,
                powerPreference: 'high-performance'
            });
        } catch (e) {
            console.warn('WebGL not supported for 3D daycare background:', e);
            return;
        }

        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Soft ambient and directional lights for rich 3D shading
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.82);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.75);
        dirLight.position.set(-120, 180, 260);
        scene.add(dirLight);

        const warmLight = new THREE.PointLight(0xf59e0b, 1.2, 450);
        warmLight.position.set(160, -100, 180);
        scene.add(warmLight);

        const blueLight = new THREE.PointLight(0x38bdf8, 1.0, 450);
        blueLight.position.set(-180, 150, 150);
        scene.add(blueLight);

        // --- 2. Procedural Block Face Texture Generator ---
        function createBlockTexture(letter, textColor, bgColor, borderColor) {
            const size = 128;
            const c = document.createElement('canvas');
            c.width = size;
            c.height = size;
            const ctx = c.getContext('2d');

            // Solid background
            ctx.fillStyle = bgColor || '#ffffff';
            ctx.fillRect(0, 0, size, size);

            // Outer wooden block border
            ctx.strokeStyle = borderColor || '#cbd5e1';
            ctx.lineWidth = 10;
            ctx.strokeRect(5, 5, size - 10, size - 10);

            // Inset highlight
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
            ctx.lineWidth = 3;
            ctx.strokeRect(12, 12, size - 24, size - 24);

            // Letter / Number Glyph
            ctx.fillStyle = textColor;
            ctx.font = 'bold 70px "Montserrat", "Comic Sans MS", "Arial Rounded MT Bold", sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(letter, size / 2, size / 2 + 4);

            const texture = new THREE.CanvasTexture(c);
            texture.needsUpdate = true;
            return texture;
        }

        // --- 3. 3D Wooden ABC Learning Block #1 ---
        const blockMaterials1 = [
            new THREE.MeshLambertMaterial({ map: createBlockTexture('A', '#ef4444', '#fff7ed', '#fdba74') }), // Right
            new THREE.MeshLambertMaterial({ map: createBlockTexture('1', '#1e40af', '#eff6ff', '#93c5fd') }), // Left
            new THREE.MeshLambertMaterial({ map: createBlockTexture('B', '#10b981', '#ecfdf5', '#86efac') }), // Top
            new THREE.MeshLambertMaterial({ map: createBlockTexture('2', '#f59e0b', '#fefce8', '#fde047') }), // Bottom
            new THREE.MeshLambertMaterial({ map: createBlockTexture('C', '#0284c7', '#f0f9ff', '#7dd3fc') }), // Front
            new THREE.MeshLambertMaterial({ map: createBlockTexture('★', '#d97706', '#fffbeb', '#fcd34d') })  // Back
        ];

        const abcBlock1 = new THREE.Mesh(new THREE.BoxGeometry(56, 56, 56), blockMaterials1);
        abcBlock1.position.set(-175, 135, -25);
        abcBlock1.rotation.set(0.35, 0.6, -0.2);
        scene.add(abcBlock1);

        // --- 4. 3D Wooden 123 Learning Block #2 ---
        const blockMaterials2 = [
            new THREE.MeshLambertMaterial({ map: createBlockTexture('1', '#f59e0b', '#fffbeb', '#fde047') }), // Right
            new THREE.MeshLambertMaterial({ map: createBlockTexture('2', '#065f46', '#ecfdf5', '#6ee7b7') }), // Left
            new THREE.MeshLambertMaterial({ map: createBlockTexture('3', '#7c3aed', '#f5f3ff', '#c4b5fd') }), // Top
            new THREE.MeshLambertMaterial({ map: createBlockTexture('♥', '#e11d48', '#fff1f2', '#fda4af') }), // Bottom
            new THREE.MeshLambertMaterial({ map: createBlockTexture('▲', '#0284c7', '#f0f9ff', '#7dd3fc') }), // Front
            new THREE.MeshLambertMaterial({ map: createBlockTexture('ABC', '#1e40af', '#eff6ff', '#93c5fd') }) // Back
        ];

        const abcBlock2 = new THREE.Mesh(new THREE.BoxGeometry(42, 42, 42), blockMaterials2);
        abcBlock2.position.set(-145, -165, -35);
        abcBlock2.rotation.set(-0.4, -0.5, 0.3);
        scene.add(abcBlock2);

        // --- 5. 3D Golden Achievement Reward Star ---
        const starShape = new THREE.Shape();
        const starPoints = 5;
        const outerR = 25;
        const innerR = 11;
        for (let i = 0; i < starPoints * 2; i++) {
            const r = (i % 2 === 0) ? outerR : innerR;
            const a = (i * Math.PI) / starPoints - Math.PI / 2;
            const x = Math.cos(a) * r;
            const y = Math.sin(a) * r;
            if (i === 0) starShape.moveTo(x, y);
            else starShape.lineTo(x, y);
        }
        starShape.closePath();

        const starGeometry = new THREE.ExtrudeGeometry(starShape, {
            depth: 7,
            bevelEnabled: true,
            bevelSegments: 2,
            steps: 1,
            bevelSize: 2.5,
            bevelThickness: 2.5
        });
        starGeometry.center();

        const starMaterial = new THREE.MeshLambertMaterial({
            color: 0xf59e0b,
            emissive: 0xb45309,
            emissiveIntensity: 0.28,
            roughness: 0.35
        });

        const goldenStar = new THREE.Mesh(starGeometry, starMaterial);
        goldenStar.position.set(185, -135, -25);
        scene.add(goldenStar);

        // --- 6. 3D Origami Paper Airplane (Symbol of Learning & Play) ---
        const planeGeo = new THREE.BufferGeometry();
        // Custom Folded Dart vertices
        const planeVerts = new Float32Array([
            // Left Wing Upper
            0, 0, 36,     -30, 6, -22,    0, 2, -18,
            // Right Wing Upper
            0, 0, 36,      0, 2, -18,     30, 6, -22,
            // Left Keel
            0, 0, 36,      0, -9, -15,    0, 2, -18,
            // Right Keel
            0, 0, 36,      0, 2, -18,     0, -9, -15
        ]);
        planeGeo.setAttribute('position', new THREE.BufferAttribute(planeVerts, 3));
        planeGeo.computeVertexNormals();

        const planeMat = new THREE.MeshLambertMaterial({
            color: 0xf8fafc,
            emissive: 0x93c5fd,
            emissiveIntensity: 0.15,
            side: THREE.DoubleSide
        });

        const paperAirplane = new THREE.Mesh(planeGeo, planeMat);
        paperAirplane.position.set(160, 155, -20);
        paperAirplane.scale.set(1.1, 1.1, 1.1);
        scene.add(paperAirplane);

        // --- 7. 3D Montessori Educational Sensory Rings ---
        const ringsGroup = new THREE.Group();
        ringsGroup.position.set(165, 0, -40);

        const ringMatEmerald = new THREE.MeshLambertMaterial({ color: 0x10b981, roughness: 0.3 });
        const ringMatSky = new THREE.MeshLambertMaterial({ color: 0x38bdf8, roughness: 0.3 });
        const ringMatHoney = new THREE.MeshLambertMaterial({ color: 0xf59e0b, roughness: 0.3 });

        const ring1 = new THREE.Mesh(new THREE.TorusGeometry(32, 2.5, 16, 40), ringMatEmerald);
        const ring2 = new THREE.Mesh(new THREE.TorusGeometry(24, 2.2, 16, 40), ringMatSky);
        const ring3 = new THREE.Mesh(new THREE.TorusGeometry(16, 2.0, 16, 40), ringMatHoney);

        ring1.rotation.x = 0.6;
        ring2.rotation.y = 0.7;
        ring3.rotation.z = 0.5;

        ringsGroup.add(ring1);
        ringsGroup.add(ring2);
        ringsGroup.add(ring3);
        scene.add(ringsGroup);

        // --- 8. Floating Classroom Soap Bubbles ---
        const bubbleCount = 32;
        const bubbles = [];
        const bubbleGeo = new THREE.SphereGeometry(1, 16, 16);

        const bubblePalette = [0x93c5fd, 0x6ee7b7, 0xfde047, 0xfbcfe8, 0xa5f3fc];

        for (let i = 0; i < bubbleCount; i++) {
            const bColor = bubblePalette[Math.floor(Math.random() * bubblePalette.length)];
            const bMat = new THREE.MeshLambertMaterial({
                color: bColor,
                transparent: true,
                opacity: 0.28 + Math.random() * 0.2,
                blending: THREE.AdditiveBlending
            });

            const bubbleMesh = new THREE.Mesh(bubbleGeo, bMat);
            const radius = 5 + Math.random() * 12;
            bubbleMesh.scale.set(radius, radius, radius);

            const spreadX = Math.max(340, width * 0.7);
            const spreadY = Math.max(320, height * 0.7);

            const startX = (Math.random() - 0.5) * spreadX;
            const startY = -spreadY * 0.6 + Math.random() * spreadY * 1.2;
            const startZ = -100 + Math.random() * 160;

            bubbleMesh.position.set(startX, startY, startZ);
            scene.add(bubbleMesh);

            bubbles.push({
                mesh: bubbleMesh,
                baseX: startX,
                baseY: startY,
                speedY: 0.4 + Math.random() * 0.5,
                swaySpeed: 1 + Math.random() * 1.5,
                swayAmount: 6 + Math.random() * 12,
                phase: Math.random() * Math.PI * 2,
                maxY: spreadY * 0.65,
                resetY: -spreadY * 0.65
            });
        }

        // --- 9. Soft Drifting Star Dust ---
        const dustCount = 140;
        const dustPositions = new Float32Array(dustCount * 3);
        const spreadX = Math.max(360, width * 0.75);
        const spreadY = Math.max(340, height * 0.75);

        for (let i = 0; i < dustCount; i++) {
            dustPositions[i * 3] = (Math.random() - 0.5) * spreadX;
            dustPositions[i * 3 + 1] = (Math.random() - 0.5) * spreadY;
            dustPositions[i * 3 + 2] = (Math.random() - 0.5) * 280;
        }

        const dustGeo = new THREE.BufferGeometry();
        dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPositions, 3));

        const dustMat = new THREE.PointsMaterial({
            size: 3.5,
            color: 0x93c5fd,
            transparent: true,
            opacity: 0.5,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });

        const dustField = new THREE.Points(dustGeo, dustMat);
        scene.add(dustField);

        // --- 10. Interactive 3D Mouse Parallax ---
        let mouseX = 0;
        let mouseY = 0;
        let targetMouseX = 0;
        let targetMouseY = 0;

        container.addEventListener('mousemove', (e) => {
            const rect = container.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            targetMouseX = x * 70;
            targetMouseY = -y * 70;
        });

        container.addEventListener('mouseleave', () => {
            targetMouseX = 0;
            targetMouseY = 0;
        });

        // --- 11. Animation Loop ---
        let clock = new THREE.Clock();
        let animationFrameId;
        let isRunning = true;

        function animate() {
            if (!isRunning) return;

            animationFrameId = requestAnimationFrame(animate);

            const elapsedTime = clock.getElapsedTime();

            // Smooth camera parallax
            mouseX += (targetMouseX - mouseX) * 0.05;
            mouseY += (targetMouseY - mouseY) * 0.05;
            camera.position.x = mouseX;
            camera.position.y = mouseY;
            camera.lookAt(0, 0, 0);

            // Animate 3D ABC Block #1
            abcBlock1.rotation.x += 0.007;
            abcBlock1.rotation.y += 0.009;
            abcBlock1.position.y = 135 + Math.sin(elapsedTime * 1.4) * 10;

            // Animate 3D 123 Block #2
            abcBlock2.rotation.x -= 0.006;
            abcBlock2.rotation.y += 0.008;
            abcBlock2.position.y = -165 + Math.sin(elapsedTime * 1.6 + 1.2) * 8;

            // Animate Golden Star
            goldenStar.rotation.y += 0.012;
            goldenStar.rotation.z = Math.sin(elapsedTime * 1.5) * 0.15;
            goldenStar.position.y = -135 + Math.sin(elapsedTime * 1.8 + 2) * 10;
            const starScale = 1 + Math.sin(elapsedTime * 2.5) * 0.06;
            goldenStar.scale.set(starScale, starScale, starScale);

            // Animate Paper Airplane (Organic flight loop & banking)
            const flightTime = elapsedTime * 0.9;
            paperAirplane.position.x = 160 + Math.sin(flightTime) * 35;
            paperAirplane.position.y = 155 + Math.cos(flightTime * 1.2) * 18;
            paperAirplane.rotation.z = Math.sin(flightTime) * 0.25; // Bank roll
            paperAirplane.rotation.y = Math.cos(flightTime) * 0.2;  // Turn yaw
            paperAirplane.rotation.x = Math.sin(flightTime * 1.2) * 0.15; // Pitch

            // Animate Montessori Rings
            ring1.rotation.x += 0.009;
            ring1.rotation.y += 0.006;
            ring2.rotation.y += 0.008;
            ring2.rotation.z += 0.007;
            ring3.rotation.z += 0.01;
            ring3.rotation.x -= 0.006;
            ringsGroup.position.y = 0 + Math.sin(elapsedTime * 1.3 + 0.8) * 10;

            // Animate Floating Bubbles
            bubbles.forEach(b => {
                b.mesh.position.y += b.speedY;
                b.mesh.position.x = b.baseX + Math.sin(elapsedTime * b.swaySpeed + b.phase) * b.swayAmount;

                // Reset when floating off top
                if (b.mesh.position.y > b.maxY) {
                    b.mesh.position.y = b.resetY;
                }
            });

            // Slowly drift star dust towards camera
            const dustPosAttr = dustGeo.attributes.position;
            for (let i = 0; i < dustCount; i++) {
                let z = dustPosAttr.getZ(i);
                z += 0.25;
                if (z > 140) z = -140;
                dustPosAttr.setZ(i, z);
            }
            dustPosAttr.needsUpdate = true;

            renderer.render(scene, camera);
        }

        animate();

        // --- 12. Responsive ResizeObserver ---
        const resizeObserver = new ResizeObserver(() => {
            const newW = container.clientWidth;
            const newH = container.clientHeight;
            if (newW > 0 && newH > 0) {
                camera.aspect = newW / newH;
                camera.updateProjectionMatrix();
                renderer.setSize(newW, newH);
            }
        });
        resizeObserver.observe(container);

        // --- 13. Visibility Lifecycle ---
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                isRunning = false;
                cancelAnimationFrame(animationFrameId);
            } else {
                if (!isRunning) {
                    isRunning = true;
                    clock.start();
                    animate();
                }
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDaycare3DBackground);
    } else {
        initDaycare3DBackground();
    }
})();
