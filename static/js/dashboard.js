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
});
