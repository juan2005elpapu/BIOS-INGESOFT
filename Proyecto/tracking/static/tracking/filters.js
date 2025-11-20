document.addEventListener("DOMContentLoaded", () => {
    const dataNode = document.getElementById("tracking-animals-data");
    if (!dataNode) {
        return;
    }

    let animals = [];
    try {
        animals = JSON.parse(dataNode.textContent);
    } catch {
        return;
    }

    const forms = document.querySelectorAll("[data-tracking-filter-form]");
    forms.forEach((form) => {
        const lotSelect = form.querySelector("[data-filter-lot]");
        const animalSelect = form.querySelector("[data-filter-animal]");
        if (!lotSelect || !animalSelect) {
            return;
        }

        const renderOptions = () => {
            const selectedBatch = lotSelect.value;
            const persisted = animalSelect.dataset.selected || "";
            animalSelect.innerHTML = "";

            if (!selectedBatch) {
                const placeholder = document.createElement("option");
                placeholder.value = "";
                placeholder.textContent = "Selecciona un lote primero";
                animalSelect.appendChild(placeholder);
                animalSelect.disabled = true;
                animalSelect.value = "";
                return;
            }

            const defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = "Todos los animales";
            animalSelect.appendChild(defaultOption);

            animals
                .filter((animal) => String(animal.batch) === selectedBatch)
                .forEach((animal) => {
                    const option = document.createElement("option");
                    option.value = String(animal.id);
                    option.textContent = animal.label;
                    animalSelect.appendChild(option);
                });

            animalSelect.disabled = false;
            if (persisted && animalSelect.querySelector(`option[value="${persisted}"]`)) {
                animalSelect.value = persisted;
            } else {
                animalSelect.value = "";
            }
        };

        renderOptions();

        lotSelect.addEventListener("change", () => {
            animalSelect.dataset.selected = "";
            renderOptions();
        });

        animalSelect.addEventListener("change", () => {
            animalSelect.dataset.selected = animalSelect.value;
        });
    });
});