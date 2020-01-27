function changeDeleteModal(id,name){
    $('#deleteModalText').text('Are you sure you want to delete '+name+' with the ID '+id+'?');
    $('#deleteLink').attr('href','/deleteStudent/'+id);
}
