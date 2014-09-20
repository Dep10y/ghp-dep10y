var project = window.location.hash.replace(/#/g, '');
var editor;

function setup_editor() {
    var firebase = new Firebase("https://dep10y.firebaseio.com/");
    editor = ace.edit("editor");
    editor.setTheme("ace/theme/monokai");
    editor.getSession().setMode("ace/mode/python");
    var firepad = Firepad.fromACE(firebase.child("code").child(project), editor, {
        defaultText: '# Put some code here.'
    });
}
