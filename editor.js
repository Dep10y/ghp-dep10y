var projec = window.location.hash.replace(/#/g, '');
var project = projec.replace(/\./g, '-').replace(/\//g, '-');
var editor;
var firebase;
$("#jcollab").hide();


function init() {
    save_code();
    projec = window.location.hash.replace(/#/g, '');
    project = projec.replace(/\./g, '-').replace(/\//g, '-');
    $("#editor").html("");
    setup_editor();
    setup_stuff();
}

function save_code() {
    firebase.child("code").child(project).child("text").set(editor.getSession().getValue());
}

function setup_editor() {
    firebase = new Firebase("https://dep10y.firebaseio.com/");
    editor = ace.edit("editor");
    editor.setTheme("ace/theme/monokai");
    var type = firebase.child("projects").child(project).child("type");
    if (type == 'flask'){
        editor.getSession().setMode("ace/mode/python");
    }
    if (type == 'sinatra'){
        editor.getSession().setMode("ace/mode/ruby");
    }
    if (type == 'php'){
        editor.getSession().setMode("ace/mode/php");
    }
    console.log("THE FIREPAD IS " + project);
    var firepad = Firepad.fromACE(firebase.child("code").child(project), editor, {
        defaultText: ''
    });
    $(window).bind('beforeunload', function() {
        save_code();
    });
}

function setup_stuff() {
    var shreks = projec.split(":");
    firebase.child("code").child(project).update({user: shreks[0], projectid: shreks[1], filepath: shreks[2]});
    var shrek2 = shreks[2].split(".");
    var shrek = shrek2[shrek2.length - 1];
    window.shreks = shreks;
    editor.getSession().setMode("ace/mode/" + {py: "python", html: "html", rb: "ruby"}[shrek]);
    $("#filename").html(shreks[2]);
    firebase.child("projects").child(shreks[0]).child(shreks[1]).child("name").on("value", function(q) {
        $("#projectname").html(q.val());
    });
    firebase.child("projects").child(shreks[0]).child(shreks[1]).child("state").on("value", function(q){
        var staturl = /Running at ([a-z0-9\.]+)/g.exec(q.val());
        if (staturl && staturl.length > 1){
            $("#projurl").html(staturl[1]);
        }
    });

    construct_things(shreks[1]);
}
function restore() {
	$("#depBut").html("Deploy");
}
function push_that_button() {
    save_code();
    $("#depBut").html("Deploying...");
    window.setTimeout(restore, 10000);
    firebase.child("code").once("value", function(v) {
        forreal = []
        v.forEach(function(x) {
            console.log(window.shreks);
            console.log(x.val());
            if(x.val().projectid == window.shreks[1]) {
                forreal.push(x.val());
            }
        });
        forreal.forEach(function(x) {
            firebase.child("files").child(window.shreks[1]).push({
                filepath: x.filepath,
                text: x.text
            });
        });
    });
}
$("#collab").attr("onclick", "javascript:void window.open('collab.html#"+project+"','1411307004190','width=700,height=500,toolbar=0,menubar=0,location=0,status=1,scrollbars=1,resizable=1,left=0,top=0');return false;");

var moxtrameet;
firebase.child("code").child(project).child("moxtrameet").on("value", function(q){
        moxtrameet = q.val();
        $("#jcollab").show();
        $("#jcollab").attr("onclick", "javascript:void window.open('jcollab.html#"+moxtrameet+"','1411307004190','width=700,height=500,toolbar=0,menubar=0,location=0,status=1,scrollbars=1,resizable=1,left=0,top=0');return false;");
        
    });
