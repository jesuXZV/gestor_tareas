document.addEventListener("DOMContentLoaded", function () {
  const toggleButton = document.getElementById("btn-toggle-sidebar");
  const sidebar = document.getElementById("sidebar");

  if (toggleButton && sidebar) {
    toggleButton.addEventListener("click", function () {
      sidebar.classList.toggle("collapsed");
    });
  }

  const btnPlanificacion = document.getElementById("btn-planificacion");
  const seccionPlanificacion = document.getElementById("contenido-planificacion");

  if (btnPlanificacion && seccionPlanificacion) {
    btnPlanificacion.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelectorAll("main").forEach(section => {
        section.style.display = "none";
      });
      seccionPlanificacion.style.display = "block";
    });
  }

  const formPerfil = document.getElementById("formPerfil");
  if (formPerfil) {
    formPerfil.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(formPerfil);
      fetch("/perfil", {
        method: "POST",
        body: formData,
      })
        .then(res => res.ok ? res.text() : Promise.reject("Error al actualizar perfil."))
        .then(() => {
          document.getElementById("mensajePerfil").textContent = "¡Perfil actualizado!";
          setTimeout(() => {
            document.getElementById("mensajePerfil").textContent = "";
            location.reload();
          }, 1500);
        })
        .catch(err => {
          document.getElementById("mensajePerfil").textContent = err.message;
        });
    });

    const avatarInput = document.querySelector('input[name="avatar"]');
    if (avatarInput) {
      avatarInput.addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = function (e) {
            document.getElementById("previewAvatar").src = e.target.result;
          };
          reader.readAsDataURL(file);
        }
      });
    }
  }

  const formAjustes = document.getElementById("formAjustes");
  if (formAjustes) {
    formAjustes.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(formAjustes);
      const temaSeleccionado = formData.get("tema");
      const idiomaSeleccionado = formData.get("idioma");

      fetch("/ajustes", {
        method: "POST",
        body: formData
      })
        .then(res => res.ok ? res.text() : Promise.reject("Error al guardar ajustes."))
        .then(() => {
          const mensaje = idiomaSeleccionado === "en" ? "Settings saved!" : "¡Ajustes guardados!";
          document.getElementById("mensajeAjustes").textContent = mensaje;

          if (temaSeleccionado === "oscuro") {
            document.body.classList.add("tema-oscuro");
          } else {
            document.body.classList.remove("tema-oscuro");
          }

          aplicarTraduccionGeneral(idiomaSeleccionado);

          const modal = bootstrap.Modal.getInstance(document.getElementById('ajustesModal'));
          modal.hide();
        })
        .catch(err => {
          document.getElementById("mensajeAjustes").textContent = err;
        });
    });
  }

  fetch("/mis-ajustes")
    .then(res => res.json())
    .then(data => {
      if (data.tema === "oscuro") {
        document.body.classList.add("tema-oscuro");
      }
      aplicarTraduccionGeneral(data.idioma || "es");
    });
});

function aplicarTraduccionGeneral(idioma) {
  const traducciones = {
    en: {
      ajustesModalLabel: "Account Settings",
      labelTema: "Theme",
      labelIdioma: "Language",
      labelNotificaciones: "Receive email notifications",
      btnCancelar: "Cancel",
      btnGuardar: "Save changes",
      navPlanificacion: "Planning",
      navCalendario: "Calendar",
      mensajeAjustes: "Settings saved!",
      // Sidebar
      tituloSidebar: "Task",
      linkProfesores: "My teachers",
      linkProyectos: "Projects",
      linkTareas: "Tasks"
    },
    es: {
      ajustesModalLabel: "Ajustes de cuenta",
      labelTema: "Tema",
      labelIdioma: "Idioma",
      labelNotificaciones: "Recibir notificaciones por correo",
      btnCancelar: "Cancelar",
      btnGuardar: "Guardar cambios",
      navPlanificacion: "Planificación",
      navCalendario: "Calendario",
      mensajeAjustes: "¡Ajustes guardados!",
      // Sidebar
      tituloSidebar: "Tarea",
      linkProfesores: "Mis profesores",
      linkProyectos: "Proyectos",
      linkTareas: "Tareas"
    }
  };

  const t = traducciones[idioma];
  if (!t) return;

  const ids = [
    "ajustesModalLabel",
    "labelTema",
    "labelIdioma",
    "labelNotificaciones",
    "btnCancelar",
    "btnGuardar",
    "navPlanificacion",
    "navCalendario",
    "tituloSidebar",
    "linkProfesores",
    "linkProyectos",
    "linkTareas"
  ];

  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerText = t[id];
  });

  const mensaje = document.getElementById("mensajeAjustes");
  if (mensaje && mensaje.textContent) {
    mensaje.textContent = t["mensajeAjustes"];
  }
}
