
setInterval(refreshDetectedStudents,100);
function refreshDetectedStudents(){

$.ajax({
    url: "recognized_students",
    cache: false,
    success: function(jsonText){
      
      
      var tableContents ='<table class="table table-striped">';
      tableContents+='<tr><th id="columnID">Identifier:</th><th id="columnName">Name:</th></tr>';
      //Create table elements
      var json = JSON.parse(jsonText);
      for(let key in json){
        var id = key.toString().padStart(4,'0');
        var studentName=json[key];
        tableContents += '<tr><td>'+id+'</td><td>'+studentName+'</td><tr>';
        
      }
      tableContents+='</table>';
      $('#divStudentsTable').html(tableContents);
    }
});
}// end of function
