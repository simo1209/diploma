const form = document.querySelector('#control-form');
$('#control-form').submit(false);

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

function createTable(data, keys){

    let header = '<tr>'
    $.each(keys, (counter, key)=>{
        header+='<th>' + key + '</th>';
    })
    header+='</tr>';
    $('#table-header').html(header)

    let result = '';
    $.each(data, (i, item)=>{
        result += '<tr>'
        for(let key of keys){
            result+='<td>' + item[key] + '</td>';
        }
        result +='</tr>';
    })
    $('#table-body').html(result)
}

$("#control-form").submit( function () {    
    $.ajax({   
        type: "POST",
        data : $(this).serialize(),
        cache: false,  
        url: "./fetch",   
        success: function(data){
            createTable(data.result, data.keys)
        }   
    });   
    return false;   
});