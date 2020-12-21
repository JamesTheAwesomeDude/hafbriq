const playerNames = ["🍇", "🍈", "🍉", "🍊", "🍋", "🍌", "🍍", "🥭", "🍎", "🍏", "🍐", "🍑", "🍒", "🍓", "🥝", "🍅", "🥥", "🥑", "🍆", "🥔", "🥕", "🌽", "🌶️", "🥒", "🥬", "🥦", "🧄", "🧅", "🍄", "🥜", "🌰", "🍞", "🥐", "🥖", "🥨", "🥯", "🥞", "🧇", "🧀", "🍖", "🍗", "🥩", "🥓", "🍔", "🍟", "🍕", "🌭", "🥪", "🌮", "🌯", "🥙", "🧆", "🥚", "🍳", "🥘", "🍲", "🥣", "🥗", "🍿", "🧈", "🧂", "🥫", "🍱", "🍘", "🍙", "🍚", "🍛", "🍜", "🍝", "🍠", "🍢", "🍣", "🍤", "🍥", "🥮", "🍡", "🥟", "🥠", "🥡", "🦪", "🍦", "🍧", "🍨", "🍩", "🍪", "🎂", "🍰", "🧁", "🥧", "🍫", "🍬", "🍭", "🍮", "🍯", "🍼", "🥛", "☕", "🍵", "🍶", "🍾", "🍷", "🍸", "🍹", "🍺", "🍻", "🥂", "🥃", "🥤", "🧃", "🧉", "🧊", "🥢"];

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
	e_old = document.querySelector('a[href*="javascript:initializeGame"]');
	if(e_old) e_old.replaceWith(e);
	else document.body.prepend(e);
}

function renderField(X=[[{name:"james",id:417,hp:99,ap:69,clan:'紫'},null],[null,null]], es=["table", "tr", "td", "p"]) {
	let e = document.createElement(es[0]);
	let clanLeaderboard = {};

	let y = -1;
	let x = -1;
	X.forEach(row => {
		x = -1;
		y += 1;

		let e_row = document.createElement(es[1]);
		row.forEach(cell => {
			x += 1;

			let e_cell = document.createElement(es[2]);

			if(cell != null) {

				let id = cell['id'];
				let e_inner = document.createElement(es[3]);
				console.log(id);
				e_inner.innerText = playerNames[id % playerNames.length];

				for(let attr in cell) {
					let val = cell[attr];
					e_cell.setAttribute(`data-${attr}`, val);
					e_cell.classList.add(`has-${attr}`);
					e_cell.title += `${attr}: ${val}\n`;
				}

				if(('clan' in cell) && (cell['clan'] != null)) {
					const clan = cell['clan'];
					const power = cell['hp'] + cell['ap'] + cell['range'];
					const coords = [x, y]; Object.freeze(coords);
					e_cell.classList.add("has-clan");
					e_cell.setAttribute("data-clan");
					if(!(clan in clanLeaderboard) || clanLeaderboard[clan][0] < power) {
						//New leader
						clanLeaderboard[clan] = [power, coords];
					} else if(clanLeaderboard[clan][0] == power) {
						//No leader
						clanLeaderboard[clan] = [power, null];
					}
				}

				e_cell.appendChild(e_inner);

			} else {
				e_cell.innerHTML='&nbsp;';
			}

			e_row.appendChild(e_cell);
		});
		e.appendChild(e_row);
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

function changeClan(event) {
	_selectClan(event.target.value);
	try {
		_updatePrefs();
	} catch(err) {
		if(err.status == 401) {
			window.location.href = './login';
		} else {
			throw err;
		}
	}
}

function _forgetId() {
	document.cookie = 'id= ; max-age=0';
}

function _forgetClan() {
	document.cookie = 'clan= ; max-age=0';
}

function _selectClan(clan) {
	document.cookie = `clan=${encodeURIComponent(clan)}; max-age=1234567`;
}
