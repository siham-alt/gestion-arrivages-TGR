// admin_stats.js

document.addEventListener('DOMContentLoaded', function() {
    console.log("[DEBUG] DOMContentLoaded event fired. Starting script execution.");

    const chartInstances = {}; // Global storage for chart instances

    // Utility function to create charts for dashboard display
    function createChart(canvasId, type, labelsData, chartData, backgroundColor, borderColor, datasets = null) {
        console.log(`[DEBUG - createChart] Attempting to create chart for ID: '${canvasId}'`);
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`[Dashboard] ERROR: Canvas element with ID '${canvasId}' not found. Cannot create chart.`);
            return null;
        }
        const chartContext = ctx.getContext('2d');

        const labels = labelsData ? (Array.isArray(labelsData) ? labelsData : labelsData.split('|').filter(l => l)) : [];
        console.log(`[DEBUG - createChart] Labels for '${canvasId}':`, labels);

        // Destroy existing chart instance to prevent memory leaks and allow re-rendering
        if (chartInstances[canvasId]) {
            console.log(`[DEBUG - createChart] Destroying old chart instance for '${canvasId}'.`);
            chartInstances[canvasId].destroy();
        }

        let chartConfig = {
            type: type,
            data: {
                labels: labels,
                datasets: datasets || [{
                    data: chartData ? chartData.split('|').filter(d => d).map(Number) : [],
                    backgroundColor: backgroundColor,
                    borderColor: borderColor,
                    borderWidth: 1,
                    fill: type === 'line' ? true : false,
                    tension: type === 'line' ? 0.4 : 0,
                    label: 'Total Arrivages'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                size: 9
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== undefined) {
                                    label += context.parsed.y;
                                } else if (context.parsed !== undefined) {
                                    label += context.parsed;
                                }
                                return label;
                            }
                        },
                        titleFont: { size: 10 },
                        bodyFont: { size: 9 }
                    }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { font: { size: 8 } } },
                    x: { ticks: { font: { size: 8 } } }
                }
            }
        };

        // Specific options for stacked bar charts
        if (type === 'bar' && datasets && datasets.length > 1) {
            chartConfig.options.scales.x = { stacked: true, ticks: { font: { size: 8 } } };
            chartConfig.options.scales.y = { stacked: true, beginAtZero: true, ticks: { font: { size: 8 } } };
            chartConfig.options.plugins.tooltip.mode = 'index';
            chartConfig.options.plugins.tooltip.intersect = false;
        }

        try {
            const newChart = new Chart(chartContext, chartConfig);
            chartInstances[canvasId] = newChart;
            console.log(`[Dashboard] SUCCESS: Chart '${canvasId}' created.`);
            return newChart;
        } catch (chartError) {
            console.error(`[Dashboard] ERROR: Failed to create Chart.js instance for '${canvasId}'.`, chartError);
            console.error("Chart config that caused error:", chartConfig);
            return null;
        }
    }

    // Default color palettes
    const defaultBarColors = [
        'rgba(75, 192, 192, 0.7)',   // Teal
        'rgba(153, 102, 255, 0.7)',  // Purple
        'rgba(255, 159, 64, 0.7)',   // Orange
        'rgba(255, 99, 132, 0.7)',   // Red
        'rgba(54, 162, 235, 0.7)',   // Blue
        'rgba(255, 206, 86, 0.7)'    // Yellow
    ];
    const defaultPieColors = [
        'rgba(255, 99, 132, 0.7)',
        'rgba(99, 181, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)'
    ];
    const defaultBorderColors = defaultPieColors.map(color => color.replace('0.7', '1'));

    // Initialize standard charts
    const chartElements = [
        { id: 'arrivagesParAnneeChart', type: 'bar', colors: [defaultBarColors[0], defaultBarColors[0].replace('0.7', '1')] },
        { id: 'arrivagesParMoisChart', type: 'line', colors: [defaultBarColors[1], defaultBarColors[1].replace('0.7', '1')] },
        { id: 'arrivagesParTypePieceChart', type: 'pie', colors: [defaultPieColors, defaultBorderColors] },
        { id: 'arrivagesParTrimestreChart', type: 'line', colors: ['rgba(255, 206, 86, 0.7)', 'rgba(255, 206, 86, 1)'] }
    ];

    chartElements.forEach(chartConfig => {
        const element = document.getElementById(chartConfig.id);
        if (element) {
            console.log(`[DEBUG] Initializing standard chart: ${chartConfig.id}`);
            createChart(chartConfig.id, chartConfig.type, element.dataset.labels, element.dataset.data, chartConfig.colors[0], chartConfig.colors[1]);
        } else {
            console.warn(`[Dashboard] WARNING: Element with ID '${chartConfig.id}' not found.`);
        }
    });

    // --- Chart: Arrivages par Poste (vs Objectif) - Stacked Bar ---
    console.log("[DEBUG] Attempting to initialize 'arrivagesParPosteChart' (stacked bar).");
    const arrivagesParPosteTargetCanvas = document.getElementById('arrivagesParPosteChart');
    const arrivagesPosteDataScript = document.getElementById('arrivages_poste_data');

    if (arrivagesParPosteTargetCanvas && arrivagesPosteDataScript) {
        console.log("[DEBUG] Found 'arrivagesParPosteChart' canvas and 'arrivages_poste_data' script tag.");
        try {
            const rawData = JSON.parse(arrivagesPosteDataScript.textContent);
            console.log("[DEBUG] Parsed rawData for poste chart:", rawData);

            if (!Array.isArray(rawData) || rawData.length === 0) {
                console.warn("[Dashboard] WARNING: 'arrivages_poste_data' is empty or not an array. No data for 'arrivagesParPosteChart'.");
                // Replace canvas with a message if no data
                if (arrivagesParPosteTargetCanvas.parentElement) {
                    arrivagesParPosteTargetCanvas.parentElement.innerHTML = '<p class="no-data-message" style="text-align: center; color: #555; margin-top: 20px;">Aucune donnée disponible pour le graphique des postes pour les filtres sélectionnés.</p>';
                }
                return;
            }

            const labels = rawData.map(item => item.type_poste);
            const totalRecus = rawData.map(item => item.total_recus);
            const remainsToReceive = rawData.map(item => item.remains_to_receive);
            const exceededTarget = rawData.map(item => item.exceeded_target);

            // Dynamic background colors for the 'Reçus' segment based on target status
            const backgroundColorsReceived = totalRecus.map((val, index) => {
                if (exceededTarget[index] > 0) {
                    return 'rgba(255, 99, 132, 0.7)'; // Red: Target exceeded
                } else if (remainsToReceive[index] === 0 && val > 0) {
                    return 'rgba(60, 179, 113, 0.7)'; // Forest Green: Target exactly met (and something was received)
                } else {
                    return 'rgba(75, 192, 192, 0.7)'; // Teal: Below target (or 0 received)
                }
            });

            // Consistent background colors for other segments
            const backgroundColorsRemains = 'rgba(200, 200, 200, 0.5)'; // Light Grey
            const backgroundColorsExceededBar = 'rgba(255, 159, 64, 0.7)'; // Orange

            const datasets = [
                {
                    label: 'Reçus',
                    data: totalRecus,
                    backgroundColor: backgroundColorsReceived,
                    borderColor: backgroundColorsReceived.map(color => color.replace('0.7', '1')),
                    borderWidth: 1
                },
                {
                    label: 'Reste à Recevoir',
                    data: remainsToReceive,
                    backgroundColor: backgroundColorsRemains,
                    borderColor: 'rgba(200, 200, 200, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Dépassement',
                    data: exceededTarget,
                    backgroundColor: backgroundColorsExceededBar,
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1
                }
            ];

            createChart('arrivagesParPosteChart', 'bar', labels, null, null, null, datasets);
            console.log(`[Dashboard] Chart 'arrivagesParPosteChart' (stacked) creation attempt finished.`);

        } catch (e) {
            console.error("Error parsing JSON for 'arrivagesParPosteChart':", e);
            console.error("Content of 'arrivages_poste_data' script tag:", arrivagesPosteDataScript ? arrivagesPosteDataScript.textContent.substring(0, 200) + '...' : 'Script tag not found or accessible.');
            if (arrivagesParPosteTargetCanvas.parentElement) {
                arrivagesParPosteTargetCanvas.parentElement.innerHTML = '<p class="error-message" style="text-align: center; color: red; margin-top: 20px;">Erreur lors du chargement des données du graphique des postes. Veuillez vérifier la console pour plus de détails.</p>';
            }
        }
    } else {
        console.warn(`[Dashboard] WARNING: Element with ID 'arrivagesParPosteChart' or 'arrivages_poste_data' not found.`);
    }

    // --- PDF Export Logic ---
    const exportPdfButton = document.getElementById('exportPdfButton');

    if (exportPdfButton) {
        exportPdfButton.addEventListener('click', async () => {
            console.log("[DEBUG] Export PDF button clicked.");
            const dashboardContent = document.getElementById('dashboardContent');

            if (!dashboardContent) {
                console.error("[Dashboard] ERROR: Dashboard content element with ID 'dashboardContent' not found for PDF export.");
                return;
            }

            // Adjust chart sizes and options for better print quality
            Object.values(chartInstances).forEach(chart => {
                if (chart) {
                    chart.options.responsive = false;
                    chart.options.maintainAspectRatio = false;

                    let targetWidth = 280;
                    let targetHeight = 180;

                    if (chart.canvas.id === 'arrivagesParPosteChart' || chart.canvas.id === 'arrivagesParTypePieceChart') {
                        targetWidth = 200;
                        targetHeight = 200;
                    }

                    chart.canvas.style.width = `${targetWidth}px`;
                    chart.canvas.style.height = `${targetHeight}px`;

                    if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                        chart.options.plugins.legend.labels.font.size = 8;
                    }
                    if (chart.options.scales) {
                        if (chart.options.scales.x && chart.options.scales.x.ticks) {
                            chart.options.scales.x.ticks.font.size = 7;
                        }
                        if (chart.options.scales.y && chart.options.scales.y.ticks) {
                            chart.options.scales.y.ticks.font.size = 7;
                        }
                    }
                    chart.update();
                    chart.resize();
                    console.log(`[DEBUG] Chart '${chart.canvas.id}' adjusted for PDF export.`);
                }
            });

            await new Promise(resolve => setTimeout(resolve, 750));

            const options = {
                margin: 10,
                filename: 'statistiques_arrivages.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: {
                    scale: 3,
                    logging: true,
                    useCORS: true,
                    allowTaint: true, // Allow images/canvases from other origins to be "tainted"
                },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };

            console.log("[DEBUG] Generating PDF...");
            html2pdf().set(options).from(dashboardContent).save().then(() => {
                console.log("[DEBUG] PDF generation complete.");
                // Restore original chart sizes and responsiveness
                Object.values(chartInstances).forEach(chart => {
                    if (chart) {
                        chart.options.responsive = true;
                        chart.options.maintainAspectRatio = true;
                        chart.canvas.style.width = '';
                        chart.canvas.style.height = '';

                        if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                            chart.options.plugins.legend.labels.font.size = 9;
                        }
                        if (chart.options.scales) {
                            if (chart.options.scales.x && chart.options.scales.x.ticks) {
                                chart.options.scales.x.ticks.font.size = 8;
                            }
                            if (chart.options.scales.y && chart.options.scales.y.ticks) {
                                chart.options.scales.y.ticks.font.size = 8;
                            }
                        }
                        chart.update();
                        chart.resize();
                    }
                });
            }).catch(error => {
                console.error("[Dashboard] ERROR generating PDF:", error);
                // Even if PDF generation fails, attempt to restore chart properties
                Object.values(chartInstances).forEach(chart => {
                    if (chart) {
                        chart.options.responsive = true;
                        chart.options.maintainAspectRatio = true;
                        chart.canvas.style.width = '';
                        chart.canvas.style.height = '';
                        if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                            chart.options.plugins.legend.labels.font.size = 9;
                        }
                        if (chart.options.scales) {
                            if (chart.options.scales.x && chart.options.scales.x.ticks) {
                                chart.options.scales.x.ticks.font.size = 8;
                            }
                            if (chart.options.scales.y && chart.options.scales.y.ticks) {
                                chart.options.scales.y.ticks.font.size = 8;
                            }
                        }
                        chart.update();
                        chart.resize();
                    }
                });
            });
        });
    } else {
        console.warn("[Dashboard] WARNING: Export PDF button with ID 'exportPdfButton' not found.");
    }
});