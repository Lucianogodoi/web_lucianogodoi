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
    newWindow.style.overflow = 'auto';

    // Posición aleatoria dentro del alto visible
    const ventanaAltura = 400; // altura estimada de la ventana
    const margenInferior = 300;
    const maxTop = window.innerHeight - ventanaAltura - margenInferior;
    const topPos = Math.max(30, Math.random() * maxTop);
    newWindow.style.top = `${topPos}px`;

    newWindow.style.left = Math.random() * (window.innerWidth - 450) + 'px';

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
                    <li>🏗️ <img src="static/codelco.png" alt="Codelco" style="width: 20px; vertical-align: middle;"> 
                        <a href="#" onclick="abrirProyectoGPRODET()">Proyecto GPRODET</a>
                    </li>
                    <li>🏢 <img src="static/igp-logo.png" alt="IGP" style="width: 20px; vertical-align: middle;">
                        <a href="#" onclick="abrirProyectoIGP()">Instituto Gestión de Personas</a>
                    </li>
                </ul>
            `;
            break;
            case 'formacion':
                title.textContent = 'Formación & Ciencia de Datos';
                content.innerHTML = `
                    <h2>Especialización en Inteligencia Artificial</h2>
                    <p>
                        📊 <strong>Master of Science in Data Science</strong> – Universidad Adolfo Ibáñez (2022–2023)<br>
                        ⚙️ <strong>Ingeniería Civil Industrial</strong> + Minor en Business Analytics (2018–2022)
                    </p>
                    <p>Mi formación está orientada al desarrollo de soluciones basadas en IA, big data y machine learning.</p>
            
                    <h3>🧠 Experiencia práctica destacada</h3>
                    <ul>
                        <li>🔍 Desarrollo de algoritmos de detección de colusión interna en <strong>Tottus</strong>, permitiendo identificar pérdidas por <strong>422 millones CLP</strong> en 6 meses.</li>
                        <li>💸 Detección de lavado de dinero en <strong>LarrainVial</strong>, aplicando modelos adaptados a normativa de la <strong>CMF</strong> y la <strong>UAF</strong>.</li>
                        <li>📊 Desarrollo de modelos de <em>suitability</em> para clasificación de clientes.</li>
                        <li>🤖 Experiencia con bots RAG, integración de soluciones con <strong>ComplyAdvantage</strong> y <strong>Codelco</strong>.</li>
                    </ul>
            
                    <h3>📚 Curso Internacional</h3>
                    <p>
                        🎓 <strong>Harvard: Improving your Business through a Culture of Health</strong><br>
                        <a href="static/docs/harvard-certificado.pdf" target="_blank">📄 Ver certificado</a>
                    </p>
            
                    <h3>🔧 Tecnologías dominadas</h3>
                    <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" title="Python" width="30"/>
                        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/r/r-original.svg" title="R" width="30"/>
                        <img src="static/sql.jpg" title="SQL" width="30"/>
                        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" title="HTML" width="30"/>
                        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" title="CSS" width="30"/>
                        <img src="static/complyadvantage-logo.png" title="ComplyAdvantage" width="60"/>
                        <img src="static/codelco.png" title="Codelco" width="40"/>
                        <img src="static/chatgpt.png" title="ChatGPT / RAG" width="40"/>
                    </div>
                `;
                break;            
        case 'contacto':
            title.textContent = 'Contacto & Recursos';
            content.innerHTML = `
                <h2>Contacto</h2>
                <p>📄 <a href="static/docs/CV_Godoi.pdf" target="_blank">Descargar CV</a></p>
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

function abrirProyectoGPRODET() {
    const template = document.getElementById('window-template');
    const newWindow = template.cloneNode(true);
    newWindow.style.display = 'block';
    newWindow.style.left = '100px';
    newWindow.style.top = '100px';
    newWindow.style.width = '600px';
    newWindow.style.height = 'auto';
    newWindow.style.maxHeight = '80vh';

    const title = newWindow.querySelector('.window-title');
    const content = newWindow.querySelector('.window-content');

    title.textContent = 'Proyecto GPRODET';

    content.innerHTML = `
        <img src="static/codelco.png" alt="Logo Codelco" style="width: 100px; float: right; margin-left: 10px;">
        <p>GPRODET es una herramienta web desarrollada para Codelco. Su objetivo es ayudar en la gestión de proyectos mediante un sistema de evaluación inteligente y análisis de riesgo con IA.</p>
        <img src="static/gprodet-preview.jpg" alt="Preview GPRODET" style="width: 100%; border-radius: 10px; margin: 10px 0;">
        <p>
            <a href="https://gprodet.cl/" target="_blank" style="font-weight: bold;">
                🌐 Conoce la página
            </a>
        </p>
        <p>Tecnologías utilizadas:</p>
        <div style="display: flex; gap: 10px;">
            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" title="HTML" width="30"/>
            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" title="CSS" width="30"/>
            <img src="static/chatgpt.png" title="ChatGPT RAG" width="30"/>
        </div>
    `;

    document.body.appendChild(newWindow);
    makeDraggable(newWindow);
}

function abrirProyectoIGP() {
    const template = document.getElementById('window-template');
    const newWindow = template.cloneNode(true);
    newWindow.style.display = 'block';
    newWindow.style.left = '120px';
    newWindow.style.top = '120px';
    newWindow.style.width = '600px';
    newWindow.style.height = 'auto';
    newWindow.style.maxHeight = '80vh';

    const title = newWindow.querySelector('.window-title');
    const content = newWindow.querySelector('.window-content');

    title.textContent = 'Instituto Gestión de Personas';

    content.innerHTML = `
        <img src="static/igp-logo.png" alt="IGP Logo" style="width: 100px; float: right; margin-left: 10px;">
        <p>Desarrollo de sitio web institucional para el Instituto Gestión de Personas, con enfoque en accesibilidad, claridad y estructura profesional.</p>
        <img src="static/igp-preview.jpg" alt="Preview IGP" style="width: 100%; border-radius: 10px; margin: 10px 0;">
        <p>
            <a href="https://institutogestiondepersonas.cl/" target="_blank" style="font-weight: bold;">
                🌐 Conoce la página
            </a>
        </p>
        <p>Tecnologías utilizadas:</p>
        <div style="display: flex; gap: 10px;">
            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" title="HTML" width="30"/>
            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" title="CSS" width="30"/>
        </div>
    `;

    document.body.appendChild(newWindow);
    makeDraggable(newWindow);
}


let msnPopups = [];

function mostrarMSN(titulo, mensaje) {
    const contenedor = document.createElement('div');
    contenedor.className = 'msn-popup';
    contenedor.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
            <img src="static/msn-logo.png" alt="MSN" style="width: 20px; height: 20px;">
            <span style="font-weight: bold; font-size: 13px; color: #1c5180;">Windows Live Messenger</span>
        </div>
        <div style="display: flex; gap: 10px;">
            <img src="static/luciano-avatar.png" alt="Avatar" style="width: 50px; height: 50px; border: 1px solid #ccc;">
            <div style="flex: 1;">
                <p style="margin: 0; font-weight: bold;">Luciano Godoi dice:</p>
                <p style="margin: 5px 0 0;">${mensaje}</p>
            </div>
        </div>
        <div class="options">
            <span onclick="cerrarPopup(this)">Cerrar</span>
            <span onclick="enviarZumbido(this)">Enviar zumbido</span>
        </div>
    `;

    const baseBottom = 20;
    const spacing = 130;
    
    // Lo agregamos *temporalmente* al array
    msnPopups.push(contenedor);

    // Recalcular la posición de todos los cuadros activos
    msnPopups.forEach((popup, i) => {
        popup.style.bottom = `${baseBottom + i * spacing}px`;
    });


    // ✅ SONIDO solo si el mensaje es de Luciano
    if (titulo === 'Luciano Godoi') {
        mensajeAudio.currentTime = 0;
        mensajeAudio.play();
    }

    document.body.appendChild(contenedor);

    setTimeout(() => {
        if (contenedor && contenedor.parentElement) {
            contenedor.remove();
            msnPopups = msnPopups.filter(p => p !== contenedor);
    
            // Reordenar desde cero
            msnPopups.forEach((popup, i) => {
                popup.style.bottom = `${baseBottom + i * spacing}px`;
            });
        }
    }, 6000);
    
    
}

function cerrarPopup(elem) {
    const contenedor = elem.closest('.msn-popup');
    if (!contenedor) return;

    contenedor.remove();
    msnPopups = msnPopups.filter(p => p !== contenedor);

    // Reordenar todos los cuadros
    const baseBottom = 20;
    const spacing = 130;
    msnPopups.forEach((popup, i) => {
        popup.style.bottom = `${baseBottom + i * spacing}px`;
    });
}

// Lanzar los mensajes iniciales
window.addEventListener('load', () => {
    setTimeout(() => mostrarMSN('Luciano Godoi', 'Hola, bienvenido a mi página.'), 1000);
    setTimeout(() => mostrarMSN('Luciano Godoi', 'Este es mi portafolio ✨'), 3500);
});

let zumbidoCount = 0;


function enviarZumbido(elem) {
    const contenedor = elem.closest('.msn-popup');
    contenedor.remove();
    msnPopups = msnPopups.filter(p => p !== contenedor);

    if (zumbidoCount === 0) {
        zumbidoCount++;
        mostrarMSN('Tú', '🔔 Zumbido enviado a Luciano...');
        setTimeout(() => {
            mostrarMSN('Luciano Godoi', '😠');
        }, 1500);
    } else if (zumbidoCount === 1) {
        zumbidoCount++;
        mostrarMSN('Tú', '🔔 Zumbido enviado a Luciano...');
        setTimeout(() => {
            mostrarMSN('Luciano Godoi', '😠😠😠');
        }, 1500);
    } else {
        mostrarMSN('Luciano Godoi', '🚫 Te he bloqueado la opción de enviar zumbido.');
    }
}


const mensajeAudio = new Audio('static/msn-notification.mp3');
mensajeAudio.volume = 0.2; // volumen suave
