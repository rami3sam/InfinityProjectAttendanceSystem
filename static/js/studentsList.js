function changeDeleteModal(id,name){
    $('#deleteModalText').text('Are you sure you want to delete '+name+'?');
    $('#deleteLink').attr('href','/deleteStudent/'+id);
}
