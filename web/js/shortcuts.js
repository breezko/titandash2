/**
 * shortcuts.js
 */
$(document).ready(function() {
    let elements = {
        shortcutsTableLoader: $(".shortcutsTableLoader"),
        shortcutsContent: $("#shortcutsContent"),
        shortcutsTable: $("#shortcutsTable")
    };

    function generateShortcut(shortcut) {
        // Generate the html element that represents a shortcut.
        // we place these into "+" separated <kbd> elements.
        let element = "";

        $.each(shortcut, function(i, v) {
            element += `<kbd>${v}</kbd>`;

            // Make sure we include a separator between shortcut elements
            // if the last element is not being processed.
            if (i + 1 !== shortcut.length) {
                element += "&nbsp;+&nbsp;";
            }
        });

        // Return our parsed element once we've appended all shortcut
        // keys present for each one.
        return element
    }

    function buildShortcutsTable(data) {
        // Build out the shortcuts table, including all proper key value
        // pairs derived through the base data retrieval.
        let html = `
            <thead>
                <tr>
                    <th>Function</th>
                    <th>Shortcut</th>
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
                    <td>${generateShortcut(data[key])}</td>
                </tr>
            `;
        }

        // We also need to append our closing </tbody> element
        // to our main html element when finished.
        html += "</tbody>";

        // Table is finished building, append new html to the shortcuts table element.
        elements.shortcutsTable.append(html);

        // Hide the table loader and display our table.
        elements.shortcutsTableLoader.fadeOut(50, function() {
            elements.shortcutsContent.fadeIn(100);
        });
    }

    async function loadShortcutsTable() {
        // Load the shortcuts table by grabbing our shortcuts information
        // asynchronously and attempt to build the table and fade everything
        // in correctly after being populated.

        // Using eel module to communicate with the backend
        // so we have the data needed to populate tables.
        let data = await eel.shortcuts_information()();

        // Attempt to build out the shortcuts table once the data has
        // been successfully retrieved.
        buildShortcutsTable(data);
    }

    // Run our load shortcuts function once when everything
    // is ready and defined.
    loadShortcutsTable();
});