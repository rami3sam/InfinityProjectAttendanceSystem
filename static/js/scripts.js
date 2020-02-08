
setInterval(refreshDetectedStudents,100);
function refreshDetectedStudents(){

$.ajax({
    url: "recognized_students",
    cache: false,
    success: function(jsonText){
      
      
      var tableContents ='<table class="table table-striped">';
      tableContents+='<tr><th id="camColor">Camera:</th><th id="columnID">Identifier:</th><th id="columnName">Name:</th></tr>';
      //Create table elements
      var json = JSON.parse(jsonText);
      for(let key in json){
        var studentID = key.toString().padStart(4,'0');
        var studentName=json[key]['name'];
        var colorsCount = json[key]['colorMarkers'].length;
        var colorSize = 100/colorsCount;

        var colorStyle = 'background: repeating-linear-gradient(90deg,';
        var colorIndex = 0;
        for (value of json[key]['colorMarkers']){
          colorStyle+= value + ' ' + colorIndex*colorSize + '% ,';
          colorStyle+= value + ' ' + (colorIndex+1)*colorSize + '% ,';
          colorIndex++;
        };
        colorStyle = colorStyle.substring(0, colorStyle.length - 1);

        colorStyle+=');';
        tableContents += '<tr>';
        tableContents += '<td><div class="square" style="' +colorStyle+ '"></div></td>';
        tableContents += '<td>'+studentID+'</td>';
        tableContents += '<td>'+studentName+'</td>';
        tableContents += '<tr>';
        
      }
      tableContents+='</table>';
      $('#divStudentsTable').html(tableContents);
    }
});
}// end of function

function changeCamera(cameraURL){
  $('#video').attr('src',('video_viewer/' + cameraURL));
}