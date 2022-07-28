// noinspection JSUnresolvedFunction,JSUnresolvedVariable

const rates = [0.3, 0.5, 0.7, 1, 1.5, 2, 3, 5, 10];
let cri = 3;

const fadeTime = 600;
let fade = false, fadeStart = 0;

let h = 0, lock = false, release = false;

function render_controls(pg, mX, mY, dt){
    let cH = pg.height/10;
    let cY = pg.height - cH;
    pg.push();
    drawFade(pg, cH, cY);
    drawControls(pg, cH, cY);
    drawSlider(pg, cH, cY, mX, mY, dt);
    pg.pop();
}

function drawFade(pg, cH, cY){
    if(fade){
        let t = performance.now();
        if(t - fadeStart >= fadeTime){
            fade = false;
        }else{
            pg.noStroke();
            pg.fill(255, 50, 255, (1 -(t-fadeStart)/fadeTime)*150);
            let x = pg.width/2, y = 2*pg.height/3 - cH;
            pg.ellipse(x, y, cH*1.5, cH*1.5);
            pg.fill(200, 255, 200, (1.5 -(t-fadeStart)/fadeTime)*150)
            switch(fade){
                case 'start':
                    pg.triangle(x - 0.19*cH, y - cH/3, x - 0.19*cH, y + cH/3, x + 0.38*cH, y);
                    break;
                case 'pause':
                    pg.rect(x - cH*0.25, y - cH/3, cH*0.2, 2*cH/3);
                    pg.rect(x + cH*0.05, y - cH/3, cH*0.2, 2*cH/3);
                    break;
                case 'forward':
                    pg.triangle(x - 0.3*cH, y - cH/4, x - 0.3*cH, y + cH/4, x + 0.13*cH, y);
                    pg.rect(x + 0.13*cH, y - cH/4, cH/7, cH/2);
                    break;
                case 'backward':
                    pg.triangle(x + 0.3*cH, y - cH/4, x + 0.3*cH, y + cH/4, x - 0.13*cH, y);
                    pg.rect(x - 0.13*cH - cH/7, y - cH/4, cH/7, cH/2);
                    break;
                case 'faster':
                    pg.triangle(x - 0.38*cH, y - cH/4, x - 0.38*cH, y + cH/4, x + 0.05*cH, y);
                    pg.triangle(x + 0.05*cH, y - cH/4, x + 0.05*cH, y + cH/4, x + 0.48*cH, y);
                    break;
                case 'slower':
                    pg.triangle(x + 0.38*cH, y - cH/4, x + 0.38*cH, y + cH/4, x - 0.05*cH, y);
                    pg.triangle(x - 0.05*cH, y - cH/4, x - 0.05*cH, y + cH/4, x - 0.48*cH, y);
                    break;
            }
        }
    }
}

function drawControls(pg, cH, cY){
    pg.fill(255);
    pg.noStroke();
    if(stopwatch.isPaused && cfn===game_length){
        pg.stroke(255);
        pg.noFill();
        pg.strokeWeight(max(3, cH/10));
        pg.arc(cH*0.5, cY + cH*0.5, cH*0.6, cH*0.6, -0.5*PI, 1.1*PI);
        pg.fill(255);
        pg.noStroke();
        pg.triangle(cH*0.35, cY + 0.2*cH, cH*0.52, cY + 0.05*cH, cH*0.52, cY + 0.35*cH);
    }else if(stopwatch.isPaused){
        pg.triangle(0.33*cH, cY + 0.2*cH, 0.33*cH, cY + 0.8*cH, 0.85*cH, cY + 0.5*cH);
    }else{
        pg.rect(0.24*cH, cY + 0.2*cH, 0.2*cH, 0.6*cH);
        pg.rect(0.56*cH, cY + 0.2*cH, 0.2*cH, 0.6*cH);
    }
    pg.fill((cri === 0)?180:255);
    pg.triangle(pg.width - 2.5*cH, cY + 0.3*cH, pg.width - 2.5*cH, cY + 0.7*cH, pg.width - 2.85*cH, cY + 0.5*cH);
    pg.triangle(pg.width - 2.2*cH, cY + 0.3*cH, pg.width - 2.2*cH, cY + 0.7*cH, pg.width - 2.55*cH, cY + 0.5*cH);
    pg.fill((cri === rates.length-1)?180:255);
    pg.triangle(pg.width - 0.5*cH, cY + 0.3*cH, pg.width - 0.5*cH, cY + 0.7*cH, pg.width - 0.15*cH, cY + 0.5*cH);
    pg.triangle(pg.width - 0.8*cH, cY + 0.3*cH, pg.width - 0.8*cH, cY + 0.7*cH, pg.width - 0.45*cH, cY + 0.5*cH);
    pg.fill(255);
    pg.textSize(cH*0.4);
    let txt = rates[cri] + "×";
    pg.text(txt, pg.width - cH*1.5 - pg.textWidth(txt)/2, cY + cH*0.65)
}

function drawSlider(pg, cH, cY, mX, mY, dt){
    if(release){
        lock = false;
        release = false;
    }

    pg.stroke(72);
    if(h === 0) h = cH/20;
    h = (lock || overSlider(pg, cH, cY, mX, mY, h))?cH/8:cH/20;
    pg.strokeWeight(h);
    pg.line(cH*1.5, cY + cH*0.5, pg.width - cH*3.5, cY + cH*0.5);
    pg.stroke(160);
    let l = pg.width - cH*5;
    let p = l/game_length;
    let s = -1, c = 0;
    while(c < game_length){
        if(loaded_frames.has(c)){
            if(s === -1){
                s = c;
            }
        }else{
            if(s !== -1){
                pg.line(cH*1.5 + s*p, cY + cH*0.5, cH*1.5 + c*p - h/2, cY + cH*0.5);
                s = -1;
            }
        }
        c++;
    }
    if(s !== -1){
        pg.line(cH*1.5 + s*p, cY + cH*0.5, pg.width - cH*3.5, cY + cH*0.5);
    }
    pg.stroke(200, 255, 100);
    pg.line(cH*1.5, cY + cH*0.5, cH*1.5 + cfn*p + dt*p, cY + cH*0.5);

    pg.noStroke();
    pg.fill(100, 255, 200);

    if(lock || overSlider(pg, cH, cY, mX, mY, h))pg.ellipse(cH*1.5 + cfn*p + dt*p, cY + cH*0.5, h*2, h*2);
    if(lock){
        pg.stroke(60, 240, 160)
        pg.noFill();
        pg.strokeWeight(2);
        pg.ellipse(cH*1.5 + cfn*p + dt*p, cY + cH*0.5, h*3, h*3);
    }
}

function overSlider(pg, cH, cY, mX, mY, h){
    return (mX >= cH*1.5 - h) && (mX <= pg.width - cH*3.5 + h) && (mY >= cY + cH*0.5 - h*3) && (mY <= cY + cH*0.5 + h*3);
}

function press_controls(pg, mX, mY){
    let cH = pg.height/10;
    let cY = pg.height - cH;
    if(overSlider(pg, cH, cY, mX, mY, h)){
        lock = true;
        frameSeek(pg, cH, cY, mX, mY);
    }
    return !lock;
}

function drag_controls(pg, mX, mY){
    let cH = pg.height/10;
    let cY = pg.height - cH;
    if(lock || overSlider(pg, cH, cY, mX, mY, h)){
        lock = true;
        frameSeek(pg, cH, cY, mX, mY);
    }
    return !lock;
}

function release_controls(){
    if(lock){
        release = true;
    }
    return !lock;
}

function frameSeek(pg, cH, cY, mX, mY){
    let t = min(max(0, (mX - (cH*1.5))/(pg.width - cH*5)), 1);
    let nt = t*game_length*TIME_PER_FRAME;
    stopwatch.time = nt;
}

function click_controls(pg, mX, mY){
    if(!lock){
        let cH = pg.height/10;
        let cY = pg.height - cH;
        if(mX >= 0.1*cH && mX <= 0.9*cH && mY >= cY + 0.1*cH && mY <= cY + 0.9*cH){
            if(stopwatch.isPaused){
                if(cfn === game_length){
                    stopwatch.reset();
                    cfn = 0;
                    cri = 3;
                }
                stopwatch.start();
            }else{
                stopwatch.pause();
            }
            return false;
        }
        if(mY >= cY + 0.2*cH && mY <= cY + 0.8*cH){
            if(mX >= pg.width - 2.9*cH && mX <= pg.width - 2.1*cH){
                if(cri > 0){
                    cri--;
                    stopwatch.rate = rates[cri];
                    return false;
                }
            }else if(mX >= pg.width - 0.9*cH && mX <= pg.width - 0.1*cH){
                if(cri < rates.length - 1){
                    cri++;
                    stopwatch.rate = rates[cri];
                    return false;
                }
            }
        }
        if(mX > 0 && mX < pg.width && mY > pg.height/3 - cH && mY < pg.height - cH){
            if(stopwatch.isPaused){
                stopwatch.start();
                fade = 'start';
            }else{
                stopwatch.pause();
                fade = 'pause';
            }
            fadeStart = performance.now();
            return false;
        }
    }
    return !lock;
}

function key_controls(){
    if(key === 'j' || key === 'J'){
        stopwatch.time -= 10000;
        fade = 'backward';
    }else if(key === 'k' || key === 'K'){
        if(stopwatch.isPaused){
            stopwatch.start();
            fade = 'start';
        }else{
            stopwatch.pause();
            fade = 'pause';
        }
    }else if(key === 'l' || key === 'L'){
        stopwatch.time += 10000;
        fade = 'forward';
    }else if(key === '>' || key === '.' || keyCode === UP_ARROW){
        if(cri < rates.length - 1){
            cri++;
            stopwatch.rate = rates[cri];
            fade = 'faster';
        }
    }else if(key === '<' || key === ',' || keyCode === DOWN_ARROW){
        if(cri > 0){
            cri--;
            stopwatch.rate = rates[cri];
            fade = 'slower';
        }
    }else if(key === 'r' || key === 'R'){
        stopwatch.reset();
        cfn = 0;
        cri = 3;
        stopwatch.start();
    }else if(keyCode === RIGHT_ARROW){
        stopwatch.time += 5000;
        fade = 'forward';
    }else if(keyCode === LEFT_ARROW){
        stopwatch.time -= 5000;
        fade = 'backward';
    }else{
        return true;
    }
    fadeStart = performance.now();
    return false;
}
