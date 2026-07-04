document.addEventListener('DOMContentLoaded', event => {
    const datepickers = document.querySelectorAll('input[data-field-type="date"]');
    if (datepickers.length){
        for(let dt of datepickers){
            new AirDatepicker(dt, {
                dateFormat: 'yyyy-MM-dd'
            });
        }
    }
    const wysiwyg = document.querySelectorAll('textarea[data-field-type="wysiwyg"]');

    if (wysiwyg.length){
        for(let wg of wysiwyg){
            const container = document.createElement('div');
            wg.parentNode.insertBefore(container, wg);
            wg.style.display = 'none';

            const quill = new Quill(container, {
                theme: 'snow',
                placeholder: wg.placeholder || ''
            });
            quill.root.style.minHeight = "200px";
            if (wg.value) {
                quill.root.innerHTML = wg.value;
            }
            quill.on('text-change', () => {
                wg.value = quill.root.innerHTML;
            });

        }
    }
});