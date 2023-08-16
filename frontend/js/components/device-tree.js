/*
 * Device tree components
*/
import { Modal } from "bootstrap/dist/js/bootstrap.bundle.js";
import Clipboard from "clipboard";

//
// Device tree UI features
//
// The tree layout features like selection management and items folding.
//
export function DeviceTreeDisplay() {
    // Remove 'open' attribute from all treegrid items to close them all
    function handleTreegridCloseAllItem(button) {
        let target = button.dataset.treegridTarget + " .treegrid__wrapper";
        document.querySelectorAll(target).forEach(
            item => item.removeAttribute("open")
        );
    }
    // Set 'open' attribute from all treegrid items to open them all
    function handleTreegridOpenAllItem(button) {
        let target = button.dataset.treegridTarget + " .treegrid__wrapper";
        document.querySelectorAll(target).forEach(
            item => item.setAttribute("open", "true")
        );
    }

    // Bind click event on buttons to open/close treegrid items
    document.querySelectorAll("#treegrid-open-all").forEach(
        button => button.addEventListener(
            "click",
            () => handleTreegridOpenAllItem(button)
        )
    );
    document.querySelectorAll("#treegrid-close-all").forEach(
        button => button.addEventListener(
            "click",
            () => handleTreegridCloseAllItem(button)
        )
    );
};


//
// Device tree export features
//
// Gather selections, send it to backend, handle backend response, display content in
// modal and manage content copy to clipboard.
//
// There is currently no specific behavior for export action type since backend is
// doing all the job and they all result to a simple content.
//
// Copy to clipboard feature stands on 'clipboard.js' since modern native browser API
// only work with HTTPS (or user custom browser permissions).
//
export function DeviceTreeExport() {
    function handleTreegridExportAction(e, button) {
        e.preventDefault();

        // Define settings from menu button data attributes
        let action = button.dataset.treegridAction;
        let form = document.querySelector(button.dataset.treegridForm);
        let title = button.dataset.treegridTitle;

        // Init payload to send to backend
        let request_data = {"action": action, "data": {"paths": []}};

        // Form element selection
        let token = form.querySelector("input[name='csrfmiddlewaretoken']").value;
        let checked = form.querySelectorAll(".path-selection:checked");

        // Modal container and object
        let modalContainer = document.getElementById("treegrid-export-modal");
        let modal = new Modal(modalContainer);

        // Modal element selection
        let modalTitle = modalContainer.querySelector(".modal-title");
        let modalBody = modalContainer.querySelector(".modal-body");
        let modalCopyButton = modalContainer.querySelector(".copy-button");

        // No selections, aborting
        if (checked.length == 0) {
            return false;
        }

        // Immediately set modal title since it won't change
        modalTitle.textContent = title;

        // Build payload from checked checkbox
        checked.forEach(function (checkbox) {
            request_data.data.paths.push({
                "path": checkbox.value,
                "name": checkbox.dataset.name,
                "total_files": checkbox.dataset.total_files,
                "total_filesize": checkbox.dataset.total_filesize,
                "recursive_files": checkbox.dataset.recursive_files,
                "recursive_filesize": checkbox.dataset.recursive_filesize,
            });
        });

        // Send payload with required Django CSRF token
        fetch(form.action, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": token
            },
            body: JSON.stringify(request_data)

        // Manage possible server error else return parsed JSON from response body
        }).then((response) => {
            if (!response.ok) {
                // Put error message into modal
                response.text().then((content) => {
                    modalBody.innerHTML = (
                        '<p class="p-3 text-danger"><b>Error HTTP' + response.status
                        + '</b></p>'
                        + '<p class="p-3 text-danger">' + content + '</p>'
                    );
                    modal.toggle();
                });
            }

            return response.json();

        // Manage success and deliver to modal
        }).then((data) => {
            modalBody.innerHTML = (
                "<pre class='p-3 bg-secondary text-white'>" + data.content + "</pre>"
            );
            modal.toggle();

            // Init ClipboardJs on button tied to modal to avoid focus issue
            // We have to use a button else browser may have issue with clipboard
            let clipboard = new Clipboard(modalCopyButton, {
                container: modalContainer,
                text: function(trigger) {
                    return data.content;
                }
            });

            clipboard.on("success", function(e) {
                // Add temporary active state on button
                e.trigger.classList.add("active");
                setTimeout(() => {
                    e.trigger.classList.remove("active");
                }, 1500);
                // Clear navigator selection
                e.clearSelection();
            });

        // Manage error throwed from fetch usage
        }).catch(function (error) {
            // Throw Javascript error
            throw new Error(
                "There was an error with fetch operation: " + error.message,
            );
        });
    }

    // Bind click event to export features function
    document.querySelectorAll(".treegrid-export-action").forEach(
        button => button.addEventListener(
            "click",
            () => handleTreegridExportAction(event, button)
        )
    );
};
