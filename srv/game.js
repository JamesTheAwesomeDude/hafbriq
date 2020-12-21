function initializeGame() {
	try {_initializeGame();}
	catch (error) {
		console.error(error);
		alert(error);
	}
	setTimeout(()=>window.location.reload(alert("Page content expired\n\nPress OK to reload.")),1000*60*5);
}

function _initializeGame() {
	var X = _loadGame();
	var e = renderField(X);
	e_old = document.querySelector('a[href^="javascript:initializeGame("]');
	if(e_old) e_old.replaceWith(e);
	else document.body.prepend(e);
}

function renderField(X=[[{name:"james",id:417,hp:99,ap:69,clan:'紫'},null],[null,null]], es=["table","tr","td","span"]) {
	var e = document.createElement(es[0]);
	var clanLeaderboard = {};
	var y = -1;
	var x = -1;
	X.forEach(r => {
		y += 1 ; x = -1;

		let e_r = document.createElement(es[1]);
		r.forEach(c => {
			x += 1;

			let e_c = document.createElement(es[2]);
			if(c != null) {
				for(let a in c) {
					e_c.setAttribute(`data-${a}`, c[a]);
					e_c.classList.add(`has-${a}`);
					let e_a = document.createElement(es[3]);
					e_a.innerText = c[a];
					e_a.classList.add(`data-${a}`);
				}
				if('id' in c) {
					//e_c.innerText=c['id'];
					e_c.appendChild(
					 document.createElement('img')
					).setAttribute("src", `avatars/${c['id']}.jpg`);
				}
				if('clan' in c && 'hp' in c && 'ap' in c) {
					let clan = c['clan'];
					let power = c['hp'] + c['ap'];
					let coords = [x, y];
					if(  (!(clan in clanLeaderboard)) || power > clanLeaderboard[clan][0]  ) {
						clanLeaderboard[clan]=[power,coords];
					} else if(power == clanLeaderboard[clan][0]) {
						clanLeaderboard[clan] = [power,null];
					}
				}
			} else {
				e_c.innerHTML='&nbsp;';
			}

			e_r.appendChild(e_c);
		});
		e.appendChild(e_r);
	});
	for(let clan in clanLeaderboard) {
		if(clanLeaderboard[clan][1] != null) {
			let [x, y] = clanLeaderboard[clan][1];
			e.childNodes[y].childNodes[x].classList.add("leader");
		}
	}
	return e;
}

function _loadGame() {
	var xhr = new XMLHttpRequest();
	xhr.open('GET', 'board', false);
//	xhr.responseType='json';
	xhr.send();
	if((xhr.status/100|0) != 2) throw xhr;
	var r = JSON.parse(xhr.responseText);
//	return xhr.response;
	return r;
}

function _takeAction(action,target) {
	var xhr = new XMLHttpRequest();
	xhr.open('POST', 'move', false);
	xhr.send(JSON.stringify({'cmd': action, 'target': target}));
	if((xhr.status/100|0) != 2) throw xhr;
	var r = JSON.parse(xhr.responseText);
	return r;
}

function _updatePrefs() {
	var xhr = new XMLHttpRequest();
	xhr.open('PUT', 'pref', false);
	xhr.send();
	if((xhr.status/100|0) != 2) throw xhr;
	var r = JSON.parse(xhr.responseText);
	return r;
}

function _forgetId() {
	document.cookie = 'id= ; max-age=0';
}

function _forgetClan() {
	document.cookie = 'clan= ; max-age=0';
}

function _selectClan(event) {
	document.cookie = `clan=${encodeURIComponent(event.target.value)}; max-age=1234567`;
}
