// noinspection JSUnresolvedVariable,JSUnresolvedFunction

const BACK_BUFFER_SIZE = 80; // just keep prev 30 frames
const FORWARD_BUFFER_SIZE = 120; // try to load next 60 frames

const TIME_PER_FRAME = 1000;

let stopwatch;

let cfn = 0;

const loaded_frames = new Map();
const loading_frames = new Set();

const game_id = parseInt(document.getElementById('game_id').content, 10);

let gotGameInfo = false;
let waitingForGameInfo = false;
let game_length = 0;
let map_w, map_h;
let game_params;

let trueCanvas;

function setup(){
	let s = min(windowWidth, (4.0/3)*windowHeight)*0.98;
	let cnv = createCanvas(s, 0.75*s);
	cnv.parent("game_canvas");
	trueCanvas = createGraphics(s*displayDensity(), 0.75*s*displayDensity());
	stopwatch = new StopWatch();
	//stopwatch.rate = 1;
}


function draw(){
	trueCanvas.reset();
	draw_real(trueCanvas);
	image(trueCanvas, 0, 0, width, height);
}

function draw_real(pg){
	pg.background(0);

	if(!socket.connected){
		if(!connection_error){
			center_text(pg, "Connecting...");
		}else{
			center_text(pg, "Error connecting. You may need to reload.");
		}
		return;
	}

	if(!gotGameInfo){
		if(!waitingForGameInfo){
			fetch_game_info();
			waitingForGameInfo = true;
		}
		center_text(pg, "Loading...");
		return;
	}

	handleFrameBuffer();

	stopwatch.update();

	// do we need to go to next frame?
	while((stopwatch.time - (cfn+1)*TIME_PER_FRAME) > 0){
		// we do
		cfn++;
		// do as many times as needed
	}
	// do we need to go to prev frame?
	while(cfn*TIME_PER_FRAME - stopwatch.time > 0){
		// we do
		cfn--;
		// do as many times as needed
	}
	if(cfn < 0){ // went too far
		cfn = 0;
		stopwatch.time = 0;
		stopwatch.pause();
		stopwatch.update();
	}
	// are we done?
	if(cfn >= game_length){
		cfn = game_length;
		stopwatch.time = cfn*TIME_PER_FRAME;
		stopwatch.pause();
		// force an update
		stopwatch.update();
	}
	// how far have we gone in this frame?
	let dt = stopwatch.time/TIME_PER_FRAME - cfn;

	if(!loaded_frames.has(cfn)){ // even if we went to next frame, this should still mostly never be the case
		center_text(pg, "Loading...");
	}else{
		render_game(pg, dt);
	}
	render_controls(pg, mouseX*displayDensity(), mouseY*displayDensity(), dt);
}

function mouseClicked(){
	if(gotGameInfo){
		return click_controls(trueCanvas, mouseX*displayDensity(), mouseY*displayDensity());
	}
	return true;
}

function mousePressed(){
	if(gotGameInfo){
		return press_controls(trueCanvas, mouseX*displayDensity(), mouseY*displayDensity());
	}
	return true;
}

function mouseDragged(){
	if(gotGameInfo){
		return drag_controls(trueCanvas, mouseX*displayDensity(), mouseY*displayDensity());
	}
	return true;
}

function mouseReleased(){
	if(gotGameInfo){
		return release_controls(trueCanvas, mouseX*displayDensity(), mouseY*displayDensity());
	}
	return true;
}

function touchStarted(){
	if(gotGameInfo){
		return press_controls(trueCanvas, mouseX*displayDensity(), mouseY*displayDensity());
	}
	return true;
}

function touchMoved(){
	if(gotGameInfo){
		return drag_controls(trueCanvas, mouseX*displayDensity(), mouseY*displayDensity());
	}
	return true;
}

function touchEnded(){
	if(gotGameInfo){
		if(!release_controls(trueCanvas, mouseX*displayDensity(), mouseY*displayDensity())){
			return false;
		}else{
			return click_controls(trueCanvas, mouseX*displayDensity(), mouseY*displayDensity());
		}
	}
	return true;
}

function keyPressed(){
	if(gotGameInfo){
		return key_controls();
	}
	return true;
}

function center_text(pg, txt){
	pg.push();
	pg.fill(255);
	let s = pg.height*0.05;
	pg.textSize(s);
	pg.text(txt, pg.width/2 - pg.textWidth(txt)/2, pg.height/2 - s/2);
	pg.pop();
}


function handleFrameBuffer(){
	// delete unnecessary loaded frames
	// noinspection JSUnusedLocalSymbols
	for(const [frame_num, frame] of loaded_frames){
		if(frame_num < cfn - BACK_BUFFER_SIZE || frame_num > cfn + FORWARD_BUFFER_SIZE){
			loaded_frames.delete(frame_num);
		}
	}
	// make sure current frame exists
	if(fetch_frame_if_needed(cfn)){
		return; // ONLY fetch one frame per call
	}
	// forward buffer
	for(let i = cfn+1; i <= min(cfn+FORWARD_BUFFER_SIZE, game_length); i++){
		if(fetch_frame_if_needed(i)){
			return; // ONLY fetch one frame per call
		}
	}
	//back buffer
	for(let i = max(0, cfn-BACK_BUFFER_SIZE); i < cfn; i++){
		if(fetch_frame_if_needed(i)){
			return; // ONLY fetch one frame per call
		}
	}
}


function fetch_frame_if_needed(frame_num){
	if(!loaded_frames.has(frame_num) && !loading_frames.has(frame_num)){
		fetch_frame(frame_num);
		loading_frames.add(frame_num);
		return true; // frame was fetched
	}
	return false;
}


function frameReceived(data){
	if(data['game_id'] !== game_id)return; // ignore the frame
	let frame_num = data['frame_num'];
	if(!loading_frames.has(frame_num))return; // again ignore
	// got a frame we needed
	loading_frames.delete(frame_num);
	loaded_frames.set(frame_num, data['frame']);
}


function gameInfoReceived(data){
	if(data['game_id'] !== game_id)return; // ignore
	game_length = data['game_length'];
	map_w = data['map_w'];
	map_h = data['map_h'];
	game_params = data['game_params'];
	game_init(trueCanvas);
	gotGameInfo = true;
	waitingForGameInfo = false;
}


function windowResized(){
	let s = min(windowWidth, (4.0/3)*windowHeight)*0.98;
	resizeCanvas(s, 0.75*s);
	trueCanvas.remove();
	trueCanvas = createGraphics(s*displayDensity(), 0.75*s*displayDensity());
	if(gotGameInfo)game_init(trueCanvas);
}
