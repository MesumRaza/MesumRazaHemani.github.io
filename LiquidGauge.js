'use strict';

// Wrap everything in an anonymous function to avoid polluting the global namespace
(function() {
    let unregisterHandlerFunctions = [];
    // Use the jQuery document ready signal to know when everything has been initialized
    $(document).ready(function() {
        // Tell Tableau we'd like to initialize our extension
        tableau.extensions.initializeAsync({
            'configure': configure
        }).then(function() {
            fetchFilters();
            const worksheetName = tableau.extensions.settings.get('selWorksheet');
            if (worksheetName) {
                loadSummaryData(worksheetName);
            } else {
                $('#user_prompts_title').text("Configure Extension...");
            }
        });
    });

    function configure() {
        showChooseSheetDialog();
        fetchFilters();
    }

    /**
     * Shows the choose sheet UI. Once a sheet is selected, the data table for the sheet is shown
     */
    function showChooseSheetDialog() {
        // Clear out the existing list of sheets
        $('#choose_sheet_buttons').empty();

        // Set the dashboard's name in the title
        const dashboardName = tableau.extensions.dashboardContent.dashboard.name;
        $('#choose_sheet_title').text(dashboardName);

        // The first step in choosing a sheet will be asking Tableau what sheets are available
        const worksheets = tableau.extensions.dashboardContent.dashboard.worksheets;

        // Next, we loop through all of these worksheets add add buttons for each one
        worksheets.forEach(function(worksheet) {
            // Declare our new button which contains the sheet name
            const button = createButton(worksheet.name);

            // Create an event handler for when this button is clicked
            button.click(function() {
                // Get the worksheet name which was selected and store setting
                const worksheetName = worksheet.name;
                tableau.extensions.settings.set('selWorksheet', worksheetName);

                // Close the dialog and show the data table for this worksheet
                tableau.extensions.settings.saveAsync().then((newSavedSettings) => {
                    $('#choose_sheet_dialog').modal('toggle');
                    loadSummaryData(worksheetName);
                });
            });

            // Add our button to the list of worksheets to choose from
            $('#choose_sheet_buttons').append(button);
        });

        // Show the dialog
        $('#choose_sheet_dialog').modal('toggle');
    }

    function createButton(buttonTitle) {
        const button =
            $(`<button type='button' class='btn btn-default btn-block'>
      ${buttonTitle}
    </button>`);

        return button;
    }

    function loadSummaryData(worksheetName) {
        // Get the worksheet object we want to get the selected marks for
        const worksheet = getSelectedSheet(worksheetName);

        // Set our title to an appropriate value
        $('#user_prompts').remove();
        //$('#show_choose_sheet_button').remove();

        // Call to get the summaryData for our sheet
        worksheet.getSummaryDataAsync().then(function(SummaryData) {
            // Get the first DataTable for our selected marks (usually there is just one)
            //const worksheetData = marks.data[0];

            // Populate the data table with the rows and columns we just pulled out
            //populateDataTable(data, columns);
            populateLiquidGauge(SummaryData);
        });
    }

    function populateLiquidGauge(SummaryData) {
        // Do some UI setup here to change the visible section and reinitialize the table
        $('#fillgauge').empty();

        if (SummaryData.data.length > 0) {

            var value = SummaryData.data[0][0].value //get meaure value from Summary Data
            var config = liquidFillGaugeDefaultSettings();
            config.circleThickness = 0.15;
            config.circleColor = "#c71414";
            config.textColor = "#c71414";
            config.waveTextColor = "#00ffff";
            config.waveColor = "#6388b4";
            config.textVertPosition = 0.5;
            config.waveAnimateTime = 1000;
            config.waveHeight = 0.05;
            config.waveAnimate = true;
            config.waveRise = true;
            config.waveHeightScaling = false;
            config.waveOffset = 0.25;
            config.textSize = 0.75;
            config.waveCount = 3;
            var gauge = loadLiquidFillGauge("fillgauge", value * 100, config);


        } else {
            // If we didn't get any rows back, there must be no marks selected
            $('#no_data_message').css('display', 'inline');
        }
    }

    function NewValue() {
        if (Math.random() > .5) {
            return Math.round(Math.random() * 100);
        } else {
            return (Math.random() * 100).toFixed(1);
        }
    }

    // This is a handling function that is called anytime a filter is changed in Tableau.
    function filterChangedHandler(filterEvent) {
        // Just reconstruct the filters table whenever a filter changes.
        // This could be optimized to add/remove only the different filters.
        //fetchFilters();
        //reload gauge
        const worksheetName = tableau.extensions.settings.get('selWorksheet');
        loadSummaryData(worksheetName);
    }

    function fetchFilters() {
        // While performing async task, show loading message to user.
        $('#loading').addClass('show');

        // Whenever we restore the filters table, remove all save handling functions,
        // since we add them back later in this function.
        unregisterHandlerFunctions.forEach(function(unregisterHandlerFunction) {
            unregisterHandlerFunction();
        });

        // Since filter info is attached to the worksheet, we will perform
        // one async call per worksheet to get every filter used in this
        // dashboard.  This demonstrates the use of Promise.all to combine
        // promises together and wait for each of them to resolve.
        let filterFetchPromises = [];

        // List of all filters in a dashboard.
        let dashboardfilters = [];

        // To get filter info, first get the dashboard.
        const dashboard = tableau.extensions.dashboardContent.dashboard;

        // Then loop through each worksheet and get its filters, save promise for later.
        dashboard.worksheets.forEach(function(worksheet) {
            filterFetchPromises.push(worksheet.getFiltersAsync());

            // Add filter event to each worksheet.  AddEventListener returns a function that will
            // remove the event listener when called.
            let unregisterHandlerFunction = worksheet.addEventListener(tableau.TableauEventType.FilterChanged, filterChangedHandler);
            unregisterHandlerFunctions.push(unregisterHandlerFunction);
        });
    }

    function getSelectedSheet(worksheetName) {
        // Go through all the worksheets in the dashboard and find the one we want
        return tableau.extensions.dashboardContent.dashboard.worksheets.find(function(sheet) {
            return sheet.name === worksheetName;
        });
    }
})();
