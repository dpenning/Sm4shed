// get username and session_id
var check_counter = 0;
var username = getCookie("username");
var session_id = getCookie("session_id");

var refresh_timeout = 1000;

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
}

function check_matchmaking() {
	if (window.XMLHttpRequest) {
		xmlhttp = new XMLHttpRequest();
	}
	xmlhttp.onreadystatechange=function() {
		if (xmlhttp.readyState==4 && xmlhttp.status==200) {
			output = JSON.parse(xmlhttp.responseText);
			output_table = document.createElement("TABLE");
			for (key in output) {
				row = output_table.insertRow(-1);
				key_cell = row.insertCell(0);
				val_cell = row.insertCell(1);

				key_cell.innerHTML = key.toString();
				val_cell.innerHTML = output[key].toString();
			}

			document.getElementById("wait_screen").innerHTML = '';
			document.getElementById("wait_screen").appendChild(output_table);
			if ("success" in output && output["success"] == true) {
				setTimeout(function() {check_matchmaking()}, refresh_timeout);
			}
		}
	}
	xmlhttp.open("POST","/check",true);
	xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	xmlhttp.send("username=" + username + "&session_id=" + session_id);
}

function cancel_matchmaking() {
	if (window.XMLHttpRequest) {
		xmlhttp = new XMLHttpRequest();
	}
	xmlhttp.onreadystatechange=function() {
		if (xmlhttp.readyState==4 && xmlhttp.status==200) {}
	}
	xmlhttp.open("POST","/cancel",true);
	xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	xmlhttp.send("username=" + username + "&session_id=" + session_id);
}

window.onbeforeunload = function() {cancel_matchmaking()};