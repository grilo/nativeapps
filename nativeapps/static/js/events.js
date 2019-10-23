$(document).ready(function() {

    load_app();

    $("input#uploadfile").on("change", function() {
        var fileName = $(this).val(); //get the file name
        //replace the "Choose a file" label
        $(this).next(".custom-file-label").html(fileName);
        var formData = new FormData();
        formData.append("file", $(this)[0].files[0]);
        xhr = new XMLHttpRequest();
        xhr.open("POST", "/application")
        xhr.upload.addEventListener("progress", function(event) {
            if (event.lengthComputable) {
                var percentComplete = event.loaded / event.total * 100;
                $("div#uploadProgress").width(percentComplete.toFixed(0) + "%");
                $("div#uploadProgress").html(event.loaded + "/" + event.total);
            }
        }, false);

        xhr.onload = function() {
            if (xhr.status != 201) {
                alert("Error uploading.");
            } else {
                alert("Upload successful!");
                $(this).val("");
                load_app();
            }
            $("div#uploadProgress").width("0%");
            $("input#uploadfile").val();
        };
        xhr.send(formData);
    });

    $("form#deleteApplications button#askDeleteApplication").on("click", function(event) {
        var app = $("form#deleteApplications select").children("option:selected").val();
        $("div#deleteApplicationText").html(`<p>Are you sure you want to delete ${app}?</p>`);
    });

    $("form#deleteApplications button#confirmDeleteApplication").on("click", function(event) {
        var app = $("form#deleteApplications select").children("option:selected").val();
        $.ajax({
            url: "/application/" + app,
            type: "DELETE",
            success: function(result) {
                load_app();
            },
            error: function(result) {
                alert("Unable to delete, check params.");
            },
        });
    });

    $("select#applicationTags").on("beforeItemAdd", function(event) {
        var app = $("select#applicationNameTags").children("option:selected").val();
        var tag_name = event.item;

        if (event.options && event.options.preventPost) {
            return;
        }

        $.ajax({
            url: "/application/" + app + "/tag/" + tag_name,
            type: "PUT",
            success: function(result) {
                $.ajax({
                    url: "/application"
                }).then(function(data) {
                    render_applications(data.applications);
                });
            },
            error: function(result) {
                $("select#applicationTags").tagsinput("remove", tag_name, { preventPost: true });
            },
        });

    });

    $("select#applicationTags").on("beforeItemRemove", function(event) {
        var app = $("select#applicationNameTags").children("option:selected").val();
        var tag_name = event.item;

        if (event.options && event.options.preventPost) {
            return;
        }

        $.ajax({
            url: "/application/" + app + "/tag/" + tag_name,
            type: "DELETE",
            success: function(result) {
                $.ajax({
                    url: "/application"
                }).then(function(data) {
                    render_applications(data.applications);
                });
            },
            error: function(result) {
                $("select#applicationTags").tagsinput("add", tag_name, { preventPost: true });
            },
        });
    });

    $("select#applicationNameTags").on("change", function(event) {
        var app = event.target.value;
        $.ajax({
            url: "/application/" + app + "/tag",
        }).then(function(data) {
            $("select#applicationTags").tagsinput("removeAll");
            data.forEach(function (tag_name, index) {
                $("select#applicationTags").tagsinput("add", tag_name, { preventPost: true });
            });
        });

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
