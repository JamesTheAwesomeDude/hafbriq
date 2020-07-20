<?php
error_reporting(-1);
ini_set('display_errors', 'On');
switch ($_SERVER['REQUEST_METHOD']) {
 case 'GET':
	header('Content-Type: application/json');
	if (!file_exists("state.json") or file_get_contents("state.json")=="" or file_get_contents("state.json")=="null") {
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
		file_put_contents("state.json","[[null,{\"id\":$id,\"hp\":99,\"ap\":3$cstr,\"r\":3},null],[null,null,null],[null,null,null]]");
	 }
	print(file_get_contents("state.json"));
	return;
 break;
 case 'POST':
	$inp=json_decode(file_get_contents('php://input'));
	$X=json_decode(file_get_contents("state.json"));
	
	if ($inp->action=='PUT'){
		file_put_contents("state.json",$inp->field);
		print('{"status":"success"}');
		return;
	}

	//TODO authenticate lolol
	if (!isset($_COOKIE['id'])) {
		header("HTTP/1.1 401 Unauthorized");
		print('{"status":"error","type":"unidentifiedPlayer"}');
		return;
	}
	$id=$_COOKIE['id'];

	$actor=null;
	foreach ($X as $y => $r) {
		foreach ($r as $x => $c) {
//			var_dump($c);
			if ($c and strval($c->id)==strval($id)) {
				$actor=$X[$y][$x];
				break 2;
			}
		}
	}
	if (!$actor and $inp->action!='PUT') {
		header("HTTP/1.1 400 Bad Request");
		print('{"status":"error","type":"unidentifiedPlayer"}');
		return;
	}
	
	$xt=$inp->target[0];
	$yt=$inp->target[1];
	$target=$X[$yt][$xt];
	
	switch ($inp->action) {
	 case 'move':
		if (!( ($actor->ap) >= (
		  abs($xt-$x)
		 +
		  abs($xt-$y)
		) )) {
		}
		if ($target) {
			//TODO: fix bug where you can "dash thru" other players
			header("HTTP/1.1 400 Bad Request");
			print('{"status":"error","type":"playerCollision"}');
			return;
		}
	
		$actor->ap--;
		$X[$yt][$xt]=$actor;
		$X[$y][$x]=null;
		file_put_contents("state.json",json_encode($X));
		header("HTTP/1.1 205 Reset Content");
		print('{"status":"success"}');
		return;
	 break;
	 case 'gift':
		if (!( $actor->r >= (
		  abs($xt-$x)
		 +
		  abs($xt-$y)
		) )) {
			header("HTTP/1.1 400 Bad Request");
			print('{"status":"error","type":"rangeDeficiency"}');
			return;
		}
		if (!( $actor->ap >= 1 )) {
			header("HTTP/1.1 400 Bad Request");
			print('{"status":"error","type":"apDeficiency"}');
			return;
		}
		
		$actor->ap--;
		$target->ap++;
		file_put_contents("state.json",json_encode($X));
		header("HTTP/1.1 205 Reset Content");
		print('{"status":"success"}');
		
	 break;
	 case 'attack':
		if (!( ($actor->r) >= (
		  abs($xt-$x)
		 +
		  abs($xt-$y)
		) )) {
			header("HTTP/1.1 400 Bad Request");
			print('{"status":"error","type":"rangeDeficiency"}');
			return;
		}
		if (!( $actor->ap >= 1 )) {
			header("HTTP/1.1 400 Bad Request");
			print('{"status":"error","type":"apDeficiency"}');
			return;
		}
		
		$actor->ap--;
		$target->hp--;
		file_put_contents("state.json",json_encode($X));
		header("HTTP/1.1 205 Reset Content");
		print('{"status":"success"}');
		
	 break;
	 case 'upgrade':
		if ( $target!=$actor ) {
			header("HTTP/1.1 400 Bad Request");
			print('{"status":"error","type":"upgradeTargetingError"}');
			return;
		}
	 break;
	}
 break;
 default:
	header("HTTP/1.1 405 Method Not Allowed");
	print('{"status":"error","type":"methodNotAllowed"}');
}

//code should NOT still be running
header("HTTP/1.1 500 Internal Server Error");
print('{"status":"error"}');
?>
