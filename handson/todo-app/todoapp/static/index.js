$(document).ready(function(e){
   $('h5').on('click',function(){
      $('.add').stop().slideToggle();
   });
})

$(document).ready(function(e){
   $('.love').on('click',function(){
      $('.newtab').stop().slideToggle();
   });
})

function check(){
    var flag = 0;
    if(document.main_form.content.value == ''){
        flag = 1;
    }
    else if(document.main_form.tab.value == ''){
        flag = 1;
    }

    if(flag){
        window.alert('未入力の項目がありました。タブが未作成の場合はサイドバーから作成してください。');
        return false;
    }
    else{
        return true;
        }
    }

$('[data-toggle="tooltip"]').tooltip();

//$(functin(){
//    $('submit_btn').on('click', function(){
//        if($('#content').val() === '')})})


// $(document).ready(function(e){
//    $('.info{{task.id}}').on('click',function(){
//        $('.memo{{task.id}}').stop().slideToggle();
//    });
//    })  


// $(function() {

// if (localStorage.getitem('memo')){
//    $('#memo').val(localStorage.getitem('memo'));
// }

// $('#clear').click(function() {
//    $('#memo').val('');
//    localStorage.removeItem('memo');
// });

// $('#save').click(function() {
//    localStorage.setItem('memo', $('#memo').val());
// });

// });
