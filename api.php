<?php
error_reporting(-1);
ini_set('display_errors', 'On');
if ($_SERVER['REQUEST_METHOD'] == 'GET') {
	header('Content-Type: application/json');
	if (!file_exists("state.json") or file_get_contents("state.json")=="") {
		if (isset($_COOKIE['id'])) {
			$id = $_COOKIE['id'];
		} else {
			$ids = array_diff(scandir("avatars",SCANDIR_SORT_NONE), array('..', '.'));
			$id = pathinfo($ids[array_rand($ids)],PATHINFO_FILENAME);
			setcookie('id',"$id");
		}
		if (isset($_COOKIE['clan'])) {
			$clan = $_COOKIE['clan'];
			$cstr = ",\"clan\":\"$clan\"";
		} else {
			$cstr="";
		}
		file_put_contents("state.json","[[null,{\"id\":$id,\"hp\":99,\"ap\":3$cstr},null],[null,null,null],[null,null,null]]");
	 }
	print(file_get_contents("state.json"));
	return;
} else if ($_SERVER['REQUEST_METHOD'] == 'POST') {
	$x=json_decode(file_get_contents('php://input'));
	if ($x->action=='save') {
		file_put_contents("state.json",$x->field);
	}
}
//code should NOT still be running
header("HTTP/1.1 500 Internal Server Error");
?>
