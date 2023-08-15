document.addEventListener("DOMContentLoaded", function() {
    // Definir variáveis para os gráficos
    let expensesByCategoriesChart;
    let incomeGrowthChart;
    let incomeVsOutcomeChart;
    let transactionsTable;
    let receivedData;
    let categoriesData
    let subcategoriesData

    // Definir cores para os gráficos
    const paletaCores = [
        '#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD',
        '#8C564B', '#E377C2', '#2C3864', '#BCBD22', '#17BECF',
        '#F6611E', '#008000', '#8B008B', '#FF00FF', '#FFD700',
        '#800000', '#00FFFF', '#00FF00', '#4B0082', '#FF4500',
        '#a37c27', '#0c0e70', '#662E54', '#3c8dbc', '#00c0ef'
    ];

    // Cores personalizadas para as categorias
    const labelColors = {
    'Não categorizado': '#999999', // Cinza
    };

    // Definir os nomes dos meses
    const months = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];

    // Definir as variáveis para armazenar o mês e ano atual
    let currentMonth;
    let currentYear;

    // Definir o mês e ano atual
    const today = new Date();
    currentMonth = today.getMonth() + 1;
    currentYear = today.getFullYear();

    // *************** NAVEGAÇÃO *************** /
    // Função para navegar para o mês atual
    function navigateToCurrentMonth() {
        const today = new Date();
        currentMonth = today.getMonth() + 1;
        currentYear = today.getFullYear();
        fetchDataAndUpdatePage();
    }
    // Função para navegar para o mês anterior
    function navigateToPreviousMonth() {
        currentMonth--;
        if (currentMonth < 1) {
            currentMonth = 12;
            currentYear--;
        }
        fetchDataAndUpdatePage();
    }

    // Função para navegar para o próximo mês
    function navigateToNextMonth() {
        currentMonth++;
        if (currentMonth > 12) {
            currentMonth = 1;
            currentYear++;
        }
        fetchDataAndUpdatePage();
    }

    // Associar eventos de clique aos botões de navegação
    document.getElementById("currentMonthBtn").addEventListener("click", navigateToCurrentMonth);
    document.getElementById("prevMonthBtn").addEventListener("click", navigateToPreviousMonth);
    document.getElementById("nextMonthBtn").addEventListener("click", navigateToNextMonth);

    fetchDataAndUpdatePage();

    // Função para atualizar o título com o mês e ano atual
    function updatePageData(receivedData) {
        const titleElement = document.getElementById("current_month_year");
        titleElement.innerText = `${months[currentMonth - 1]} ${currentYear}`;

        const rendaTotalElement = document.getElementById("rendaTotal");
        rendaTotalElement.innerText = receivedData.rendaTotal;

        const despesaTotalElement = document.getElementById("despesaTotal");
        despesaTotalElement.innerText = receivedData.despesaTotal;

        const saldoTotalElement = document.getElementById("saldoTotal");
        saldoTotalElement.innerText = receivedData.saltoTotal;

        const reservasElement = document.getElementById("reservas");
        reservasElement.innerText = receivedData.reservas;

        categoriesData = receivedData.gastosPorCategorias;
        subcategoriesData = receivedData.gastosPorSubcategorias;
    }

    // Função para atualizar a página com os dados do mês atual
    function fetchDataAndUpdatePage() {
        fetchData(currentMonth, currentYear, (receivedData) => {
            updatePageData(receivedData);
            console.log("categoriesData", categoriesData);
            console.log("subcategoriesData", subcategoriesData);

            createCharts(receivedData, categoriesData, subcategoriesData);
        });
    }

    // Function to fetch data from the server
    function fetchData(month, year, callback) {
        const url = `data/?month=${currentMonth}&year=${currentYear}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                receivedData = data;
                callback(receivedData);
            })
            .catch(error => console.error('Error fetching data:', error));
    }

    // Função para destruir o gráfico existente, se houver
    function destroyChart(chart) {
        if (chart) {
        chart.destroy();
        }
    }

    function createCharts(receivedData, categoriesData, subcategoriesData) {
        createExpensesByCategoriesChart(categoriesData, subcategoriesData);
        createIncomeGrowthChart(receivedData);
        createIncomeVsOutcomeChart(receivedData);
        createTransactionsTable(receivedData);
    }

    // Função para lidar com o clique em categorias
    function handleCategoryClick(event, elements, receivedData) {
        if (elements.length > 0) {
            const clickedLabel = elements[0]._model.label;
            const subcategoriesData = {};


            if (receivedData.gastosPorSubcategorias[clickedLabel]) {
            const subcategoriesData = receivedData.gastosPorSubcategorias[clickedLabel];
                updateSubcategoriesChart(categoriesData, subcategoriesData);
            }
        }
    }

    function createDonutChart(chartData) {
        const customColors = paletaCores.map((color, index) => {
            const label = Object.keys(chartData)[index];
            switch (label) {
                case 'Não categorizado':
                    return '#999999';
                case 'Beleza':
                    return '#C70FF7';
                case 'Casa':
                    return '#F7B50F';
                case 'Aluguel':
                    return '#F70F0F';
                case 'Judy':
                    return '#F71B70';
                case 'Lazer':
                    return '#0FF7F7';
                case 'Cartão de Crédito':
                    return '#F26E61';
                case 'Manu':
                    return '#69239E';
                default:
                    return color;
            }
        });
        donutChart = new Chart(document.getElementById('expensesByCategoriesChart'), {
            type: 'doughnut',
            data: {
                labels: Object.keys(chartData),
                datasets: [{
                    data: Object.values(chartData),
                    backgroundColor: customColors,
                }]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                legend: {
                    position: 'left',
                    align: 'start',
                    labels: {
                        padding: 10,
                    },
                },
            }
        });

        return donutChart;
    }

    function createExpensesByCategoriesChart(categoriesData, subcategoriesData) {
        // Destruir o gráfico existente, se houver
        destroyChart(expensesByCategoriesChart);

        expensesByCategoriesChart = createDonutChart(categoriesData)

        // Verificar se não existem dados e exibir a mensagem
        if (Object.keys(receivedData.gastosPorCategorias).length === 0) {
            document.getElementById('noDataMessage').style.display = 'block';
        } else {
            document.getElementById('noDataMessage').style.display = 'none';
        }

        // Adicionar evento de clique ao gráfico de categorias
        expensesByCategoriesChart.canvas.addEventListener("click", function(event) {
            const activePoints = expensesByCategoriesChart.getElementsAtEvent(event);
            if (activePoints.length > 0) {
                const clickedLabel = activePoints[0]._model.label;
                if (receivedData.gastosPorSubcategorias[clickedLabel]) {
                    handleCategoryClick(event, activePoints, receivedData);
                }
            }
        });
    }

    // Função para atualizar o gráfico para mostrar as subcategorias
    function updateSubcategoriesChart(categoriesData, subcategoriesData) {
        // Destruir o gráfico existente, se houver
        destroyChart(expensesByCategoriesChart);

        // Mostrar o botão de volta quando as subcategorias forem exibidas
        document.getElementById('backButtonContainer').style.display = 'block';

        // Adicionar evento de clique ao botão de volta para retornar ao gráfico de categorias
        document.getElementById('backButton').addEventListener('click', function() {
            createExpensesByCategoriesChart(categoriesData, subcategoriesData);
            document.getElementById('backButtonContainer').style.display = 'none'; // Esconder o botão novamente
        });

        expensesByCategoriesChart = createDonutChart(subcategoriesData);

        // Adicionar evento de clique ao gráfico de subcategorias
        expensesByCategoriesChart.canvas.addEventListener("click", function(event) {
            const activePoints = expensesByCategoriesChart.getElementsAtEvent(event);
            if (activePoints.length > 0) {
                const clickedLabel = activePoints[0]._model.label;
            }
        });
    }

    // Create and configure the "Income/Outcome Growth by Month" chart
    function createIncomeGrowthChart(receivedData) {
        // Destruir o gráfico existente, se houver
        destroyChart(incomeGrowthChart);
        incomeGrowthChart = new Chart(document.getElementById('incomeGrowthChart'), {
            type: 'bar',
            data: {
                labels: Object.keys(receivedData.income_outcome_growth_data),
                datasets: [{
                    label: 'Renda',
                    data: Object.values(receivedData.income_outcome_growth_data).map(item => item.income),
                    backgroundColor: '#a4eba4',
                    borderWidth: 1,
                    fill: false
                }, {
                    label: 'Despesa',
                    data: Object.values(receivedData.income_outcome_growth_data).map(item => item.outcome),
                    backgroundColor: '#ec5353',
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                maintainAspectRatio : false,
                responsive : true,
            }
        });
    }

    function createIncomeVsOutcomeChart(receivedData) {
        // Destruir o gráfico existente, se houver
        destroyChart(incomeVsOutcomeChart);
        incomeVsOutcomeChart = new Chart(document.getElementById('incomeVsOutcomeChart'), {
            type: 'bar',
            data: {
                labels: Object.keys(receivedData.income_outcome_growth_data),
                datasets: [{
                    label: 'Despesas',
                    data: Object.values(receivedData.income_outcome_growth_data).map(item => item.outcome),
                    backgroundColor: '#d47668',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                maintainAspectRatio : false,
                responsive : true,
            }
        });
    }

    function createTransactionsTable(receivedData) {
    if (transactionsTable) {
        transactionsTable.clear().draw();
        transactionsTable.rows.add(receivedData.transactions).draw();
    } else {
        $('#transactionsTable thead tr')
            .clone(true)
            .addClass('filters')
            .appendTo('#transactionsTable thead');
        transactionsTable = $('#transactionsTable').DataTable({
            data: receivedData.transactions,
            columns: [
                { data: 'data' },
                { data: 'tipo'},
                { data: 'descricao' },
                { data: 'categoria' },
                { data: 'subcategoria' },
                { data: 'valor' },
            ],
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json',
            },
            paging: true,
            info: true,
            responsive: true,
            autoWidth: false,
            order: [[0, 'desc']],
            pageLength: 5,
            lengthMenu: [5, 10, 20, 50, 100],
            orderCellsTop: true,
            fixedHeader: true,
            initComplete: function () {
                var api = this.api();

                // For each column
                api
                    .columns()
                    .eq(0)
                    .each(function (colIdx) {
                        // Set the header cell to contain the input element
                        var cell = $('.filters th').eq(
                            $(api.column(colIdx).header()).index()
                        );
                        var title = $(cell).text();
                        $(cell).html('<input type="text" placeholder="' + title + '" />');

                        // On every keypress in this input
                        $(
                            'input',
                            $('.filters th').eq($(api.column(colIdx).header()).index())
                        )
                            .off('keyup change')
                            .on('change', function (e) {
                                // Get the search value
                                $(this).attr('title', $(this).val());
                                var regexr = '({search})'; //$(this).parents('th').find('select').val();

                                var cursorPosition = this.selectionStart;
                                // Search the column for that value
                                api
                                    .column(colIdx)
                                    .search(
                                        this.value != ''
                                            ? regexr.replace('{search}', '(((' + this.value + ')))')
                                            : '',
                                        this.value != '',
                                        this.value == ''
                                    )
                                    .draw();
                            })
                            .on('keyup', function (e) {
                                e.stopPropagation();

                                $(this).trigger('change');
                                $(this)
                                    .focus()[0]
                                    .setSelectionRange(cursorPosition, cursorPosition);
                            });
                    });
            },
            columnDefs: [
                {
                    targets: 0,
                    render: function (receivedData, type, row) {
                        return moment(receivedData).format('DD/MM/YYYY');
                    }
                },
                {
                    targets: 5,
                    render: function (receivedData, type, row) {
                        return 'R$ ' + receivedData.toFixed(2).replace('.', ',');
                    }
                }
            ],
            rowCallback: function (row, receivedData) {
                if (receivedData.tipo === 'S') {
                    $(row).addClass('bg-light-red');
                } else if (receivedData.tipo === 'E') {
                    $(row).addClass('bg-light-green'); // Transação de entrada
                }
            }
        });

        transactionsTable.rows.add(receivedData.transactions).draw();
    }
}

    // Function to initialize the charts with the data
    function initializeCharts() {
        // Definir um valor inicial para o mês e ano
        const today = new Date();
        currentMonth = today.getMonth() + 1;
        currentYear = today.getFullYear();


        fetchData(currentMonth, currentYear, (receivedData) => {
            updatePageData(receivedData);
        });
    }

    // Call initializeCharts to load the charts with the data from the server
    initializeCharts();
});

$(function () {
  'use strict'

  // Make the dashboard widgets sortable Using jquery UI
  $('.connectedSortable').sortable({
    placeholder: 'sort-highlight',
    connectWith: '.connectedSortable',
    handle: '.card-header, .nav-tabs',
    forcePlaceholderSize: true,
    zIndex: 999999
  })
  $('.connectedSortable .card-header').css('cursor', 'move')

})