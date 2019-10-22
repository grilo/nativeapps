$(document).ready(function() {

    $.ajax({
        url: "/application"
    }).then(function(data) {
        render_applications(data.applications);
        render_deleteapps(data.applications);
    });

    $("input#uploadfile").on("change", function() {
        var fileName = $(this).val(); //get the file name
        //replace the "Choose a file" label
        $(this).next(".custom-file-label").html(fileName);
        var formData = new FormData();
        formData.append("file", $(this)[0].files[0]);
        xhr = new XMLHttpRequest();
        xhr.open("POST", "/application")
        xhr.onload = function() {
            if (xhr.status != 201) {
                alert("Error uploading.");
            } else {
                alert("Upload successful!");
                $(this).val("");
                location.reload();
            }
            $("#uploadprogress").width("0%");
            $("input#uploadfile").val();
        };
        xhr.send(formData);
        $("#uploadprogress").width("50%");
    });

    $("form#deleteApplications button#askDeleteApplication").on("click", function(event) {
        var app = $("form#deleteApplications select").children("option:selected").val();
        $("div#deleteApplicationText").html(`<p>Are you sure you want to delete ${app}?</p>`);
    });

    $("form#deleteApplications button#confirmDeleteApplication").on("click", function(event) {
        var app = $("form#deleteApplications select").children("option:selected").val();
        xhr = new XMLHttpRequest();
        xhr.open("DELETE", "/application/" + app);
        xhr.onload = function() {
            if (xhr.status != 200) {
                alert("Unable to delete, check params.");
            } else {
                location.reload();
            }
        };
        xhr.send();
    });

});

// Persist selected tab on refresh
// https://stackoverflow.com/questions/18999501
$(document).ready(function() {
    if (location.hash) {
        $("a[href='" + location.hash + "']").tab("show");
    } else {
        // If user agent is ios, show the correct tab
        if (navigator.userAgent.match(/iPhone|iPad|iPod/i)) {
            $("a[href='#ipa'").tab("show");
        } else {
            $("a[href='#apk'").tab("show");
        }
    }
    $(document.body).on("click", "a[data-toggle='pill']", function(event) {
        location.hash = this.getAttribute("href");
    });
});
$(window).on("popstate", function() {
    var anchor = location.hash || $("a[data-toggle='pill']").first().attr("href");
    $("a[href='" + anchor + "']").tab("show");
});
