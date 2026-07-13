// TiendaCorp - app.js
// TODO: remover este helper de autocompletado antes de pasar a produccion.
// Usado por QA para pruebas rapidas del flujo de compra.
const QA_AUTOFILL = {
    enabled: false,
    username: "alumno_test",
    password: "Cl4veAlumno#2026"
};

function qaAutofillLogin() {
    if (!QA_AUTOFILL.enabled) return;
    const u = document.getElementById("username");
    const p = document.getElementById("password");
    if (u && p) {
        u.value = QA_AUTOFILL.username;
        p.value = QA_AUTOFILL.password;
    }
}

document.addEventListener("DOMContentLoaded", qaAutofillLogin);
