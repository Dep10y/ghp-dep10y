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
        shrekt_stuff[to_shrek.substring(0, to_shrek.lastIndexOf("/")+1)] = 1;
    });
    shrekt_return = [];
    for(key in shrekt_stuff) {
        shrekt_return.push(key);
    }
    return shrekt_return;
}

function slash(dot) {
    count = 0;
    dot.split("").forEach(function(x) {
        if(x == '/') count++;
    });
    return count;
}

function constructNodeGivenAStringThatTheNodeRepresentsHelloMrStueben(x) {
    return {label: x, children: [], 
        url: "/editor/editor.html#" + window.shreks[0] + ":" + window.shreks[1] + ":" + x.slice(1)};
}

function construct_things(id) {
    save_code();
    var files = find_by_project(id, function(files) {
        var folders = find_folders(files);
        var rfiles = [];
        files.forEach(function(qr) {
            if(folders.indexOf(qr) == -1) {
                rfiles.push("/" + qr);
            }
        });
        console.log(rfiles);
        console.log(folders);
        stuff = {}
        folders.forEach(function(a) {
            yeah = [];
            rfiles.forEach(function(b) {
                if(b.indexOf(a) == 0 && (slash(a) == slash(b))) {
                    yeah.push(b);
                }
            });
            stuff[a] = yeah
        });
        console.log(stuff);
        slashes = stuff['/'];
        delete stuff['/'];
        hue = {};
        hue = {label: '/', children: []}
        slashes.forEach(function(qwaszx) {
            hue.children.push(constructNodeGivenAStringThatTheNodeRepresentsHelloMrStueben(qwaszx));
        });
        for(var key in stuff) {
            var cur = constructNodeGivenAStringThatTheNodeRepresentsHelloMrStueben(key);
            stuff[key].forEach(function(ruc) {
                cur.children.push(constructNodeGivenAStringThatTheNodeRepresentsHelloMrStueben(ruc));
            });
            hue.children.push(cur);
        }
        console.log(hue);
        var nodes = [];
        nodes.push(hue);
        console.log("WHAT FOLLOSW IS SHREKT");
        console.log(nodes);
        $("#stueben").tree({data: nodes});
        $("#stueben").bind("tree.click", function(e) {
            var node = e.node;
            location.href = "/editor/editor.html#" + window.shreks[0] + ":" + window.shreks[1] + ":" + node.label.slice(1);
            location.reload();
        });
    });
}
