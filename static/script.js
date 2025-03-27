// Actualizar reloj
function updateClock() {
    const clock = document.getElementById('clock');
    const now = new Date();
    clock.textContent = now.toLocaleTimeString();
}
setInterval(updateClock, 1000);
updateClock();

// Abrir ventana con contenido personalizado
function openWindow(type) {
    const template = document.getElementById('window-template');
    const newWindow = template.cloneNode(true);
    newWindow.style.display = 'block';
    newWindow.style.height = 'auto';
    newWindow.style.maxHeight = '80vh'; // para evitar que sea más alto que la pantalla
    newWindow.style.width = '500px'; // opcional, si quieres que sea un poco más ancho

    
    // Posición aleatoria
    newWindow.style.left = Math.random() * (window.innerWidth - 450) + 'px';
    newWindow.style.top = (Math.random() * (window.innerHeight - 350 - 100) + 30) + 'px';


    const title = newWindow.querySelector('.window-title');
    const content = newWindow.querySelector('.window-content');

    // Contenido según el tipo
    switch (type) {
        case 'sobre-mi':
            title.textContent = 'Sobre Mí';
            content.innerHTML = `
                <h2>Luciano Godoi</h2>
                <img src="static/luciano.jpg" alt="Luciano Godoi" style="width: 100px; border-radius: 50%; margin-bottom: 10px;">
                <p>Especialista en inteligencia financiera e inteligencia artificial. Actualmente, trabajo en LarrainVial como Analista de Inteligencia Financiera. Anteriormente, fui Data Scientist en Tottus, donde desarrollé algoritmos de detección de fraude basados en IA.</p>
                <p>Mi enfoque: IA, detección de fraude y estrategias AML. Desarrollo soluciones con machine learning, big data y modelos predictivos.</p>
            `;
            break;

        case 'redes':
            title.textContent = 'Redes Sociales';
            content.innerHTML = `
                <h2>Creación de Contenido</h2>
                <p>Comparto información sobre IA y tecnología en:</p>
                <ul>
                    <li>🎙️ <a href="https://open.spotify.com/show/0OQon7yas4Ab4nhlOEUg0B" target="_blank">Escuchar Podcast</a></li>
                    <li>📸 <a href="https://www.instagram.com/chanogodoi/" target="_blank">Instagram: @chanogodoi</a></li>
                    <li>✍️ <a href="#" onclick="mostrarMensajeBlog()">Leer mi Blog</a></li>
                </ul>
            `;
            break;
        case 'proyectos':
            title.textContent = 'Proyectos & Investigación';
            content.innerHTML = `
                <h2>Mis Proyectos</h2>
                <p>He trabajado en investigaciones y proyectos aplicando ciencia de datos e IA:</p>
                <ul>
                    <li>🔭 <a href="static/docs/Tesis_Godoi.pdf" target="_blank">Investigación en Astronomía</a></li>
                    <li>🏗️ Proyecto en Codelco</li>
                </ul>
            `;
            break;
        case 'formacion':
            title.textContent = 'Cursos & Formación';
            content.innerHTML = `
                <h2>Formación</h2>
                <p>🎓 Cursos y formación en ciencia de datos, IA y más.</p>
            `;
            break;
        case 'contacto':
            title.textContent = 'Contacto & Recursos';
            content.innerHTML = `
                <h2>Contacto</h2>
                <p>📄 <a href="#">Descargar CV</a></p>
                <p>🔗 <a href="https://www.linkedin.com/in/lucianogodoi" target="_blank">LinkedIn</a></p>
            `;
            break;
    }

    document.body.appendChild(newWindow);
    makeDraggable(newWindow);
}

function mostrarMensajeBlog() {
    alert("El blog está en construcción 🚧. ¡Pronto habrá contenido!");
}


// Cerrar ventana
function closeWindow(button) {
    const window = button.closest('.window');
    window.remove();
}

function makeDraggable(element, onMoveCallback = () => {}) {
    let isDragging = false;
    let currentX = 0;
    let currentY = 0;
    let initialX = 0;
    let initialY = 0;

    const dragTarget = element.classList.contains('window') 
        ? element.querySelector('.window-header') 
        : element;

    dragTarget.addEventListener('mousedown', (e) => {
        isDragging = true;
        initialX = e.clientX - (parseInt(element.style.left) || 0);
        initialY = e.clientY - (parseInt(element.style.top) || 0);
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            element.style.left = currentX + 'px';
            element.style.top = currentY + 'px';
            onMoveCallback();
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
    });
}



document.querySelectorAll('.app-icon').forEach(icon => {
    let moved = false;

    makeDraggable(icon, () => { moved = true; });

    icon.addEventListener('click', (e) => {
        if (moved) {
            e.preventDefault(); // Evita abrir el enlace si fue arrastrado
            moved = false;
        }
    });
});


function openBackgroundSettings() {
    const panel = document.getElementById('background-settings');
    panel.classList.toggle('hidden');
}

function setBackground(imageUrl) {
    document.body.style.backgroundImage = `url('${imageUrl}')`;
    localStorage.setItem('wallpaper', imageUrl);
}

window.addEventListener('load', () => {
    let savedBg = localStorage.getItem('wallpaper');

    // Si no hay fondo guardado, usar uno por defecto
    if (!savedBg) {
        savedBg = 'https://images.unsplash.com/photo-1506744038136-46273834b3fb'; // fondo predeterminado
        localStorage.setItem('wallpaper', savedBg);
    }

    document.body.style.backgroundImage = `url('${savedBg}')`;
});

