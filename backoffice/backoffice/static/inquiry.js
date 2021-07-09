const form = document.querySelector('#control-form');

document.querySelectorAll('#start_date_filter,#end_date_filter').forEach(input => {
    input.addEventListener('change', () => {
        if (input.value == '') {
            document.querySelector('#time_group').disabled = true;
        } else {
            document.querySelector('#time_group').disabled = false;
        }
    });
});

document.querySelectorAll('#type_filter').forEach(input => {
    input.addEventListener('change', () => {
        if (this.value == '') {
            document.querySelector('#type_group').disabled = true;
        } else {
            document.querySelector('#type_group').disabled = false;
        }
    });
});

document.querySelectorAll('#status_filter').forEach(input => {
    input.addEventListener('change', () => {
        if (this.value == '') {
            document.querySelector('#status_group').disabled = true;
        } else {
            document.querySelector('#status_group').disabled = false;
        }
    });
});

document.querySelector('#show-form').addEventListener('click', () => {
    form.style.display = 'block';
})

document.querySelector('#hide-form').addEventListener('click', () => {
    form.style.display = 'none';
})
