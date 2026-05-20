document.addEventListener('DOMContentLoaded', function () {
    var editButton = document.getElementById('edit-profile-button');
    var cancelButton = document.getElementById('cancel-edit-button');
    var viewBlock = document.getElementById('profile-view');
    var editBlock = document.getElementById('profile-edit');

    if (editButton && cancelButton && viewBlock && editBlock) {
        editButton.addEventListener('click', function () {
            viewBlock.classList.add('d-none');
            editBlock.classList.remove('d-none');
        });

        cancelButton.addEventListener('click', function () {
            editBlock.classList.add('d-none');
            viewBlock.classList.remove('d-none');
        });
    }
});
