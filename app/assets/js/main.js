const open_modal = (link) => {

    if (link.dataset.modalBound){
        return;
    }
    link.dataset.modalBound = "true";
    link.addEventListener('click', async (e)=>{
        const modal = document.getElementById("view-modal");
        if (!modal) {
            return true;
        }
        e.preventDefault();
        const modal_body = modal.querySelector('#view-modal-body');
        const bs_modal = bootstrap.Modal.getOrCreateInstance(modal);
        modal_body.innerHTML = ` 
            <div class="text-center py-4"> 
                <div class="spinner-border" role="status"> 
                    <span class="visually-hidden">Loading…</span> 
                </div> 
            </div> `;
        bs_modal.show();
        try {
            const resp = await fetch(link.href, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!resp.ok) {
                throw new Error('Loading error');
            }
            modal_body.innerHTML = await resp.text();
        } catch (err) {
            modal_body.innerHTML = `<div class="alert alert-danger">Trouble loading content</div>`;
        }
        if (!modal.dataset.hiddenBound) {
            modal.dataset.hiddenBound = 'true';
            modal.addEventListener('hidden.bs.modal', () => {
                modal_body.innerHTML = '';
            });
        }
    });
};
const refresh_view = (_dom) => {
    _dom.querySelectorAll('a[data-modal]').forEach(open_modal);
    const datepickers = _dom.querySelectorAll('input[data-field-type="date"]');
    if (datepickers.length){
        for(let dt of datepickers){
            new AirDatepicker(dt, {
                dateFormat: 'yyyy-MM-dd'
            });
        }
    }
    const wysiwyg = _dom.querySelectorAll('textarea[data-field-type="wysiwyg"]');

    if (wysiwyg.length){
        for(let wg of wysiwyg){
            const container = _dom.createElement('div');
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
};


document.addEventListener('DOMContentLoaded', event => {

    refresh_view(
        document
    );
});