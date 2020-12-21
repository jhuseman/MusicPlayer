function encode_song_id(song) {
	return encodeURI(song).replace(/\//g,'%2F');
}

function pause() {
	WebRequest("GET","/pause/","",function(text) {
		// do nothing on return
	},function(error) {
		console.log("ERROR getting return from pause: "+error);
	});
}

function unpause() {
	WebRequest("GET","/unpause/","",function(text) {
		// do nothing on return
	},function(error) {
		console.log("ERROR getting return from unpause: "+error);
	});
}

function setVolume(vol) {
	WebRequest("GET","/set_vol/"+vol,"",function(text) {
		// do nothing on return
	},function(error) {
		console.log("ERROR getting return from setVolume: "+error);
	});
}

function skip_song() {
	WebRequest("GET","/skip_song/","",function(text) {
		// do nothing on return
	},function(error) {
		console.log("ERROR getting return from skip_song: "+error);
	});
}

function remove_from_playlist(song,callback) {
	WebRequest("GET","/del_song/"+encode_song_id(song),"",function(text) {
		// do nothing on return
		if(callback!=null) {
			callback();
		}
	},function(error) {
		console.log("ERROR getting return from del_song: "+error);
		if(callback!=null) {
			callback();
		}
	});
}

function add_to_playlist_pos(song,pos) {
	WebRequest("GET","/add_song/"+encode_song_id(song)+"/"+pos,"",function(text) {
		// do nothing on return
	},function(error) {
		console.log("ERROR getting return from add_song (pos): "+error);
	});
}

function add_to_playlist(song) {
	WebRequest("GET","/add_song/"+encode_song_id(song),"",function(text) {
		// do nothing on return
	},function(error) {
		console.log("ERROR getting return from add_song: "+error);
	});
}

function move_in_playlist(song,pos) {
	remove_from_playlist(song,function() {
		add_to_playlist_pos(song,pos);
	});
}

function random_time() {
	return 500;
	return Math.floor((Math.random() * 100) + 450);
}

function path_split(path) {
	return [path.replace(/(^.*)\/.*/, '$1'),path.replace(/^.*\//, '')];
}

function guess_info(filename) {
	var first_split = path_split(filename);
	var second_split = path_split(first_split[0]);
	var third_split = path_split(second_split[0]);
	var title = first_split[1].replace(/(^.*)\..*/, '$1');
	var album = second_split[1];
	var artist = third_split[1];
	var track = null;
	if(!isNaN(parseInt(title[0]))) {
		track = parseInt(title.replace(/(^\d*).*/, '$1'));
		title = title.replace(/(^\d*) ?/, '');
	}
	
	return {
		"title": title,
		"track": track,
		"album": album,
		"artist": artist,
		"filename": filename,
		"filepath": filename,
		"language": null,
		"year": null,
		"recorded": null,
		"genre": null,
		"composer": null,
		"published": null,
		"duration": null,
		"is_lossless": null,
		"bitrate": null
	};
}

function makediv(class_type,children) {
	var div = document.createElement('div');
	div.setAttribute("class",class_type);
	updateelemchildren(div, children);
	return div;
}

function updateelemchildren(elem, children, clear=true) {
	if(clear) {
		elem.innerHTML = '';
	}
	var i;
	for (i = 0; i < children.length; ++i) {
		if(typeof(children[i])=="string") {
			elem.appendChild(document.createTextNode(children[i]));
		} else if(typeof(children[i])=="number") {
			elem.appendChild(document.createTextNode(children[i]));
		} else if (children[i]==null || children[i]==undefined) {
			// elem.appendChild(document.createTextNode("unknown"));
		} else {
			elem.appendChild(children[i]);
		}
	}
}

function dur_to_str(duration) {
	var sec_num = duration;
	var hours   = Math.floor(sec_num / 3600);
	var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
	var seconds = Math.round(sec_num - (hours * 3600) - (minutes * 60));
	
	if (seconds < 10) {seconds = "0"+seconds;}
	if (hours==0) {
		return minutes+':'+seconds;
	} else {
		if (minutes < 10) {minutes = "0"+minutes;}
		return hours+':'+minutes+':'+seconds;
	}
}

function update_song_info_item(div,info,child_append) {
	div.innerHTML = '';
	var new_info = info;
	if(info['title']==undefined || info['title']==null) {
		new_info = guess_info(info['filename']);
	}
	var top_row_items = [
		makediv("flexheader padded",[new_info['track']]),
		makediv("flexitembasisauto4 padded bigger",[new_info['title']]),
		makediv("flexitembasisauto2 padded",[new_info['artist']]),
		makediv("flexitembasisauto2 padded",[new_info['album']]),
		makediv("flexheader padded",[new_info['year']]),
		makediv("flexitembasisauto padded",[new_info['genre']]),
		makediv("flexheader padded",[dur_to_str(new_info['duration'])]),
	]
	var top_row = makediv("flexbox_horiz_wrap fullwidth",top_row_items);
	div.appendChild(top_row);
	var bot_row_items = [
		makediv("flexitembasisauto padded smaller",['Composer: ',new_info['composer']]),
		makediv("flexitembasisauto4 padded tiny",['Filename: ',new_info['filename']]),
		child_append,
	]
	var bot_row = makediv("flexbox_horiz fullwidth",bot_row_items);
	div.appendChild(bot_row);
}

function make_song_info_item(info,child_append) {
	var div = document.createElement('div');
	update_song_info_item(div,info,child_append);
	return div;
}

window.song_info_queue = [];
window.song_info_dict = {};
function song_info_queue_handler() {
	if(window.song_info_queue.length>0) {
		var item = window.song_info_queue[0];
		var song = item['song'];
		var callback = item['callback'];
		
		WebRequest("GET","/song_info/"+encode_song_id(song),"",function(text) {
			try {
				var song_info = JSON.parse(text);
				if (song_info['filename']==song) {
					window.song_info_dict[song] = song_info;
					callback(song_info);
					window.song_info_queue = window.song_info_queue.splice(1,window.song_info_queue.length);
				}
			}
			catch(err) {
				console.log('Error processing song info: '+err.message);
			}
			window.setTimeout(song_info_queue_handler, 5);
		},function(error) {
			console.log("ERROR getting song info: "+error);
			window.setTimeout(song_info_queue_handler, 100);
		});
	} else {
		window.setTimeout(song_info_queue_handler, 100);
	}
}

function get_song_info_req(song,callback) {
	window.song_info_queue[window.song_info_queue.length] = {"song" : song, "callback" : callback};
}

function get_all_song_info(callback) {
	WebRequest("GET","/song_info/","",function(text) {
		try {
			var all_song_info = JSON.parse(text);
			for (var song in all_song_info) {
				var song_info = all_song_info[song];
				window.song_info_dict[song] = song_info;
			}
			callback();
		}
		catch(err) {
			console.log('Error processing all song info: '+err.message);
			window.setTimeout(function() {
				get_all_song_info(callback);
			}, 1000);
		}
	},function(error) {
		console.log("ERROR getting all song info: "+error);
		window.setTimeout(function() {
			get_all_song_info(callback);
		}, 1000);
	});
}

function get_song_info(song,callback) {
	if(window.song_info_dict[song]==undefined) {
		/* WebRequest("GET","/song_info/"+encode_song_id(song),"",function(text) {
			var song_info = JSON.parse(text);
			if (song_info['filename']==song) {
				window.song_info_dict[song] = song_info;
				// callback(song_info);
			}
		},function(error) {
			console.log("ERROR getting song info: "+error);
		});
		window.setTimeout(function(){ get_song_info(song,callback); }, random_time()); */
		get_song_info_req(song,callback);
	} else {
		callback(window.song_info_dict[song]);
	}
}

function makelink(child,class_type,onclk) {
	var anch = document.createElement('a');
	anch.appendChild(child);
	anch.onclick = onclk;
	anch.setAttribute("class",class_type);
	anch.href = '#';
	return anch;
}

function makeicon(icon) {
	var img = document.createElement('img');
	img.setAttribute('src',"img/"+icon+".png");
	img.setAttribute('width',"16");
	img.setAttribute('height',"16");
	return img;
}

function makeslider(min,max,step,value,onchange) {
	var slide = document.createElement('input');
	slide.setAttribute('type',"range");
	slide.setAttribute('min',min);
	slide.setAttribute('max',max);
	slide.setAttribute('step',step);
	slide.setAttribute('value',value);
	slide.addEventListener("change", function() {
		onchange(slide.value);
	}, false);
	return slide;
}

function getcurrentsonglinks(song_info,pos) {
	var play_pause = null;
	if(pos['paused']) {
		play_pause = makelink(makeicon('play'),"",function() {
			unpause();
		});
	} else {
		play_pause = makelink(makeicon('pause'),"",function() {
			pause();
		});
	}
	var links = [
		play_pause,
		makelink(makeicon('skip'),"",function() {
			skip_song();
		}),
	];
	return makediv("flexheadernoshrink",links);
}

function update_cur_song(cur_song,song_info,pos) {
	if(song_info!=undefined) {
		// cur_song.innerHTML = song_info['filename'] + pos['fraction'];
		// cur_song.innerHTML = '';
		var top_row_items = [
			makediv("flexheader padded",[song_info['track']]),
			makediv("flexitembasisauto4 padded bigger",[song_info['title']]),
			makediv("flexitembasisauto2 padded",[song_info['artist']]),
			makediv("flexitembasisauto2 padded",[song_info['album']]),
			makediv("flexheader padded",[song_info['year']]),
			makediv("flexitembasisauto padded",[song_info['genre']]),
			makediv("flexheader padded",[dur_to_str(pos['pos']),'/',dur_to_str(pos['length'])]),
		]
		if(cur_song.getElementsByClassName('cur_song_top_row')[0]==undefined) {
			cur_song.appendChild(makediv("cur_song_top_row flexbox_horiz_wrap fullwidth",top_row_items));
		} else {
			updateelemchildren(cur_song.getElementsByClassName('cur_song_top_row')[0], top_row_items);
		}
		
		var bot_row_items = [
			makediv("flexitembasisauto padded",['Composer: ',song_info['composer']]),
			makediv("flexitembasisauto4 padded tiny",['Filename: ',song_info['filename']]),
			getcurrentsonglinks(song_info,pos),
		]
		if(cur_song.getElementsByClassName('cur_song_bot_row')[0]==undefined) {
			cur_song.appendChild(makediv("cur_song_bot_row flexbox_horiz_wrap fullwidth smaller",bot_row_items));
		} else {
			updateelemchildren(cur_song.getElementsByClassName('cur_song_bot_row')[0], bot_row_items);
		}

		if(cur_song.getElementsByClassName('cur_song_progress')[0]==undefined) {
			cur_song.appendChild(makediv("cur_song_progress progress progress-striped active",[]));
		}
		if(cur_song.getElementsByClassName('cur_song_progress')[0].getElementsByClassName('cur_song_progress_bar')[0]==undefined) {
			cur_song.getElementsByClassName('cur_song_progress')[0].appendChild(makediv("cur_song_progress_bar progress-bar",[]));
		}
		var prog = pos['fraction']*100;
		cur_song.getElementsByClassName('cur_song_progress')[0].getElementsByClassName('cur_song_progress_bar')[0].style.width=prog.toString() + "%";

		var volume_val = pos['vol'];
		var volume_slider = makeslider(0,100,1,volume_val,function(new_vol) {
			setVolume(new_vol);
		});
		if(cur_song.getElementsByClassName('cur_song_volume_slider')[0]==undefined) {
			cur_song.appendChild(makediv("cur_song_volume_slider volume-slider",[volume_slider]));
		} else {
			updateelemchildren(cur_song.getElementsByClassName('cur_song_volume_slider')[0], [volume_slider]);
		}
	}
}

window.latestplaylistsongs = [];
function getplaylistlinks(song_info) {
	var songs = window.latestplaylistsongs;
	var links = [
		makelink(makeicon('up'),"",function() {
			var cur_index = songs.indexOf(song_info['filename']);
			if(cur_index>1) {
				move_in_playlist(song_info['filename'],cur_index-1);
			}
		}),
		makelink(makeicon('down'),"",function() {
			var cur_index = songs.indexOf(song_info['filename']);
			if(cur_index<(songs.length-1)) {
				move_in_playlist(song_info['filename'],cur_index+1);
			}
		}),
		makelink(makeicon('delete'),"",function() {
			var cur_index = songs.indexOf(song_info['filename']);
			remove_from_playlist(song_info['filename'],null);
		}),
	];
	return makediv("flexheadernoshrink",links);
}

function make_playlist_item(info) {
	var div = make_song_info_item(info,getplaylistlinks(info));
	var anch = makelink(div,"list-group-item",function() {
		// do nothing
	});
	// var fname = document.createTextNode(info['filename']);
	// div.appendChild(fname);
	return anch;
	// var ret = document.createElement('tr');
	// var col = document.createElement('td');
	// col.innerHTML = info['filename'];
	// ret.appendChild(col);
	// return ret;
}

function update_playlist(playlist,songs,song_info) {
	window.latestplaylistsongs = songs;
	playlist.innerHTML = '';
	if(songs!=undefined && song_info!=undefined) {
		for (i = 0; i < songs.length; i++) {
			var song = songs[i];
			var item = make_playlist_item(song_info[song]);
			playlist.appendChild(item);
		}
	}
}

function update_data(playlist, cur_song, first_callback) {
	WebRequest("GET","/songs/","",function(text) {
		try {
			var song_data = JSON.parse(text);
			if(song_data['song_info']!=undefined) {
				if (song_data['song_info'][song_data['current_song']]!=undefined) {
					update_cur_song(cur_song,song_data['song_info'][song_data['current_song']],song_data['pos']);
				} else {
					update_cur_song(cur_song,guess_info(song_data['current_song']),song_data['pos']);
				}
				update_playlist(playlist,song_data['song_list'],song_data['song_info']);
			}
		}
		catch(err) {
			console.log('Error processing song data: '+err.message);
		}
		window.setTimeout(function() {
			update_data(playlist,cur_song,null);
		},1000);
		if (first_callback!=null) {
			first_callback();
		}
	},function(error) {
		console.log("ERROR getting song data: "+error);
		window.setTimeout(function() {
			update_data(playlist,cur_song,null);
		},100);
		if (first_callback!=null) {
			first_callback();
		}
	});
}

function make_all_songs_item(song) {
	// var ret = document.createElement('tr');
	// var div = document.createElement('div');
	// var anch = makelink(div,function() {
		// add_to_playlist(song);
	// });
	// var songtext = document.createTextNode(song);
	// div.appendChild(songtext);
	// get_song_info(song,function(song_info) {
		// div.innerHTML = '';
		// var col = document.createElement('td');
		// var fname = document.createTextNode(song_info['filename']);
		// col.appendChild(fname);
		// div.appendChild(col);
	// });
	// ret.appendChild(div);
	// return ret;
	
	// var div = document.createElement('div');
	var div = make_song_info_item({'filename':song},null);
	var anch = makelink(div,"list-group-item",function() {
		add_to_playlist(song);
	});
	// var songtext = document.createTextNode(song);
	// div.appendChild(songtext);
	get_song_info(song,function(song_info) {
		update_song_info_item(div,song_info,null);
		// div.innerHTML = '';
		// var fname = document.createTextNode(song_info['filename']);
		// div.appendChild(fname);
	});
	return anch;
}

function update_all_songs(target,all_songs) {
	var i;
	for (i = 0; i < all_songs.length; i++) {
	// for (i = 0; i < 20; i++) {
		var song = all_songs[i];
		var item = make_all_songs_item(song);
		target.appendChild(item);
	}
}

window.all_songs_updated = false;
function update_all_songs_req(target) {
	if(!window.all_songs_updated) {
		WebRequest("GET","/avail_songs/","",function(text) {
			try {
				var all_songs = JSON.parse(text);
				target.innerHTML = '';
				window.all_songs_updated = true;
				update_all_songs(target,all_songs);
			}
			catch(err) {
				console.log('Error processing song data: '+err.message);
			}
			window.setTimeout(function(){ update_all_songs_req(target); }, 100);
		},function(error) {
			console.log("ERROR getting song data: "+error);
			window.setTimeout(function(){ update_all_songs_req(target); }, 100);
		});
		// window.setTimeout(function(){ update_all_songs_req(target); }, 2000);
	}
}

function init() {
	var playlist = document.getElementById("playlist");
	var cur_song = document.getElementById("current_song");
	var all_songs = document.getElementById("all_songs");
	song_info_queue_handler();
	update_data(playlist,cur_song,function() {
		get_all_song_info(function() {
			update_all_songs_req(all_songs);
		});
	});
}

init();
