function load_app() {
    $.ajax({
        url: "/application"
    }).then(function(data) {
        render_applications(data.applications);
        render_deleteapps(data.applications);
        render_apptags(data.applications);
    });
}

function render_applications(applications) {
    $(`div#ipa table tbody`).empty();
    $(`div#apk table tbody`).empty();
    applications.forEach(function (app, index) {
        var type = app.type;
        var dom_obj = render_app(index, app);
        $(`div#${type} > table > tbody`).append(dom_obj);
    });
}

function render_app(id, application) {
    let link = application.link;
    let type = application.type;
    let name = application.name;
    let version = application.version;
    let metadata = JSON.parse(application.metadata);
    let metadata_dom = render_object(metadata);
    let tags = "";

    if (Array.isArray(metadata.tags)) {
        metadata.tags.forEach(function (tag_name, index) {
            tags = `${tags} <span class="badge badge-primary">${tag_name}</span>`
        });
    }

    return `
    <tr>
        <td scope="row">
            <a href="${link}">
                <img style="width: 2em; height: 2em;" src="static/img/${type}.png"/>
            </a>
        </td>
        <td>
            ${name}-${version}
            ${tags}
        </td>
        <td>
            <button class="btn btn-link"
                    data-toggle="collapse"
                    data-target="#collapseID${id}">
                <img style="width: 1.5em; height: 1.5em;" src="static/img/help.png"/>
            </button>
        </td>
    </tr>
    <tr>
        <td colspan="4">
            <div class="collapse" id="collapseID${id}">
                <div class="card card-body">
                   ${metadata_dom}
                </div>
            </div>
        </td>
    </tr>`;
}

function get_type(object) {
    let type = typeof object;
    if (type == "object"){
        if (Array.isArray(object)) {
            return "array"
        } else {
            return "object"
        }
    } else {
        return "string"
    }
}


function render_array(meta) {
    var template = `<ul class="list-unstyled">`;
    meta.forEach(function (item, index) {
        if (get_type(item) == "object") {
            template = template + render_object(item);
        } else {
            template = template + `<li>${item}</li>`;
        }
    });
    return template + `</ul>`;
}


function render_object(meta) {
    let table = `
    <table class="table small table-sm table-responsive alert alert-dark">
        <thead>
            <tr>
                <th scope="col">Key</th>
                <th scope="col">Value</th>
            </tr>
        </thead>
        <tbody>`;

    for (var key in meta) {
        var value = meta[key];
        var type = get_type(value);
        if (type == "object") {
            value = render_object(value);
        } else if (type == "array") {
            value = render_array(value);
        }

        table = table + `
            <tr>
                <td>${key}</td>
                <td>${value}</td>
            </tr>
        `;
    }

    return table + "</table>";
}


function render_deleteapps(apps) {
    $("form#deleteApplications select").empty();
    apps.forEach(function (app, index) {
        var name = app.name + "-" + app.version + "." + app.type;
        $("form#deleteApplications select").append(`<option>${name}</option>`);
    });
}

function render_apptags(apps) {
    $("form select#applicationNameTags").empty();
    apps.forEach(function (app, index) {
        var name = app.name + "-" + app.version + "." + app.type;
        $("form select#applicationNameTags").append(`<option>${name}</option>`);
    });
    $("select#applicationTags").tagsinput("removeAll", { preventPost: true });
    tags = JSON.parse(apps[0].metadata).tags
    if (tags) {
        tags.forEach(function (tag_name, index) {
            $("select#applicationTags").tagsinput("add", tag_name, { preventPost: true });
        });
    }
}

