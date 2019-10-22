$(document).ready(function() {

    $.ajax({
        url: "/application"
    }).then(function(data) {
        render_applications(data.applications);
    });

    $('input#uploadfile').on('change', function() {
        var fileName = $(this).val(); //get the file name
        //replace the "Choose a file" label
        $(this).next('.custom-file-label').html(fileName);
        var formData = new FormData();
        formData.append('file', $(this)[0].files[0]);
        xhr = new XMLHttpRequest();
        xhr.open('POST', '/application')
        xhr.onload = function() {
            if (xhr.status != 201) {
                alert("Error uploading.");
            } else {
                alert("Upload successful!");
                $(this).val('');
            }
            $('#uploadprogress').width("0%");
            $('input#uploadfile').val();
        };
        xhr.send(formData);
        $('#uploadprogress').width("50%");
    });

    $('button#deleteapp').on('click', function(event) {
        event.preventDefault();
        var type = $('input#deletetype').val().toLowerCase();
        var name = $('input#deletename').val();
        var version = $('input#deleteversion').val();
        var application = name + "-" + version + "." + type;
        xhr = new XMLHttpRequest();
        xhr.open('DELETE', '/application/' + application);
        xhr.onload = function() {
            if (xhr.status != 200) {
                alert("Unable to delete, check params.");
            } else {
                alert("Deleted!");
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
