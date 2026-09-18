const format_date = (value) => {
    if (!value) return "";
    let date = new Date(value);
    if (isNaN(date.getTime())){
        return "";
    }
    let year = date.getFullYear();
    let month = String(date.getMonth() + 1).padStart(2, '0');
    let day = String(date.getDate()).padStart(2, '0');
    let hours = String(date.getHours()).padStart(2, '0');
    let minutes = String(date.getMinutes()).padStart(2, '0');
    let seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};


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

const open_confirm = (link)=>{

    const options = {
        text: link.dataset.confirm || 'Confirm?',
        icon: link.dataset.type || 'warning' ,
        showCancelButton: true,
        confirmButtonText: link.dataset.buttonOk || 'OK',
        cancelButtonText: link.dataset.buttonCancel || 'Cancel',
    };
    if (link.dataset.title){
        options.title = link.dataset.title;
    }
    const url = link.href;
    const method = link.dataset.method && ['GET', 'POST', 'PUT', 'DELETE'].includes(link.dataset.method.toUpperCase())
        ? link.dataset.method.toUpperCase()
        : 'GET';
    Swal.fire(options).then((result) => {
        if (!result.isConfirmed)
            return;
        fetch(url, {
            method: method,
            headers: {
                Accept: 'application/json'
            }
        }).then((res) => {
            if (!res.ok)
                throw new Error('Error: ' + res.status);
            const callback = link.dataset.callback;
            console.log(callback);
            if (callback && callback in window && typeof window[callback] == "function"){
                window[callback]();
            }
        }).catch((err) => {
            Swal.fire({
                text: err.message,
                icon: "error"
            });
        });
    });
};


const refresh_view = (_dom) => {
    _dom.querySelectorAll('a[data-modal]').forEach(open_modal);
    _dom.querySelectorAll('a[data-confirm]').forEach(link=>{
        link.addEventListener("click", e=>{
            if (!link || !link.href){
                return true;
            }
            e.preventDefault();
            open_confirm(link);
        });
    });
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
