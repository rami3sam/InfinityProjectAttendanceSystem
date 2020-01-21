setInterval(refresh_detected_students,100);

function refresh_detected_students(){
$.ajax({
    url: "recognized_students",
    cache: false,
    success: function(html){
      $("#recognized_students").text(html);
    }
});
}