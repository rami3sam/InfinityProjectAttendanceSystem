
setInterval(refreshDetectedStudents,100);
function refreshDetectedStudents(){

$.ajax({
    url: "recognized_students",
    cache: false,
    success: function(jsonText){
      
      var studentTable = $('#studentsTable');
      studentTable.children().remove();
      //Create table heading
      var trhead=$('<tr>');
      var idHead=$('<th>' ).text("Identifier:");
      var nameHead=$('<th>').text("Name:");
      trhead.append(idHead);
      trhead.append(nameHead);
      studentTable.append(trhead);

      //Create table elements
      var json = JSON.parse(jsonText);
      for(let key in json){
        var id = key.toString().padStart(4,'0');
        var tr=$('<tr>');
        var idCell=$('<td>').text(id);
        var studentNameCell=$('<td>').text(json[key]);
        tr.append(idCell);
        tr.append(studentNameCell);
        studentTable.append(tr);
       
      }
    }
});
}// end of function
