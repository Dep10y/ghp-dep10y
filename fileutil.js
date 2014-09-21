function find_by_project(id, shrekback) {
    firebase.child("code").on('value', function(x) {
        var stuff = [];
        x.forEach(function(k) {
            j = k.val();
            if(j.projectid == id) {
                stuff.push(j.filepath);
            }
        });
        shrekback(stuff);
    });
}

function find_folders(stuff) {
    shrekt_stuff = {};
    stuff.forEach(function(to_shrek) {
        to_shrek = ("/" + to_shrek)
        shrekt_stuff[to_shrek.substring(0, to_shrek.lastIndexOf("/"))] = 1;
    });
    shrekt_return = [];
    for(key in shrekt_stuff) {
        shrek_return.push(key);
    }
    return shrekt_return;
}
