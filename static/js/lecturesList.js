function changeDeleteModal(id,name){
    $('#deleteModalText').text('Are you sure you want to delete '+name+'?');
    var nameURI = encodeURI(id)
    $('#deleteLink').attr('href','/deleteLecture/'+nameURI);
}
