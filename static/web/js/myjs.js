$(document).ready(function(){
    $('.shop-meta').on('click',function(){
        window.location.href = $(this).data('url')
    })
    $('#order_cofirm').on('click',function(e){
        e.preventDefault();
        let csrftoken = $('[name=csrfmiddlewaretoken]').val();
        var validatation = validate_orderdata()
        var city = $('#city').val()
        var promocode = $('#promocode').data('id')
        var country = $('#email').data('id')
        var url = $(this).data('url')
        var user_id = $('#email').data('id')
        var total_price = $('#total_pricefinal').val()
        var total_discount = $('#total_dsicount').val()
        var order_id = $('#order_id').val()
        var phone = $('#mobile').val()
        var razorpay_id = $('#razorpay_order_id').val()
        var razorpay_key = $('#razorpay_key_id ').val()
        var currency = $('#currency ').val()
        console.log(currency,razorpay_id,razorpay_key)
    
        if (!validatation) {
            // var options = {
            //     "key": "YOUR_KEY_ID", // Enter the Key ID generated from the Dashboard
            //     "amount": "50000", // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
            //     "currency": "INR",
            //     "name": "Acme Corp", //your business name
            //     "description": "Test Transaction",
            //     "image": "https://example.com/your_logo",
            //     "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
            //     "callback_url": "https://eneqd3r9zrjok.x.pipedream.net/",
            //     "prefill": { //We recommend using the prefill parameter to auto-fill customer's contact information especially their phone number
            //         "name": "Gaurav Kumar", //your customer's name
            //         "email": "gaurav.kumar@example.com",
            //         "contact": "9000090000" //Provide the customer's phone number for better conversion rates 
            //     },
            //     "notes": {
            //         "address": "Razorpay Corporate Office"
            //     },
            //     "theme": {
            //         "color": "#3399cc"
            //     }
            // };
            var options = {
                "key": razorpay_key, // Enter the Key ID generated from the Dashboard
                "amount": total_price*100, // Convert to paise. Amount is in currency subunits. Default currency is INR.
                "currency": currency,
                "name": "Catloads",
                "description": "Description",
                "order_id": razorpay_id, // This is a sample Order ID. Pass the `id` obtained in the previous step
                "handler": function (response) {
                    // Prepare data for AJAX request
                    var paymentData = {
                        'razorpay_payment_id': response.razorpay_payment_id,
                        'razorpay_order_id': response.razorpay_order_id,
                        'razorpay_signature': response.razorpay_signature,
                        'user': user_id,
                        'city': city,
                        'country': country,
                        'promocode': promocode,
                        'total_price': total_price,
                        'order_id': order_id,
                        'phone': phone,
                        'discount': total_discount
                    };
    
                    $.ajax({
                        type: 'POST',
                        headers: {'X-CSRFToken': csrftoken},
                        url: url,
                        data: paymentData,
                        success: function(response) {
                            if (response.Message === 'Success') {
                                if (response.redirect_url) {
                                    window.location.href = response.redirect_url; 
                                }
                            }
                        },
                        error: function(xhr) {
                            console.error(xhr.responseText);
                            // resetFields();
                        }
                    });
                },
                // "callback_url": "https://eneqd3r9zrjok.x.pipedream.net/",
                "prefill": {
                    "name": $('#name').val(),
                    "email": $('#email').val(),
                    "contact":$('#mobile').val()
                },
                "theme": {
                    "color": "#F37254"
                }
            };
            try {
                var rzp1 = new Razorpay(options);
                rzp1.on('payment.failed', function (response){
                    alert("Payment Failed...!")
                    window.location.href = '/customer/orders'

            });
                rzp1.open();
            } catch (e) {
                alert("Razorpay Checkout script failed to load. Please try again in another browser or contact support.");
                console.error("Razorpay Checkout error: ", e);
            }
        }
    })
    cart= loadCart()
    $('#cartcount').text(cart.items.length)

    var $keyword = $('#serach_input');
    // var $product_box = $('#product_box');
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
        let url = $keyword.data('url');

        if (value.length > 4) {
            $.ajax({
                type: 'GET',
                url: url,
                data: { 'search': value },
                success: function(response) {
                    $searchdiv.empty()
                    const product=response.products
                    console.log(product)
                    for(i=0;i<product.length;i++){
						
                        var context = `<a href="/product/${product[i].slug}" class="p-2 ms-4 mt-2" style="display: block;">${product[i].name}</a>`
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

    $('.cart_btn').click(function(e) {
        // e.preventDefault(); // Prevent default action of the anchor tag

        const productId = $(this).data('id');
        const productPrice = $(this).data('price');
        const productimage = $(this).data('image');
        const product_slug = $(this).data('slug');
        const product_name = $(this).data('name');
        const quantity = 1;  
        const cart_btn = $(this)
        const url = $(this).data('url')
        console.log(url)
        

        const productObj = {
            product: productId,
            price: productPrice,
            quantity: quantity,
            image:productimage,
            slug : product_slug,
            name : product_name,
            subtotal: productPrice * quantity
        };

        let cart = loadCart()

        let existingProduct = cart.items.find(item => item.product === productId);
        if (existingProduct) {
            existingProduct.quantity += quantity;
            existingProduct.subtotal += productPrice * quantity;
        } else {
            cart.items.push(productObj);
        }
        cart.cart_total = cart.items.reduce((total, item) => total + item.subtotal, 0);
        localStorage.setItem('catloads_cartdata', JSON.stringify(cart));
        $('#cartcount').text(cart.items.length)
        order_post(url,cart)
        // cart_btn.text('Added to Cart')
        // cart_btn.removeClass('btn-secondary')
        // cart_btn.addClass('btn-success')
        // $('.cart_btn2').show()
    });
    

    if (window.location.pathname === '/customer/cart') { 
        load_cartdata() 

    // Check if the current page is the cart page
        
    }


    
   
$('#cart_table').on('click', '.plus-cart', function() {
    const index = $(this).data('index');
    let cart = loadCart();
    cart.items[index].quantity++;
    cart.items[index].subtotal = cart.items[index].price * cart.items[index].quantity;
    cart.cart_total = updateCartTotal(cart)
    localStorage.setItem('catloads_cartdata', JSON.stringify(cart));
    $(this).siblings('input').val( cart.items[index].quantity)
});

$('#cart_table').on('click', '.minus-cart', function() {
    const index = $(this).data('index');
    let cart = loadCart();
    cart.items[index].quantity--;
    if(cart.items[index].quantity < 1){
        cart.items.splice(index, 1);
        $(this).parents('tr').first().remove()
        $('.cartsdata').hide()

    }
    if(cart.items.length >= 1){
    cart.items[index].subtotal = cart.items[index].price * cart.items[index].quantity;
    $(this).siblings('input').val( cart.items[index].quantity)    
    cart.cart_total = updateCartTotal(cart)
    }
    else{
        cart.cart_total = 0
    $('.cartmsg').show()
    }
    updateCartTotal(cart)

    localStorage.setItem('catloads_cartdata', JSON.stringify(cart));
});

$('#login-form, #registration-form').submit(function(e) {
    e.preventDefault(); // Prevent the default form submission

// sourcery skip: avoid-using-var
    var cartData = localStorage.getItem('catloads_cartdata'); // Get cart data from localStorage
    if (cartData) {
        $('<input>').attr({
            type: 'hidden',
            name: 'cartData',
            value: cartData
        }).appendTo(this); // Append cart data to the form
    }
    localStorage.removeItem('catloads_cartdata');
    this.submit(); // Submit the form
});

function validate_orderdata(){
    var status =true
    var errobox = $('#error_box')
    var name = $('#name').val();
    var email = $('#email').val();
    var mobile = $('#mobile').val();
    var city = $('#city').val();
    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Simple email regex pattern
    var mobilePattern = /^[0-9]{10}$/; // Regex pattern for 10-digit mobile number

    // Validate Email
    if (!emailPattern.test(email)) {
	    errobox.append(`<div class="alert alert-warning">Enter a Valid Email</div>`)
    }

    // Validate Mobile
    if (!mobilePattern.test(mobile)) {
        errobox.append(`<div class="alert alert-warning">Enter a Valid Number</div>`)
        status= false
    }

    // Validate City
    if (city.length < 2) {
        errobox.append(`<div class="alert alert-warning">Enter a Valid City</div>`)

        status= false
        ; // Prevent form from submitting
    }

    if (name.length < 2) {
        errobox.append(`<div class="alert alert-warning">Enter a Valid Name</div>`)

        status= false

    }
    return status
}

$('#submitorder_btn').on('clcik',function(e) {
   
});

$('#promocodebtn').on('click', function(){
    var promocode = $('#promocode')
    var promobtn = $(this)
    var order_total = $('#total')
    var url = $(this).data('url')
        $.ajax({
            type: 'GET',
            url: url,
            data: { 'promocode': promocode.val() ,'order_total':order_total.data('total')},
            success: function(response) {
                if (response.Message=='Success'){
                    promobtn.text(`Applied`)
                    promobtn.attr('disabled', true)
                    $('#alertpromo').text(`Applied ₹ ${response.discount} discount on your order`)
                    promobtn.addClass('btn-success')
                    order_total.text('₹'+response.total)
                    $('#discount').text('₹'+response.discount)
                    promocode.attr('data-id',response.promocode_id)
                    $('#total_pricefinal').val(response.total)
                    $('#total_dsicount').val(response.discount)

                }
                else{
                    $('#alertpromo').text('Invalid promocode').addClass('text-danger')
                }
            },
            error: function(xhr) {
                console.error(xhr.responseText);
                // resetFields();
            }
        });
})


$('#checkout_btn').on('click',function(){
    console.log('hhh')
    var url = $(this).data('url')
    var cart = loadCart()
    order_post(url,cart)

})
});

function order_post(url,cart){
    if (cart.items.length>=1){
        let csrftoken = $('[name=csrfmiddlewaretoken]').val();
        $.ajax({
            type: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            url: url,
            data: {'cart':JSON.stringify(cart)},
            success: function(response) {
                if (response.Message=='Success'){
                    if (response.redirect_url) {
                        localStorage.removeItem('catloads_cartdata');
                        window.location.href = response.redirect_url; 
                    }
                }
                else{
                    if (response.redirect_url) {
                        window.location.href = response.redirect_url; 
                    }
                }
            },
            error: function(xhr) {
                console.error(xhr.responseText);
            }
        });

    }
}
   



function updateCartTotal(cart) {
    let total = 0;
    cart.items.forEach(item => {
        total += item.subtotal;
    });
    $('#cart_total').text(`₹ ${total}`)
    return total
    

    // Assuming there is an element to display the total
}

function loadCart() {
    let cart = JSON.parse(localStorage.getItem('catloads_cartdata'));
    if (!cart) {
        cart = { cart_total: 0, items: [] };
    }
    return cart;
}

function load_cartdata()
{
    const cart = loadCart()
        if (cart.items.length<1) {
            // alert('not Found')
        $('.cartsdata').hide()
        $('.cartmsg').show()


        }

        else{

            cart.items.forEach(function(item,index) {

                $('#cart_table').append(`<tr>
                <td class="product-item-img"><img src="${item.image}" alt="/"></td>
                <td class="product-item-name">${item.name}</td>
                <td class="product-item-price">₹${item.price}</td>
                <td class="product-item-quantity">
                <div class=" btn-quantity style-1 me-3" style="display:  flex; justify-content: space-between; align-items: center;">
                <button class="p-2 minus-cart" data-index=${index} style="background-color: black; color: white;border-radius: 100%;" ><i class="fa-solid fa-minus"></i></button>
                <input style="margin: 10px !important;" type="text" value="${item.quantity}" name=""> 
                <button class="p-2 plus-cart" data-index=${index} style="background-color: black; color: white;border-radius: 100%;" ><i class="fa-solid fa-plus"></i></button>
                

            </div>
                    
                </td>
                <td class="product-item-totle">₹${item.subtotal}</td>
                <td class="product-item-close" ><a href="javascript:void(0);" style="display: flex;align-items: center; justify-content: center;"><i class="fa fa-trash-o"></i></a></td>

            </tr>`);
            });

        }  
        updateCartTotal(cart)




}


  








