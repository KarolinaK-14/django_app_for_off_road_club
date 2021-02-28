document.addEventListener("DOMContentLoaded", () => {
    /**
     * Images, after clicking on them, display in a full screen mode.
     */
    const elements = document.querySelectorAll('#image');
    const body = document.querySelector('body');
    console.log(elements);
    console.log(body);

    elements.forEach(el => {
        el.addEventListener('click', function () {
            const div = document.createElement('div');
            div.className = 'fullScreen';
            body.append(div);
            const imgBig = document.createElement('img');
            imgBig.src = this.querySelector('img').getAttribute('src');
            div.append(imgBig);
            const btn = document.createElement('button');
            btn.className = 'close btn btn-warning';
            btn.innerText = 'zamknij';
            div.append(btn);
            btn.addEventListener('click', e => {
                div.parentElement.removeChild(div);
            });
        });
    });

    /**
     * Remove default tooltips that appear if inputs are required.
     */
    const inputs = document.querySelectorAll('input');
    inputs.forEach(el => el.title = ' ');

     /**
     * Customize tooltips which appear if a user clicks the submit button
     * when form fields are filled incorrectly or are not filled at all.
     */
    const form_fields = document.querySelectorAll('input, textarea, select');
    form_fields.forEach(el => {
        el.addEventListener("invalid", function () {
            el.setCustomValidity("Wypełnij poprawnie to pole");
        });
        el.addEventListener("change", function () {
            try {
                el.setCustomValidity('');
            }
            catch(e){}
        });
        el.addEventListener("keypress", function () {
            try {
                el.setCustomValidity('');
            }
            catch(e){}
        });
    });
})
