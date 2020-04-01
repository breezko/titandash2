/**
 * settings.js
 */
$(document).ready(function() {
    let elements = {
        settingsTableLoader: $(".settingsTableLoader"),
        settingsContent: $("#settingsContent"),
        settingsTable: $("#settingsTable")
    };

    function buildSettingsTable(data) {
        // Build out the settings table, including all key value pairs
        // derived through the base data retrieval, this is done once
        // when the page is loaded.
        let html = `
            <thead>
                <tr>
                    <th>Setting</th>
                    <th>Value</th>
                </tr>
            </thead>
        `;

        // Make sure we include the initial <tbody> element
        // in our main html element.
        html += "<tbody>";

        // Looping through each key available, the key can be
        // used to grab the value as well per iteration.
        for (let key in data) {
            html += `
                <tr>
                    <td>${formatString(key)}</td>
                    <td>${data[key]}</td>
                </tr>
            `;
        }

        // We also need to append the closing </tbody> element
        // to our main html element when finished.
        html += "</tbody>";

        // Table is finished building, append new html to the settings table element.
        elements.settingsTable.append(html);

        // Hide the table loader and display our table.
        elements.settingsTableLoader.fadeOut(50, function() {
            elements.settingsContent.fadeIn(100);
        });
    }

    async function loadSettingsTable() {
        // Load the settings table by grabbing our settings information
        // asynchronously and attempt to build the table and fade everything
        // in correctly after being populated.

        // Using eel module to communicate with the backend
        // so we have the data needed to populate tables.
        let data = await eel.settings_information()();

        // Attempt to build out the settings table once data has
        // been successfully retrieved.
        buildSettingsTable(data);
    }

    // Run our load settings function once when everything
    // is ready and defined.
    loadSettingsTable();
});
