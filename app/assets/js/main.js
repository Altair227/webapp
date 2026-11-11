let FB;
// jodit-finder runs on :9023 on the same host the page was opened from
const JODIT_URL = `${window.location.protocol}//${window.location.hostname}:9023/`;
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


const get_file_browser = () => {
    if (!FB){
        FB = new Jodit.modules.FileBrowser({
            ajax: {
                url: JODIT_URL
            },
            uploader: {
                url: JODIT_URL + '?action=fileUpload'
            }
        });
    }
    return FB;
};

// file manager result -> list of URLs (root-relative for local files)
const selected_urls = (data) => data.files.map(
    file => file.startsWith('http') ? file : data.baseurl + file
);

// div[data-field-type="images"]: one .image-row per image
// ([input name=images][browse][+][-]), see ImageListWidget
const image_rows = (box) => {
    if (box.dataset.imagesBound){
        return;
    }
    box.dataset.imagesBound = "true";
    const max_items = parseInt(box.dataset.maxItems || "0", 10);
    const rows = () => box.querySelectorAll('.image-row');

    const set_url = (row, url) => {
        row.querySelector('input').value = url;
    };
    // new rows are copies of the first one, emptied
    const add_row = (after, url = "") => {
        const row = rows()[0].cloneNode(true);
        set_url(row, url);
        after.after(row);
        return row;
    };
    const update = () => {
        const full = max_items > 0 && rows().length >= max_items;
        box.querySelectorAll('[data-image-action="add"]').forEach(btn => btn.disabled = full);
    };

    box.addEventListener("click", e => {
        const button = e.target.closest('[data-image-action]');
        if (!button) {
            return;
        }
        e.preventDefault();
        const row = button.closest('.image-row');
        switch (button.dataset.imageAction) {
            case "browse":
                // several picked files fill this row and new rows after it
                get_file_browser().open(data => {
                    let current = row;
                    selected_urls(data).forEach((url, index) => {
                        if (index === 0) {
                            set_url(row, url);
                        } else if (max_items <= 0 || rows().length < max_items) {
                            current = add_row(current, url);
                        }
                    });
                    update();
                }, true);
                break;
            case "add":
                add_row(row).querySelector('input').focus();
                break;
            case "remove":
                if (rows().length > 1) {
                    row.remove();
                } else {
                    set_url(row, "");
                }
                break;
        }
        update();
    });
    update();
};

const refresh_view = (_dom) => {
    _dom.querySelectorAll('a[data-modal]').forEach(open_modal);
    _dom.querySelectorAll('a[data-confirm]').forEach(link => {
        link.addEventListener("click", e => {
            if (!link || !link.href) {
                return true;
            }
            e.preventDefault();
            open_confirm(link);
        });
    });
    const datepickers = _dom.querySelectorAll('input[data-field-type="date"]');
    if (datepickers.length) {
        for (let dt of datepickers) {
            new AirDatepicker(dt, {
                dateFormat: 'yyyy-MM-dd'
            });
        }
    }
    const wysiwyg = _dom.querySelectorAll('textarea[data-field-type="wysiwyg"]');

    if (wysiwyg.length) {
        for (let wg of wysiwyg) {
            const editor = Jodit.make(wg, {
                height: 400,
                filebrowser: {
                    ajax: {
                        url: JODIT_URL
                    }
                },
                uploader: {
                    url: JODIT_URL + '?action=fileUpload'
                }
            });

        }
    }

    _dom.querySelectorAll('div[data-field-type="images"]').forEach(image_rows);

    const filemanagers = _dom.querySelectorAll('button[data-button-type="filemanager"]');
    if (filemanagers.length) {
        for (let fm of filemanagers) {

            if (fm.dataset.fmBound){
                continue;
            }
            const type = fm.dataset.selectType || "file";
            const field = fm.dataset.selectField ? _dom.querySelector("#" + fm.dataset.selectField ) : null;
            fm.addEventListener("click", e=>{
                e.preventDefault();
                get_file_browser().open(data=>{
                    if (field){
                        field.value = selected_urls(data)[0];
                        field.dispatchEvent(new Event('change',{bubbles: true}));
                    }
                }, type == "image");
            });
            fm.dataset.fmBound = true;
        }
    }
};


document.addEventListener('DOMContentLoaded', event => {

    refresh_view(
        document
    );
});
