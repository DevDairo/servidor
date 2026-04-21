const API = "http://localhost:5001";

// 🔍 Buscar canciones
async function search() {
    const query = document.getElementById("searchInput").value;

    const res = await fetch(`${API}/api/search?q=${query}`);
    const data = await res.json();

    const container = document.getElementById("results");
    container.innerHTML = "";

    data.results.forEach(song => {
        const div = document.createElement("div");
        div.className = "card";

        div.innerHTML = `
            <img src="${song.thumbnail}">
            <h3>${song.title}</h3>
            <p>${song.artist}</p>
            <button onclick="download('${song.url}')">Descargar</button>
        `;

        container.appendChild(div);
    });
}

// 📥 Descargar
async function download(url) {
    const res = await fetch(`${API}/api/download`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ url })
    });

    const data = await res.json();

    checkStatus(data.task_id);
}

// 📊 Ver estado
async function checkStatus(task_id) {
    const statusDiv = document.getElementById("status");

    const interval = setInterval(async () => {
        const res = await fetch(`${API}/api/status/${task_id}`);
        const data = await res.json();

        statusDiv.innerHTML = `
            Estado: ${data.status} <br>
            Progreso: ${data.progress}%
        `;

        if (data.status === "done" || data.status === "error") {
            clearInterval(interval);
            loadLibrary();
        }
    }, 1500);
}

// 📚 Biblioteca
async function loadLibrary() {
    const res = await fetch(`${API}/api/library`);
    const data = await res.json();

    const container = document.getElementById("library");
    container.innerHTML = "";

    data.songs.forEach(song => {
        const div = document.createElement("div");
        div.className = "card";

        div.innerHTML = `
            <h3>${song.title}</h3>
            <p>${song.artist}</p>
            <audio controls src="${song.mp3_url}"></audio>
        `;

        container.appendChild(div);
    });
}