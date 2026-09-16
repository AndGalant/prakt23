/* =========================================================
   Расписание: рендер, Drag & Drop, модальное окно
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
        // Определяем, в какую ячейку положить карточку:
        // приоритет — 1-я неделя, если её нет — 2-я.
        const week1 = l.week1_lesson;
        const week2 = l.week2_lesson;
        if (!week1 && !week2) return;

        const targetPair = week1 || week2;

        const td = document.querySelector(
            `.slot[data-group="${l.group_id}"][data-day="${l.day}"][data-pair="${targetPair}"]`
        );
        if (!td) return;

        td.appendChild(buildCard(l));
    });
}

/* ---------- Построение карточки ---------- */
function buildCard(l) {
    const card = document.createElement("div");
    card.className = "lesson-card";
    card.style.setProperty("--teacher-color", l.teacher_color);
    card.dataset.id = l.id;
    card.draggable = true;

    const week1 = l.week1_lesson ? `1 нед → ${l.week1_lesson} пара` : "1 нед → —";
    const week2 = l.week2_lesson ? `2 нед → ${l.week2_lesson} пара` : "2 нед → —";

    card.innerHTML = `
        <div class="lesson-teacher">
            <span class="lesson-short">${l.teacher_short}</span>
            <span class="lesson-fio">${l.teacher_name}</span>
        </div>
        <div class="lesson-subject">${l.subject_name}</div>
        <div class="lesson-weeks">${week1}<br>${week2}</div>
        <div class="lesson-room">каб. ${l.classroom_name} • ${l.lesson_type}</div>
    `;
    return card;
}

/* ---------- Drag & Drop ---------- */
document.addEventListener("dragstart", e => {
    // Из панели преподавателей
    const li = e.target.closest(".subject-list li");
    if (li) {
        e.dataTransfer.setData("application/json", JSON.stringify({
            type: "new",
            teacher_id: li.dataset.teacher,
            subject_id: li.dataset.subject,
        }));
        return;
    }
    // Из уже существующей карточки
    const card = e.target.closest(".lesson-card");
    if (card) {
        e.dataTransfer.setData("application/json", JSON.stringify({
            type: "move",
            id: card.dataset.id,
        }));
    }
});

document.querySelectorAll(".slot").forEach(td => {
    td.addEventListener("dragover", e => e.preventDefault());

    td.addEventListener("drop", async e => {
        e.preventDefault();
        const data = JSON.parse(e.dataTransfer.getData("application/json"));
        const groupId = parseInt(td.dataset.group);
        const day = td.dataset.day;
        const pair = parseInt(td.dataset.pair);

        if (data.type === "new") {
            await fetch("/lessons", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    group_id: groupId,
                    teacher_id: data.teacher_id,
                    subject_id: data.subject_id,
                    day: day,
                    week1_lesson: pair,
                    week2_lesson: null,
                }),
            });
            await loadLessons();
        } else if (data.type === "move") {
            await fetch(`/lessons/${data.id}`, {
                method: "PUT",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    group_id: groupId,
                    day: day,
                    week1_lesson: pair,
                    week2_lesson: null,
                }),
            });
            await loadLessons();
        }
    });
});

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
    const payload = {
        group_id: parseInt(document.getElementById("group_id").value),
        day: document.getElementById("day").value,
        teacher_id: parseInt(document.getElementById("teacher_id").value),
        subject_id: parseInt(document.getElementById("subject_id").value),
        week1_lesson: document.getElementById("week1_lesson").value || null,
        week2_lesson: document.getElementById("week2_lesson").value || null,
        classroom_id: document.getElementById("classroom_id").value || null,
        lesson_type: document.getElementById("lesson_type").value,
    };

    if (state.editingId) {
        await fetch(`/lessons/${state.editingId}`, {
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload),
        });
    } else {
        await fetch("/lessons", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload),
        });
    }

    closeModal();
    await loadLessons();
});

deleteBtn.addEventListener("click", async () => {
    if (!state.editingId) return;
    if (!confirm("Удалить занятие?")) return;
    await fetch(`/lessons/${state.editingId}`, {method: "DELETE"});
    closeModal();
    await loadLessons();
});

/* ---------- Клик по карточке → редактирование ---------- */
document.addEventListener("click", e => {
    const card = e.target.closest(".lesson-card");
    if (!card) return;
    const lesson = state.lessons.find(l => l.id === parseInt(card.dataset.id));
    if (lesson) openModal(lesson);
});

/* ---------- Старт ---------- */
loadLessons();