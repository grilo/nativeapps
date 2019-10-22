function render_deleteapps(apps) {
    apps.forEach(function (app, index) {
        var name = app.name + "-" + app.version + "." + app.type;
        $("form#deleteApplications select").append(`<option>${name}</option>`);
    });
}


function render_applications(applications) {

    for (var i = 0; i < applications.length; i++) {
        var type = applications[i].type;
        var dom_obj = render_app(i, applications[i]);
        $(`div#${type} table tbody`).append(dom_obj);
    }
}

function render_app(id, application) {
    let link = application.link;
    let type = application.type;
    let name = application.name;
    let version = application.version;
    let metadata = render_object(JSON.parse(application.metadata));
    return `
    <tr>
        <td scope="row">
            <a href="${link}">
                <img style="width: 2em; height: 2em;" src="static/img/${type}.png"/>
            </a>
        </td>
        <td>${name}</td>
        <td>
            <button class="btn btn-link"
                    data-toggle="collapse"
                    data-target="#collapseID${id}">
                ${version}
            </button>
        </td>
    </tr>
    <tr>
        <td colspan="4">
            <div class="collapse" id="collapseID${id}">
                <div class="card card-body">
                   ${metadata}
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
    var template = ``;
    meta.forEach(function (item, index) {
        if (get_type(item) == "object") {
            template = template + render_object(item);
        } else {
            template = template + `<p>${item}</p>`;
        }
    });
    return template;
}


function render_object(meta) {
    let table = `
    <table class="table table-sm table-responsive alert alert-dark">
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
