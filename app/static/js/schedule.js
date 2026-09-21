/* =========================================================
   Расписание: рендер, Drag & Drop, конфликты, модалка
   ========================================================= */

const state = {
    lessons: [],
    editingId: null,
};

/* ---------- Загрузка занятий ---------- */
async function loadLessons() {
    const res = await fetch("/api/schedule");
    state.lessons = await res.json();
    renderSchedule();
}

/* ---------- Рендер карточек ---------- */
function renderSchedule() {
    document.querySelectorAll(".slot").forEach(td => td.innerHTML = "");

    state.lessons.forEach(l => {
        const week1 = l.week1_lesson;
        const week2 = l.week2_lesson;
        if (!week1 && !week2) return;

        if (week1) placeCard(l, week1);
        if (week2) placeCard(l, week2);
    });
}

function placeCard(l, pair) {
    const td = document.querySelector(
        `.slot[data-group="${l.group_id}"][data-day="${l.day}"][data-pair="${pair}"]`
    );
    if (!td) return;
    td.appendChild(buildCard(l, pair));
}

function buildCard(l, pair) {
    const card = document.createElement("div");
    card.className = "lesson-card";
    card.style.setProperty("--teacher-color", l.teacher_color);
    card.dataset.id = l.id;
    card.dataset.pair = pair;
    card.draggable = true;

    const w1 = l.week1_lesson ? `1 нед → ${l.week1_lesson} пара` : "1 нед → —";
    const w2 = l.week2_lesson ? `2 нед → ${l.week2_lesson} пара` : "2 нед → —";

    card.innerHTML = `
        <div class="lesson-teacher">
            <span class="lesson-short">${l.teacher_short}</span>
            <span class="lesson-fio">${l.teacher_name}</span>
        </div>
        <div class="lesson-subject">${l.subject_name}</div>
        <div class="lesson-weeks">${w1}<br>${w2}</div>
        <div class="lesson-room">каб. ${l.classroom_name} • ${l.lesson_type}</div>
    `;
    return card;
}

/* ---------- Drag & Drop ---------- */
document.addEventListener("dragstart", e => {
    const li = e.target.closest(".subject-list li");
    if (li) {
        e.dataTransfer.setData("application/json", JSON.stringify({
            type: "new",
            teacher_id: li.dataset.teacher,
            subject_id: li.dataset.subject,
        }));
        return;
    }
    const card = e.target.closest(".lesson-card");
    if (card) {
        const lesson = state.lessons.find(l => l.id === parseInt(card.dataset.id));
        e.dataTransfer.setData("application/json", JSON.stringify({
            type: "move",
            id: card.dataset.id,
            fromPair: parseInt(card.dataset.pair),
            week1_lesson: lesson ? lesson.week1_lesson : null,
            week2_lesson: lesson ? lesson.week2_lesson : null,
        }));
    }
});

document.querySelectorAll(".slot").forEach(td => {
    td.addEventListener("dragover", e => {
        e.preventDefault();
        td.classList.add("drag-over");
    });
    td.addEventListener("dragleave", () => td.classList.remove("drag-over"));

    td.addEventListener("drop", async e => {
        e.preventDefault();
        td.classList.remove("drag-over");

        const data = JSON.parse(e.dataTransfer.getData("application/json"));
        const groupId = parseInt(td.dataset.group);
        const day = td.dataset.day;
        const pair = parseInt(td.dataset.pair);

        let payload, url, method;

        if (data.type === "new") {
            payload = {
                group_id: groupId,
                teacher_id: parseInt(data.teacher_id),
                subject_id: parseInt(data.subject_id),
                day: day,
                week1_lesson: pair,
                week2_lesson: null,
            };
            url = "/lessons";
            method = "POST";
        } else if (data.type === "move") {
            const wasWeek1 = data.week1_lesson === data.fromPair;
            payload = {
                group_id: groupId,
                day: day,
                week1_lesson: wasWeek1 ? pair : null,
                week2_lesson: wasWeek1 ? null : pair,
            };
            url = `/lessons/${data.id}`;
            method = "PUT";
        } else {
            return;
        }

        const res = await fetch(url, {
            method: method,
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload),
        });

        // Безопасный разбор ответа — сервер может вернуть пустое тело
        let body = null;
        try {
            const text = await res.text();
            body = text ? JSON.parse(text) : null;
        } catch (err) {
            body = null;
        }

        if (res.status === 409) {
            const conflicts = (body && body.conflicts && body.conflicts.length)
                ? body.conflicts
                : [{message: "Конфликт расписания (подробности недоступны)"}];
            showConflicts(conflicts);
            return;
        }
        if (res.status === 400) {
            showError(body && body.error ? body.error : "Ошибка запроса");
            return;
        }
        if (!res.ok) {
            showError("Не удалось сохранить занятие");
            return;
        }
        await loadLessons();
    });
});

/* ---------- Уведомления ---------- */
function showConflicts(conflicts) {
    let text = "⚠ Обнаружены конфликты:\n\n";
    conflicts.forEach(c => {
        text += "• " + (c.message || "Неизвестный конфликт") + "\n";
    });
    alert(text);
}

function showError(msg) {
    alert("Ошибка: " + msg);
}

/* ---------- Модальное окно ---------- */
const modal = document.getElementById("lessonModal");
const form = document.getElementById("lessonForm");
const modalTitle = document.getElementById("modalTitle");
const saveBtn = document.getElementById("saveBtn");
const deleteBtn = document.getElementById("deleteBtn");

function openModal(lesson = null) {
    modal.hidden = false;

    if (lesson) {
        state.editingId = lesson.id;
        modalTitle.textContent = "Редактирование занятия";
        saveBtn.textContent = "Сохранить";
        deleteBtn.hidden = false;

        document.getElementById("group_id").value = lesson.group_id;
        document.getElementById("day").value = lesson.day;
        document.getElementById("teacher_id").value = lesson.teacher_id;
        fillSubjects(lesson.teacher_id, lesson.subject_id);
        document.getElementById("week1_lesson").value = lesson.week1_lesson || "";
        document.getElementById("week2_lesson").value = lesson.week2_lesson || "";
        document.getElementById("classroom_id").value = lesson.classroom_id || "";
        document.getElementById("lesson_type").value = lesson.lesson_type;
    } else {
        state.editingId = null;
        modalTitle.textContent = "Добавление занятия";
        saveBtn.textContent = "Добавить";
        deleteBtn.hidden = true;
        form.reset();
        fillSubjects(document.getElementById("teacher_id").value);
    }
}

function closeModal() {
    modal.hidden = true;
}

async function fillSubjects(teacherId, selectedId = null) {
    const sel = document.getElementById("subject_id");
    sel.innerHTML = "";
    const res = await fetch(`/teachers/${teacherId}/subjects`);
    const subjects = await res.json();
    subjects.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = s.name;
        if (selectedId && parseInt(selectedId) === s.id) opt.selected = true;
        sel.appendChild(opt);
    });
}

document.getElementById("teacher_id").addEventListener("change", e => {
    fillSubjects(e.target.value);
});

document.getElementById("addLessonBtn").addEventListener("click", () => openModal());
document.getElementById("cancelBtn").addEventListener("click", closeModal);

form.addEventListener("submit", async e => {
    e.preventDefault();

    const week1 = document.getElementById("week1_lesson").value || null;
    const week2 = document.getElementById("week2_lesson").value || null;
    if (!week1 && !week2) {
        showError("Нужно указать пару хотя бы на одной неделе");
        return;
    }

    const payload = {
        group_id: parseInt(document.getElementById("group_id").value),
        day: document.getElementById("day").value,
        teacher_id: parseInt(document.getElementById("teacher_id").value),
        subject_id: parseInt(document.getElementById("subject_id").value),
        week1_lesson: week1,
        week2_lesson: week2,
        classroom_id: document.getElementById("classroom_id").value || null,
        lesson_type: document.getElementById("lesson_type").value,
    };

    const url = state.editingId ? `/lessons/${state.editingId}` : "/lessons";
    const method = state.editingId ? "PUT" : "POST";

    const res = await fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload),
    });

    // Безопасный разбор ответа
    let body = null;
    try {
        const text = await res.text();
        body = text ? JSON.parse(text) : null;
    } catch (err) {
        body = null;
    }

    if (res.status === 409) {
        const conflicts = (body && body.conflicts && body.conflicts.length)
            ? body.conflicts
            : [{message: "Конфликт расписания (подробности недоступны)"}];
        showConflicts(conflicts);
        return;
    }
    if (res.status === 400) {
        showError(body && body.error ? body.error : "Ошибка запроса");
        return;
    }
    if (!res.ok) {
        showError("Не удалось сохранить занятие");
        return;
    }

    closeModal();
    await loadLessons();
});

deleteBtn.addEventListener("click", async () => {
    if (!state.editingId) return;
    if (!confirm("Удалить занятие?")) return;

    const res = await fetch(`/lessons/${state.editingId}`, {method: "DELETE"});

    if (!res.ok) {
        let body = null;
        try {
            const text = await res.text();
            body = text ? JSON.parse(text) : null;
        } catch (err) {
            body = null;
        }
        showError(body && body.error ? body.error : "Не удалось удалить занятие");
        return;
    }

    closeModal();
    await loadLessons();
});

document.addEventListener("click", e => {
    const card = e.target.closest(".lesson-card");
    if (!card) return;
    const lesson = state.lessons.find(l => l.id === parseInt(card.dataset.id));
    if (lesson) openModal(lesson);
});

/* ---------- Старт ---------- */
loadLessons();