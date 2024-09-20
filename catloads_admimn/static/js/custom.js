$(function() {
    var $keyword = $('#productsearch');
    var $product_box = $('#product_box');
    var $searchdiv = $('.searchdiv');


    function debounce(func, wait, immediate) {
        var timeout;
        return function() {
            var context = this, args = arguments;
            var later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    }

    var handleInput = debounce(function() {
        var value = $keyword.val().trim();
        let url = $product_box.data('url');

        if (value.length > 4) {
            $.ajax({
                type: 'GET',
                url: url,
                data: { 'search': value },
                success: function(response) {
                    $searchdiv.empty()
                    const product=response.products
                    for(i=0;i<product.length;i++){
                        var context = `<div class="search_item" data-code="${product[i].product_code}" data-size="${product[i].product_size}" data-id="${product[i].id}" data-unit="${product[i].product_unit}">${product[i].name}</div>`
                        $searchdiv.append(context)
                    }   
                },
                error: function(xhr) {
                    console.error(xhr.responseText);
                }
            });
        } else {
            $searchdiv.empty();
        }
    }, 250); 

    $keyword.on('input', handleInput);

    $('.searchdiv').on('click', ".search_item",function(){
        var product_item = ` <div class="product-item m-2">
        <div class="image">
            <img src="images/products/1.png" alt="">
        </div>
        <div class="flex items-center justify-between flex-grow">
            <div class="name">
                <a href="{% url 'catloadsadmin:product_list' %}" class="body-title-2">${$(this).text()}</a>
                <div class="text-tiny mt-3"></div>
            </div>
            <div>
                <div class="text-tiny mb-3">Size</div>
                <div class="body-text">${$(this).data('size')}${$(this).data('unit')}</div>
            </div>
            <div>
                <div class="body-title-2 mb-3">
                    Product ID</div>
                <div class="text-tiny">${$(this).data('code')}</div>
            </div>
            <div>
                <a class="body-title-2 mb-3 delete" data-id="${$(this).data('id')}">
                <i class="icon-trash-2" style="color: red;"></i></a>
            </div>
        </div>
        
    </div>`
    var checkbox = $('<input>').attr({
        class:"d-none",
        type: 'checkbox',
        name: 'options[]',
        value: $(this).data('id'),
        checked: 'checked'
    });
    $('#salecreate').append(checkbox)
    $product_box.append(product_item)
    $searchdiv.empty();
    updateFormState();

    })

    $('#product_box').on('click','.delete',function(){
        var product_id = $(this).data('id')
        $('input[name="options[]"][value="' + product_id + '"]').each(function() {
            $(this).remove()
        })
        $(this).parent().parent().parent().remove()
        updateFormState();
    })


});


function updateFormState() {
    var $productBox = $('#product_box');
    var $submitBtn = $('#submitbtn');
    var $msg = $('#msg');

    if ($productBox.children().length === 0) {
        $submitBtn.prop('disabled', true);
        $msg.text("Products can't be none");
        $msg.show();
    } else {
        $submitBtn.prop('disabled', false);
        $msg.hide();
    }
}



 