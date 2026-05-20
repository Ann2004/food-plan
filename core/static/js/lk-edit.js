document.addEventListener('DOMContentLoaded', function () {
    var editButton = document.getElementById('edit-profile-button');
    var cancelButton = document.getElementById('cancel-edit-button');
    var viewBlock = document.getElementById('profile-view');
    var editBlock = document.getElementById('profile-edit');
    var avatarInput = document.getElementById('avatar-input');
    var avatarPreview = document.getElementById('avatar-preview');
    var avatarPlusBtn = document.getElementById('avatar-plus-btn');

    if (editButton && cancelButton && viewBlock && editBlock) {
        editButton.addEventListener('click', function () {
            viewBlock.classList.add('d-none');
            editBlock.classList.remove('d-none');
            avatarPlusBtn.classList.remove('d-none');
        });

        cancelButton.addEventListener('click', function () {
            editBlock.classList.add('d-none');
            viewBlock.classList.remove('d-none');
            avatarPlusBtn.classList.add('d-none');
        });
    }

    if (avatarInput && avatarPreview) {
        avatarInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    avatarPreview.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
});