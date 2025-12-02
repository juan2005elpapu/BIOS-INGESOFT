document.addEventListener("DOMContentLoaded", function () {
    const dataElement = document.getElementById("charts-data");
    if (!dataElement) return;

    let chartsData;
    try {
        chartsData = JSON.parse(dataElement.textContent);
    } catch (e) {
        console.error("Error parsing charts data:", e);
        return;
    }

    const colors = {
        primary: "rgba(34, 197, 94, 0.8)",
        primaryLight: "rgba(34, 197, 94, 0.2)",
        secondary: "rgba(59, 130, 246, 0.8)",
        secondaryLight: "rgba(59, 130, 246, 0.2)",
        palette: [
            "rgba(34, 197, 94, 0.8)",
            "rgba(59, 130, 246, 0.8)",
            "rgba(168, 85, 247, 0.8)",
            "rgba(249, 115, 22, 0.8)",
            "rgba(236, 72, 153, 0.8)",
            "rgba(20, 184, 166, 0.8)",
            "rgba(245, 158, 11, 0.8)",
            "rgba(99, 102, 241, 0.8)",
        ],
    };

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: "rgba(148, 163, 184, 1)",
                    font: { size: 12 },
                },
            },
        },
    };

    const gridColor = "rgba(51, 65, 85, 0.5)";
    const textColor = "rgba(148, 163, 184, 1)";

    function createBarChart(canvasId, data, label) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !data || !data.labels || data.labels.length === 0) return;

        new Chart(canvas, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{
                    label: label,
                    data: data.values,
                    backgroundColor: colors.primary,
                    borderColor: colors.primary,
                    borderWidth: 1,
                    borderRadius: 6,
                }],
            },
            options: {
                ...defaultOptions,
                scales: {
                    x: {
                        ticks: { color: textColor },
                        grid: { color: gridColor },
                    },
                    y: {
                        ticks: { color: textColor },
                        grid: { color: gridColor },
                        beginAtZero: true,
                    },
                },
            },
        });
    }

    function createDoughnutChart(canvasId, data, label) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !data || !data.labels || data.labels.length === 0) return;

        new Chart(canvas, {
            type: "doughnut",
            data: {
                labels: data.labels,
                datasets: [{
                    label: label,
                    data: data.values,
                    backgroundColor: colors.palette.slice(0, data.labels.length),
                    borderColor: "rgba(15, 23, 42, 1)",
                    borderWidth: 2,
                }],
            },
            options: {
                ...defaultOptions,
                cutout: "60%",
            },
        });
    }

    function createPieChart(canvasId, data, label) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !data || !data.labels || data.labels.length === 0) return;

        new Chart(canvas, {
            type: "pie",
            data: {
                labels: data.labels,
                datasets: [{
                    label: label,
                    data: data.values,
                    backgroundColor: colors.palette.slice(0, data.labels.length),
                    borderColor: "rgba(15, 23, 42, 1)",
                    borderWidth: 2,
                }],
            },
            options: defaultOptions,
        });
    }

    function createLineChart(canvasId, data, label) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !data || !data.labels || data.labels.length === 0) return;

        new Chart(canvas, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{
                    label: label,
                    data: data.values,
                    borderColor: colors.primary,
                    backgroundColor: colors.primaryLight,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: colors.primary,
                }],
            },
            options: {
                ...defaultOptions,
                scales: {
                    x: {
                        ticks: { color: textColor },
                        grid: { color: gridColor },
                    },
                    y: {
                        ticks: { color: textColor },
                        grid: { color: gridColor },
                        beginAtZero: true,
                    },
                },
            },
        });
    }

    // Gráficas de Lotes y Animales
    if (chartsData.por_lote) {
        createBarChart("chart-por-lote", chartsData.por_lote, "Animales");
    }
    if (chartsData.por_especie) {
        createDoughnutChart("chart-por-especie", chartsData.por_especie, "Animales");
    }
    if (chartsData.por_sexo) {
        createPieChart("chart-por-sexo", chartsData.por_sexo, "Animales");
    }

    // Gráficas de Tracking
    if (chartsData.pesos_mensuales) {
        createLineChart("chart-pesos-mensuales", chartsData.pesos_mensuales, "Peso promedio (kg)");
    }
    if (chartsData.producciones_mensuales) {
        createBarChart("chart-producciones-mensuales", chartsData.producciones_mensuales, "Producción");
    }

    // Gráficas de Costos
    if (chartsData.por_tipo) {
        createDoughnutChart("chart-por-tipo", chartsData.por_tipo, "Gastos");
    }
    if (chartsData.por_lote) {
        createBarChart("chart-por-lote-costos", chartsData.por_lote, "Gastos");
    }
    if (chartsData.mensual) {
        createLineChart("chart-mensual", chartsData.mensual, "Gasto mensual ($)");
    }
});