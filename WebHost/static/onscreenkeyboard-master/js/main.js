var kbdhasfocus = false;
var isFocused = [];
var currentid = 1;
function init() {
	document.getElementById("hover-hideable").style.display = 'none';
	jsKeyboard.init("virtualKeyboard");
	var inputs = document.getElementById('main').getElementsByTagName('input');
	for (input in inputs) {
		registerForKbd(inputs[input]);
	}
	var txtareas = document.getElementById('main').getElementsByTagName('textarea');
	for (txtarea in txtareas) {
		registerForKbd(txtareas[txtarea]);
	}
	
	
	
	
	document.getElementById("hover-hideable").setAttribute("tabindex",-1);
	document.getElementById("hover-hideable").addEventListener("focusin", kbdGotFocus);
	document.getElementById("hover-hideable").addEventListener("focusout", kbdLostFocus);

}

function kbdGotFocus() {
	kbdhasfocus = true;
}
function kbdLostFocus() {
	kbdhasfocus = false;
	hideKeyboard();
}
function registerForKbd(item) {
	try {
		item.removeEventListener("focus", function() {gotFocus(item);});
		item.addEventListener("focus", function() {gotFocus(item);});
		item.removeEventListener("focusout", function() {lostFocus(item);});
		item.addEventListener("focusout", function() {lostFocus(item);});
		if (item.id=="") {
			item.id = currentid;
			currentid = currentid+1;
		}
		isFocused[item.id] = false;
	}
	catch (e) {
		//do nothing! Just ignore error. Probably an invalid item.
	}
}
function lostFocus(item) {
	isFocused[item.id] = false;
	setTimeout(function(){ // wait 10 seconds first, to allow keyboard to get focus first
		if (!elementInFocus(item.id)) {
			hideKeyboard();
		}
	}, 10);
}
function gotFocus(item) {
	isFocused[item.id] = true;
	showKeyboard();
}

function elementInFocus(ignore=NULL) {
	for (id in isFocused) {
		if (id!=ignore) {
			if (isFocused[id]) {
				return true;
			}
		}
	}
	return kbdhasfocus;
}

function showKeyboard() {
	document.getElementById("hover-hideable").style.display = 'block';
	kbdheight = document.getElementById("hover-hideable").clientHeight;
	mainheight = window.innerHeight - kbdheight;
	document.getElementById("main").style.height = mainheight+"px";
	//document.getElementById("main").style.height = "70%"; // fallback if previous line malfunctions
}

function hideKeyboard() {
	document.getElementById("hover-hideable").style.display = 'none';
	document.getElementById("main").style.height = "100%";
}

init();