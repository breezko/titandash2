/**
 * statistics.js
 */
$(document).ready(function() {
    let elements = {
        statisticsTableLoader: $(".statisticsTableLoader"),
        statisticsSelectorContainer: $("#statisticsInstanceSelectorContainer"),
        statisticsSelectorSelect: $("#statisticsInstanceSelectorSelect"),
        statisticsContent: $("#statisticsContent"),
        statisticsTableContainer: $("#statisticsTableContainer")
    };

    function buildTable(instance) {
        // Build the actual statistics table.
        // Ensuring we empty the table before anything.
        elements.statisticsTableContainer.empty();

        // Begin building the first table, this one should contain
        // all information about the current game statistics parsed.
        let html = `
            <h6 class="font-weight-bold">Game Statistics</h6>
            <table id="statisticsTableOne" class="table-titan-stats table table-sm table-hover">
                <tbody>
        `;
        $.each(instance.statistics.game_statistics, function(key, value) {
            html += `
                <tr>
                    <td>${formatString(key)}</td>
                    <td><strong>${value || "N/A"}</strong></td>
                </tr>
            `;
        });
        // Close up and finish populating our first table of information.
        html += "</tbody></table>";

        // Begin building the second table, this one should contain all
        // generic bot statistics data.
        html += `
            <h6 class="font-weight-bold">Bot Statistics (Generic)</h6>
            <table id="statisticsTableTwo" class="table-titan-stats table table-sm table-hover">
                <tbody>        
        `;
        $.each(instance.statistics.bot_statistics.generic, function(key, value) {
            html += `
                <tr>
                    <td>${formatString(key)}</td>
                    <td><strong>${value}</strong></td>
                </tr>
            `;
        });
        // Close up and finish populating our second table of information.
        html += "</tbody></table>";

        // Begin building the third table, this one should contain
        // all information about the functions executed by the bot.
        html += `
            <hr/>
            <h6 class="font-weight-bold">Bot Statistics (Functions)</h6>
            <table id="statisticsTableThree" class="table-titan-stats table table-sm table-hover">
                <tbody>
        `;
        $.each(instance.statistics.bot_statistics.functions, function(key, value) {
            html += `
                <tr>
                    <td>${formatString(key)}</td>
                    <td><strong>${value}</strong></td>
                </tr>
            `;
        });
        // Close up and finish populating our second table of information.
        html += "</tbody></table>";

        // Add dynamic content to the statistics table now.
        elements.statisticsTableContainer.append(html);
    }

    async function reloadStatisticsTable(instance, hideAndShow) {
        // Reload the statistics table (or just load). Based on whether or not
        // we are initializing or selecting a different instance. Show information
        // required within the table.
        if (typeof instance !== "object") {
            // Instance is not an object, so it's probably an id of the
            // instance selected, grab the data we need.
            instance = await eel.statistics_information(instance)();
        }

        if (hideAndShow) {
            // Hiding the panel before building our table and displaying it.
            // We do this so we can switch between instances without weird html effects.
            hidePanel(elements.statisticsContent, elements.statisticsTableLoader, function() {
                buildTable(instance);
                // Display the panel again once building of the
                // table has concluded properly.
                showPanel(elements.statisticsContent, elements.statisticsTableLoader);
            });
        } else {
            // Otherwise, just build the table and then display
            // our statistics content like we normally would.
            buildTable(instance);
            // Display panel once table is built out.
            showPanel(elements.statisticsContent, elements.statisticsTableLoader);
        }
    }

    function buildStatisticsTable(data) {
        // Build out the statistics table.
        // We display all statistics and provide
        // a simple table to view information.

        // If multiple instances are currently available, we should display
        // a selector to change the selected instances information.
        if (data.instances.length > 1) {
            // Make sure the container has been properly shown, so that
            // on main display, it can be used by the user.
            elements.statisticsSelectorContainer.show();
            // Update the selector to contain all proper options
            // that can choose from as a user.
            for (let instance of data.instances) {
                elements.statisticsSelectorSelect.append($("<option>", {value: instance.pk, text: instance.name}));
            }

            // Setup the click listener so we can properly swap betwwen instances.
            // Swapping an instance should reload the table with newest information.
            elements.statisticsSelectorSelect.change(function() {
                reloadStatisticsTable($(this).val(), true);
            });
        }

        // Load the base table with our current information.
        // Regardless of whether or not multiple instances are available.
        reloadStatisticsTable(data.instances[0]);

        // Hide our loader and display the table once it's been built
        // out properly and everything is now ready.
        showPanel(elements.statisticsContent, elements.statisticsTableLoader);
    }

    async function loadStatisticsTable() {
        // Load the statistics table by grabbing the statistics information
        // asynchronously to display all statistics available.
        let data = await eel.statistics_information()();

        // Using the data retrieved through eel to ensure
        // that we properly build the table.
        buildStatisticsTable(data);
    }

    // Run our load statistics function once everything is ready.
    loadStatisticsTable();
});