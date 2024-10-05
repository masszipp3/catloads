/**
    * selectImages
    * menuleft
    * tabs
    * progresslevel
    * collapse_menu
    * fullcheckbox
    * showpass
    * gallery
    * coppy
    * select_colors_theme
    * icon_function
    * box_search
    * preloader
*/


$(function () {
  var $keyword = $('#countrysearch');
  var $searchdiv = $('#country_box');


  function debounce2(func, wait, immediate) {
    var timeout;
    return function () {
      var context = this, args = arguments;
      var later = function () {
        timeout = null;
        if (!immediate) func.apply(context, args);
      };
      var callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func.apply(context, args);
    };
  }

  var handleInput = debounce2(function () {
    var value = $keyword.val().trim();
    let url = window.location.href

    if (value.length > 1) {
      $.ajax({
        type: 'GET',
        url: url,
        data: { 'search': value },
        success: function (response) {
          $searchdiv.empty()
          const countries = response.contries
          for (i = 0; i < countries.length; i++) {
            var context = `<li class="product-item gap14">
                        <div class="image no-bg">
                            <img src="" alt="">
                        </div>
                        <div class="flex items-center justify-between gap20 flex-grow">
                            <div class="name">
                                <a class="body-title-2">${countries[i].name}</a>
                            </div>
                            <div class="body-text">${countries[i].code}</div>
                            <div class="body-text">${countries[i].symbol}</div>
                            <div class="body-text">${countries[i].status}</div>
                           
                            <div class="list-icon-function">
                               
                                <div class="item edit">
                                    <a style="text-decoration: none !important;" href="${countries[i].edit_link}"><i style="color: green;" class="icon-edit-3"></i></a> 

                                </div>
                                <div class="item trash">
                                    <a style="text-decoration: none !important;" onclick="return confirm('Are you Sure..?')" href="${countries[i].delete_link}"> <i style="color: red;" class="icon-trash-2"></i></a>

                                </div>
                            </div>
                        </div>
                    </li>`
            $searchdiv.append(context)
          }
        },
        error: function (xhr) {
          console.error(xhr.responseText);
        }
      });
    } else {
      window.location.reload()
    }
  }, 250);

  $keyword.on('input', handleInput);

})


$(function () {
  var $keyword = $('#order_search');
  var $searchdiv = $('#order_box');
  function debounce2(func, wait, immediate) {
    var timeout;
    return function () {
      var context = this, args = arguments;
      var later = function () {
        timeout = null;
        if (!immediate) func.apply(context, args);
      };
      var callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func.apply(context, args);
    };
  }

  var handleInput = debounce2(function () {
    var value = $keyword.val().trim();
    let url = window.location.href

    if (value.length >= 1) {
      $.ajax({
        type: 'GET',
        url: url,
        data: { 'search': value },
        success: function (response) {
          $searchdiv.empty()
          const orders = response.orders
          console.log(orders)
          for (i = 0; i < orders.length; i++) {
            var context = `<li class="product-item gap14">
                        
                        <div class="image no-bg">
                            <img src="" alt="">
                        </div>
                        <div class="flex items-center justify-between gap20 flex-grow">
                            <div class="body-text">${orders[i].order_id}</div>
                            <div class="body-text">${orders[i].amount}</div>
                            <div class="body-text">${orders[i].count}</div>
                            <div class="body-text">${orders[i].date}</div>
                            <div>
                                <div class="block-available">${orders[i].status}</div>
                            </div>
                            <!-- <div>
                                <div class="block-tracking">Tracking</div>
                            </div> -->   
                            <div class="list-icon-function">
                                <div class="item edit">
                                    <a style="text-decoration: none !important;" href="${orders[i].edit_link}"><i style="color: green;" class="icon-edit-3"></i></a> 

                                </div>
                                <div class="item trash">
                                    <a style="text-decoration: none !important;" onclick="return confirm('Are you Sure..?')" href="${orders[i].delete_link}"> <i style="color: red;" class="icon-trash-2"></i></a>

                                </div>
                            </div>
                        </div>
                    </li>`
            $searchdiv.append(context)
          }
        },
        error: function (xhr) {
          console.error(xhr.responseText);
        }
      });
    } else {
      window.location.reload()
    }
  }, 250);

  $keyword.on('input', handleInput);

})

  



; (function ($) {

  "use strict";

  var selectImages = function () {
    if ($(".image-select").length > 0) {
      const selectIMG = $(".image-select");
      selectIMG.find("option").each((idx, elem) => {
        const selectOption = $(elem);
        const imgURL = selectOption.attr("data-thumbnail");
        if (imgURL) {
          selectOption.attr(
            "data-content",
            "<img src='%i'/> %s"
              .replace(/%i/, imgURL)
              .replace(/%s/, selectOption.text())
          );
        }
      });
      selectIMG.selectpicker();
    }
  };

  var menuleft = function () {
    if ($('div').hasClass('section-menu-left')) {
      var bt = $(".section-menu-left").find(".has-children");
      bt.on("click", function () {
        var args = { duration: 200 };
        if ($(this).hasClass("active")) {
          $(this).children(".sub-menu").slideUp(args);
          $(this).removeClass("active");
        } else {
          $(".sub-menu").slideUp(args);
          $(this).children(".sub-menu").slideDown(args);
          $(".menu-item.has-children").removeClass("active");
          $(this).addClass("active");
        }
      });
      $('.sub-menu-item').on('click', function (event) {
        event.stopPropagation();
      });
    }
  };

  var tabs = function () {
    $('.widget-tabs').each(function () {
      $(this).find('.widget-content-tab').children().hide();
      $(this).find('.widget-content-tab').children(".active").show();
      $(this).find('.widget-menu-tab').find('li').on('click', function () {
        var liActive = $(this).index();
        var contentActive = $(this).siblings().removeClass('active').parents('.widget-tabs').find('.widget-content-tab').children().eq(liActive);
        contentActive.addClass('active').fadeIn("slow");
        contentActive.siblings().removeClass('active');
        $(this).addClass('active').parents('.widget-tabs').find('.widget-content-tab').children().eq(liActive).siblings().hide();
      });
    });
  };

  $('ul.dropdown-menu.has-content').on('click', function (event) {
    event.stopPropagation();
  });
  $('.button-close-dropdown').on('click', function () {
    $(this).closest('.dropdown').find('.dropdown-toggle').removeClass('show');
    $(this).closest('.dropdown').find('.dropdown-menu').removeClass('show');
  });

  var progresslevel = function () {
    if ($('div').hasClass('progress-level-bar')) {
      var bars = document.querySelectorAll('.progress-level-bar > span');
      setInterval(function () {
        bars.forEach(function (bar) {
          var t1 = parseFloat(bar.dataset.progress);
          var t2 = parseFloat(bar.dataset.max);
          var getWidth = (t1 / t2) * 100;
          bar.style.width = getWidth + '%';
        });
      }, 500);
    }
  }

  var collapse_menu = function () {
    $(".button-show-hide").on("click", function () {
      $('.layout-wrap').toggleClass('full-width');
    })
  }

  var fullcheckbox = function () {
    $('.total-checkbox').on('click', function () {
      if ($(this).is(':checked')) {
        $(this).closest('.wrap-checkbox').find('.checkbox-item').prop('checked', true);
      } else {
        $(this).closest('.wrap-checkbox').find('.checkbox-item').prop('checked', false);
      }
    });
  };

  var showpass = function () {
    $(".show-pass").on("click", function () {
      $(this).toggleClass("active");
      var input = $(this).parents(".password").find(".password-input");

      if (input.attr("type") === "password") {
        input.attr("type", "text");
      } else if (input.attr("type") === "text") {
        input.attr("type", "password");
      }
    });
  }

  var gallery = function () {
    $(".button-list-style").on("click", function () {
      $(".wrap-gallery-item").addClass("list");
    });
    $(".button-grid-style").on("click", function () {
      $(".wrap-gallery-item").removeClass("list");
    });
  }

  var coppy = function () {
    $(".button-coppy").on("click", function () {
      myFunction()
    });
    function myFunction() {
      var copyText = document.getElementsByClassName("coppy-content");
      navigator.clipboard.writeText(copyText.text);
    }
  }

  var select_colors_theme = function () {
    if ($('div').hasClass("select-colors-theme")) {
      $(".select-colors-theme .item").on("click", function (e) {
        $(this).parents(".select-colors-theme").find(".active").removeClass("active");
        $(this).toggleClass("active");
      })
    }
  }

  var icon_function = function () {
    if ($('div').hasClass("list-icon-function")) {
      $(".list-icon-function .trash").on("click", function (e) {
        $(this).parents(".product-item").remove();
        $(this).parents(".attribute-item").remove();
        $(this).parents(".countries-item").remove();
        $(this).parents(".user-item").remove();
        $(this).parents(".roles-item").remove();
      })
    }
  }

  var box_search = function () {

    $(document).on('click', function (e) {
      var clickID = e.target.id; if ((clickID !== 's')) {
        $('.box-content-search').removeClass('active');
      }
    });
    $(document).on('click', function (e) {
      var clickID = e.target.class; if ((clickID !== 'a111')) {
        $('.show-search').removeClass('active');
      }
    });

    $('.show-search').on('click', function (event) {
      event.stopPropagation();
    }
    );
    $('.search-form').on('click', function (event) {
      event.stopPropagation();
    }
    );
    var input = $('.header-dashboard').find('.form-search').find('input');
    input.on('input', function () {
      if ($(this).val().trim() !== '') {
        $('.box-content-search').addClass('active');
      } else {
        $('.box-content-search').removeClass('active');
      }
    });

  }

  var retinaLogos = function () {
    var retina = window.devicePixelRatio > 1 ? true : false;
    if (retina) {
      if ($(".dark-theme").length > 0) {
        $('#logo_header').attr({ src: `${window.location.protocol}//${window.location.host}/static/images/logo/logo.png`, width: '154px', height: '52px' });
      } else {
        $('#logo_header').attr({ src: `${window.location.protocol}//${window.location.host}/static/images/logo/logo.png`, width: '154px', height: '52px' });

      }
    }
  };

  var preloader = function () {
    setTimeout(function () {
      $("#preload").fadeOut("slow", function () {
        $(this).remove();
      });
    }, 1000);
  };


  // Dom Ready
  $(function () {
    selectImages();
    menuleft();
    tabs();
    progresslevel();
    collapse_menu();
    fullcheckbox();
    showpass();
    gallery();
    coppy();
    select_colors_theme();
    icon_function();
    box_search();
    retinaLogos();
    preloader();

  });

})(jQuery);
