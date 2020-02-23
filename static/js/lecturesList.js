function changeDeleteModal(name){
    $('#deleteModalText').text('Are you sure you want to delete '+name+'?');
    var nameURI = encodeURI(name)
    $('#deleteLink').attr('href','/deleteLecture/'+nameURI);
}
