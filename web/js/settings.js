/**
 * settings.js
 *
 * Perform all functionality required to retrieve and populate the settings table present on the page.
 */
$(document).ready(function() {
    let elements = {
        settingsTableLoader: $(".settingsTableLoader"),
        settingsTableWrapper: $("#settingsTable"),
        settingsTable: $("#settingsDataTable")
    };


    /**
     * Build the settings table out, expecting our data to contain a dictionary of key -> value pairs.
     *
     * The table will contain two columns, one containing the key and one containing the value.
     */
    function buildSettingsTable(data) {
        let html = "";
        // Build the headers for the table.
        html += `
            <thead>
                <tr>
                    <th>Setting</th>
                    <th>Value</th>
                </tr>
            </thead>
        `;

        // Build the body for the table.
        html += "<tbody>";
        for (let key in data) {
            html += `
                <tr>
                    <td>${key}</td>
                    <td>${data[key]}</td>
                </tr>
            `;
        }
        html += "</tbody>";

        // Table is finished building, append new html to the settings table element
        // and initialize the table through our datatable library.
        elements.settingsTable.append(html);
        elements.settingsTable.DataTable({
            searching: false,
            lengthChange: false,
            paging: false
        });

        // Hide the table loader and display our table.
        elements.settingsTableLoader.fadeOut(50, function() {
            elements.settingsTableWrapper.fadeIn(100);
        })
    }

    /**
     * Retrieve and setup the settings table to display all derived settings values.
     */
    async function loadSettingsTable() {
        // Use Eel and grab object containing all settings information.
        let data = await eel.settings_information()();
        // Attempt to build out the settings table once data has been retrieved.
        buildSettingsTable(data);
    }

    loadSettingsTable();
});
