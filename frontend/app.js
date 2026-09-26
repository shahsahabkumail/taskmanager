const API_BASE = `http://${window.location.hostname}:5000`;

async function fetchTasks() {
  const res = await fetch(`${API_BASE}/tasks`);
  const tasks = await res.json();
  renderTasks(tasks);
}

function renderTasks(tasks) {
  const container = document.getElementById("taskList");
  if (!tasks.length) {
    container.innerHTML = `<p class="empty-state">No tasks yet. Add one!</p>`;
    return;
  }
  container.innerHTML = tasks.map(t => `
    <div class="task-card" id="card-${t.id}">
      <h3>${escapeHtml(t.title)}</h3>
      <p>${escapeHtml(t.description || "")}</p>
      <div class="task-meta">
        <span class="badge ${t.status}">${t.status}</span>
        <div class="task-actions">
          <button onclick="cycleStatus(${t.id}, '${t.status}')">Change Status</button>
          <button class="del-btn" onclick="deleteTask(${t.id})">Delete</button>
        </div>
      </div>
    </div>
  `).join("");
}

async function createTask() {
  const title = document.getElementById("taskTitle").value.trim();
  const description = document.getElementById("taskDesc").value.trim();
  const status = document.getElementById("taskStatus").value;

  if (!title) {
    alert("Title is required.");
    return;
  }

  await fetch(`${API_BASE}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description, status })
  });

  document.getElementById("taskTitle").value = "";
  document.getElementById("taskDesc").value = "";
  document.getElementById("taskStatus").value = "pending";

  fetchTasks();
}

async function deleteTask(id) {
  if (!confirm("Delete this task?")) return;
  await fetch(`${API_BASE}/tasks/${id}`, { method: "DELETE" });
  fetchTasks();
}

async function cycleStatus(id, current) {
  const cycle = { pending: "in-progress", "in-progress": "done", done: "pending" };
  const next = cycle[current];
  await fetch(`${API_BASE}/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: next })
  });
  fetchTasks();
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

document.getElementById("submitBtn").addEventListener("click", createTask);

fetchTasks();
