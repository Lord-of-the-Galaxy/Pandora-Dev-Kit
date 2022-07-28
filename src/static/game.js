// ARRANGEMENT
// top 1/3 - 1/10 of screen is info
// next 2/3 is game
// final 1/10 is controls
// noinspection JSUnusedLocalSymbols,JSUnresolvedVariable,JSUnresolvedFunction

let size;
let boardX, boardY, boardW, boardH;

let infoH;

let red1, red2, blue1, blue2, ore1, ore2, fuel1, fuel2, white;

let pointsBar1, pointsBar2, basesBar1, basesBar2, turretsBar1, turretsBar2, minersBar1, minersBar2, fightersBar1,
    fightersBar2, oreBar1, oreBar2, fuelBar1, fuelBar2;
let allBars;

Object.entries = typeof Object.entries === 'function' ? Object.entries : obj => Object.keys(obj).map(k => [k, obj[k]]);

function game_init(pg){
    // initialize all rendering variables
    // calculate size of cells
    if(map_w < map_h*2){
        size = (2.0/3)*pg.height/map_h;
    }else{
        size = pg.width/map_w;
    }
    boardW = size*map_w;
    boardH = size*map_h;
    boardX = (pg.width - boardW)/2.0;
    boardY = pg.height/3.0 + ((2.0/3)*pg.height - boardH)/2 - pg.height/10.0;

    infoH = pg.height/3 - pg.height/10 - 2;

    white = color(255);

    red1 = color(255, 50, 20);
    red2 = color(160, 30, 10);

    blue1 = color(20, 140, 255);
    blue2 = color(0, 90, 180);

    ore1 = color(50, 200, 30);
    ore2 = color(15, 105, 85);

    fuel1 = color(255, 200, 0);
    fuel2 = color(200, 140, 30);

    pointsBar1 = new AutoProgressBar(infoH*0.29, infoH*0.04, pg.width*0.3 - infoH*0.32, infoH*0.17, blue1, blue2, false, 300, 500);
    pointsBar2 = new AutoProgressBar(pg.width*0.7 + infoH*0.03, infoH*0.04, pg.width*0.3 - infoH*0.32, infoH*0.17, red1, red2, true, 300, 500);

    basesBar1 = new AutoProgressBar(infoH*0.29, infoH*0.29, pg.width*0.25 - infoH*0.32, infoH*0.17, blue1, blue2, false, 1, 2);
    basesBar2 = new AutoProgressBar(pg.width*0.75 + infoH*0.03, infoH*0.29, pg.width*0.25 - infoH*0.32, infoH*0.17, red1, red2, true, 1, 2);

    turretsBar1 = new AutoProgressBar(pg.width*0.25 + infoH*0.29, infoH*0.29, pg.width*0.25 - infoH*0.34, infoH*0.17, blue1, blue2, false, 0, 2);
    turretsBar2 = new AutoProgressBar(pg.width*0.50 + infoH*0.05, infoH*0.29, pg.width*0.25 - infoH*0.34, infoH*0.17, red1, red2, true, 0, 2);

    minersBar1 = new AutoProgressBar(infoH*0.29, infoH*0.54, pg.width*0.25 - infoH*0.32, infoH*0.17, blue1, blue2, false, 10, 15);
    minersBar2 = new AutoProgressBar(pg.width*0.75 + infoH*0.03, infoH*0.54, pg.width*0.25 - infoH*0.32, infoH*0.17, red1, red2, true, 10, 15);

    fightersBar1 = new AutoProgressBar(pg.width*0.25 + infoH*0.29, infoH*0.54, pg.width*0.25 - infoH*0.34, infoH*0.17, blue1, blue2, false, 3, 5);
    fightersBar2 = new AutoProgressBar(pg.width*0.50 + infoH*0.05, infoH*0.54, pg.width*0.25 - infoH*0.34, infoH*0.17, red1, red2, true, 3, 5);

    oreBar1 = new AutoProgressBar(infoH*0.29, infoH*0.79, pg.width*0.25 - infoH*0.32, infoH*0.17, ore1, ore2, false, 0, 2);
    oreBar2 = new AutoProgressBar(pg.width*0.75 + infoH*0.03, infoH*0.79, pg.width*0.25 - infoH*0.32, infoH*0.17, ore1, ore2, true, 0, 2);

    fuelBar1 = new AutoProgressBar(pg.width*0.25 + infoH*0.29, infoH*0.79, pg.width*0.25 - infoH*0.34, infoH*0.17, fuel1, fuel2, false, 0, 2);
    fuelBar2 = new AutoProgressBar(pg.width*0.50 + infoH*0.05, infoH*0.79, pg.width*0.25 - infoH*0.34, infoH*0.17, fuel1, fuel2, true, 0, 2);

    allBars = [pointsBar1, pointsBar2, basesBar1, basesBar2, turretsBar1, turretsBar2, minersBar1, minersBar2, fightersBar1, fightersBar2, oreBar1, oreBar2, fuelBar1, fuelBar2]
}

function render_game(pg, dt){
    render_info(pg, dt);
    render_map(pg, dt);
}

function render_info(pg, dt){
    pg.push();

    let frame = loaded_frames.get(cfn);
    let info = frame.info;

    let s = infoH/4;

    pg.strokeWeight(2);
    pg.stroke(255);

    laser(pg, 0, s, pg.width*0.4, s, 1, 3);
    laser(pg, pg.width*0.6, s, pg.width, s, 2, 3);
    laser(pg, pg.width*0.25, s, pg.width*0.25, infoH, 1, 3);
    laser(pg, pg.width*0.75, s, pg.width*0.75, infoH, 2, 3);

    laser(pg, pg.width/2, s-1, pg.width/2, infoH, 0, 5);
    laser(pg, pg.width*0.4, s-1, pg.width*0.6, s-1, 0, 5);
    laser(pg, pg.width*0.4, 0, pg.width*0.4, s-1, 0 , 5);
    laser(pg, pg.width*0.6, 0, pg.width*0.6, s-1, 0, 5);
    laser(pg, 0, infoH, pg.width, infoH, 0, 3);

    pg.textSize(s*0.75);
    pg.fill(180, 255, 180);
    let txt = "Move " + (cfn+1);
    if(cfn === game_length)txt = "Ended!";
    pg.text(txt, (pg.width-pg.textWidth(txt))/2, s*0.7);

    // to show a bunch of lines demarcating regions
    /*
    line(0, s, width, s);
    line(0, 2*s, width, 2*s);
    line(0, 3*s, width, 3*s);
    line(width*0.25, s, width*0.25, infoH);
    line(width*0.75, s, width*0.75, infoH);
    line(width*0.3, 0, width*0.3, s);
    line(width*0.7, 0, width*0.7, s);

    line(s, 0, s, infoH);
    line(width*0.25 + s, s, width*0.25 + s, infoH);
    line(width*0.75 - s, s, width*0.75 - s, infoH);
    line(width - s, 0, width - s, infoH);*/

    special_star(pg, s*0.5, s*0.5, s*0.4, false, 6);
    special_star(pg, pg.width - s*0.5, s*0.5, s*0.4, true, 6);

    pg.textSize(s*0.75);
    pg.fill(blue1);
    txt = "" + info[0].points
    pg.text(txt, pg.width*0.385-pg.textWidth(txt), s*0.8);
    pg.fill(red1);
    txt = "" + info[1].points
    pg.text(txt, pg.width*0.615, s*0.8);

    drawBase(pg, s*0.2, s*1.2, false, s*0.6);
    drawTurret(pg, pg.width*0.25 + s*0.1, s*1.1, false, s*0.8);
    drawMiner(pg, s*0.05, s*2.05, QUARTER_PI, "FOF", false, s*0.9);
    drawFighter(pg, pg.width*0.25 + s*0.05, s*2.05, QUARTER_PI, false, s*0.9);
    drawOre(pg, s*0.05, s*3.05, Math.round(game_params.ore_deposits.max_amt*0.5), s*0.9);
    drawFuel(pg, pg.width*0.25 + s*0.05, s*3.05, Math.round(game_params.fuel_deposits.max_amt*0.35), s*0.9);

    drawBase(pg, pg.width - s*0.8, s*1.2, true, s*0.6);
    drawTurret(pg, pg.width*0.75 - s*0.9, s*1.1, true, s*0.8);
    drawMiner(pg, pg.width - s*0.95, s*2.05, QUARTER_PI, "OFO", true, s*0.9);
    drawFighter(pg, pg.width*0.75 - s*0.95, s*2.05, QUARTER_PI, true, s*0.9);
    drawOre(pg, pg.width - s*0.95, s*3.05, Math.round(game_params.ore_deposits.max_amt*0.5), s*0.9);
    drawFuel(pg, pg.width*0.75 - s*0.95, s*3.05, Math.round(game_params.fuel_deposits.max_amt*0.35), s*0.9);


    progressBarLinkedUpdate([pointsBar1, pointsBar2], [info[0].points, info[1].points]);
    progressBarLinkedUpdate([basesBar1, basesBar2], [info[0].bases, info[1].bases]);
    progressBarLinkedUpdate([turretsBar1, turretsBar2], [info[0].turrets, info[1].turrets]);
    progressBarLinkedUpdate([minersBar1, minersBar2], [info[0].miners, info[1].miners]);
    progressBarLinkedUpdate([fightersBar1, fightersBar2], [info[0].fighters, info[1].fighters]);
    progressBarLinkedUpdate([oreBar1, oreBar2], [info[0].ore, info[1].ore]);
    progressBarLinkedUpdate([fuelBar1, fuelBar2], [info[0].fuel, info[1].fuel]);

    for(const bar of allBars){
        bar.draw(pg);
    }

    pg.pop();
}

function render_map(pg, dt){
    pg.push();
    pg.noStroke();

    pg.fill(50, 40, 20)
    pg.rect(0, pg.height/3 - pg.height/10, pg.width, (2.0/3)*pg.height);
    pg.fill(0);
    pg.rect(boardX, boardY, boardW, boardH);

    // all of this can be cached actually -_-
    // OPTIMIZE:
    let frame = loaded_frames.get(cfn);
    let map = frame.map;
    let moves = new Map(Object.entries(frame.moves));
    let collisions = frame.collisions;
    let destroyed = frame.destroyed;
    let attacks = frame.attacks;

    let bases = new Map();
    let turrets = new Map();
    let buildings = new Map(); // buildings under construction
    let vehicles = new Map();
    for(let i = 0; i < map_w; i++){
        for(let j = 0; j < map_h; j++){
            let tile = map[i][j];
            let x = boardX + i*size;
            let y = boardY + j*size;
            switch(tile.t){
                case 'O': // ore and fuel can be drawn anyway as nothing will ever be on top of ore/fuel
                drawOre(pg, x, y, tile.a);
                break;
                case 'F': // ore and fuel can be drawn anyway as nothing will ever be on top of ore/fuel
                drawFuel(pg, x, y, tile.a);
                break;
                case 'B': // store for drawing later
                bases.set(tile.i, [i, j]);
                let bv1 = new Map(Object.entries(tile.v));
                for(const [id,v] of bv1){
                    vehicles.set(id, [i,j]);
                }
                break;
                case 'T':
                turrets.set(tile.i, [i,j]);
				let bv2 = new Map(Object.entries(tile.v));
                for(const [id,v] of bv2){
                    vehicles.set(id, [i,j]);
                }
                break;
                case 'C':
                buildings.set(tile.i, [i,j]);
				let bv3 = new Map(Object.entries(tile.v));
                for(const [id,v] of bv3){
                    vehicles.set(id, [i,j]);
                }
                break;
                case 'K':
                case 'M':
                vehicles.set(tile.i, [i,j]);
                break;
            }
        }
    }
    let dir_to_r = {
        'U': 0,
        'D': PI,
        'L': 3*HALF_PI,
        'R': HALF_PI
    }
    let dir_to_d = {
        'U': [0, -1],
        'D': [0, 1],
        'L': [-1, 0],
        'R': [1, 0]
    }
    for(const [id, loc] of buildings){
        let x = loc[0];
        let y = loc[1];
        drawBuilding(pg, boardX + s*size, boardY + y*size, map[x][y].m, map[x][y]);
    }
    if(dt >= 0.7){
        for(const a of attacks){
            let x1 = boardX + size/2 + size*a[0][0], y1 = boardY + size/2 + size*a[0][1];
            let x2 = boardX + size/2 + size*a[1][0], y2 = boardY + size/2 + size*a[1][1];
            let p = a[2];
            laser(pg, x1, y1, x2, y2, p)
        }
    }
    for(const [id, loc] of vehicles){
        let x = loc[0];
        let y = loc[1];
        let d = 'U';
        if(map[x][y].t === 'M' || map[x][y].t === 'K'){
            d = map[x][y].d;
        }else{
            d = map[x][y].v[id].d;
        }
        let r = dir_to_r[d];
        let px = x;
        let py = y;
        // first check if it should be moving
        if(moves.has(id) && moves.get(id).charAt(0)!=='N'){ // if so, then calculate movement
            let r2 = dir_to_r[moves.get(id).charAt(0)];
            let dl = dir_to_d[moves.get(id).charAt(0)];
            r = lerp_r(r, r2, dt/0.3);
            px += min(1, max(0, (dt-0.3)/0.4))*dl[0];
            py += min(1, max(0, (dt-0.3)/0.4))*dl[1];
        }
        let v = (map[x][y].t === 'M' || map[x][y].t === 'K')? map[x][y] : map[x][y].v[id]
        if(v.t === 'M'){
            drawMiner(pg, boardX + px*size, boardY + py*size, r, v.c, v.p===2);
        }else if(v.t === 'K'){
            drawFighter(pg, boardX + px*size, boardY + py*size, r, v.p===2);
        }
    }
    for(const [id, loc] of bases){
        let x = loc[0];
        let y = loc[1];
        drawBase(pg, boardX + x*size, boardY + y*size, map[x][y].p===2);
    }
    for(const [id, loc] of turrets){
        let x = loc[0];
        let y = loc[1];
        drawTurret(pg, boardX + x*size, boardY + y*size, map[x][y].p===2);
    }
    if(dt >= 0.5){
        pg.noFill();
        pg.stroke(255, 150, 0);
        pg.strokeWeight(3);
        for(const loc of collisions){
            pg.ellipse(boardX + (loc[0]+0.5)*size, boardY + (loc[1]+0.5)*size, size, size);
        }
    }
    if(dt >= 0.85){
        pg.noFill();
        pg.stroke(255, 0, 70);
        pg.strokeWeight(3);
        for(const loc of destroyed){
            pg.ellipse(boardX + (loc[0]+0.5)*size, boardY + (loc[1]+0.5)*size, size, size);
        }
    }
    pg.pop();
}


function drawMiner(pg, x, y, r, c, p, s = size){
    pg.push();
    pg.translate(x+s/2, y+s/2);
    pg.rotate(r);
    pg.noStroke();
    pg.fill(p?red1:blue1);
    pg.beginShape();
    pg.vertex(0, s*-0.42);
    pg.vertex(s*0.25, s*-0.22);
    pg.vertex(s*0.25, s*0.4);
    pg.vertex(0, s*0.2);
    pg.vertex(s*-0.25, s*0.4);
    pg.vertex(s*-0.25, s*-0.22);
    pg.endShape(CLOSE);
    pg.fill(p?red2:blue2);
	pg.rect(-s*0.14, -s*0.23, s*0.28, s*0.36);
  	for(let i = 0; i < c.length; i++){
      if(c.charAt(i) === 'O'){
        pg.fill(ore1);
      }else if(c.charAt(i) === 'F'){
        pg.fill(fuel1);
      }else{
        continue;
      }
      pg.rect(s*-0.14, s*(-0.22+0.09*(3-i)), s*0.28, s*0.09);
    }
    pg.pop();
}

function drawFighter(pg, x, y, r, p, s = size){
    pg.push();
    pg.translate(x+s/2, y+s/2);
    pg.rotate(r);
    pg.noStroke();
    pg.fill(p?red1:blue1);
    pg.beginShape();
  	pg.vertex(0, s*-0.42);
  	pg.vertex(s*0.09, s*-0.12);
	pg.vertex(s*0.27, s*0.16);
  	pg.vertex(s*0.12, s*0.16);
  	pg.vertex(s*0.20, s*0.28);
  	pg.vertex(0, s*0.23);
  	pg.vertex(s*-0.20, s*0.28);
  	pg.vertex(s*-0.12, s*0.16);
  	pg.vertex(s*-0.27, s*0.16);
  	pg.vertex(s*-0.09, s*-0.12);
  	pg.endShape(CLOSE);
  	pg.pop();
}

function drawBuilding(pg, x, y, m, b, p, s = size){
    let t = (b==='B')?'BASE':'TURRET';
    let a = m*s;
    pg.push();
    pg.noStroke();
    pg.fill(p?red2:blue2);
    pg.rect(x, y, s, s);
    pg.fill(p?red1:blue1);
    pg.rect(x + (s-a)/2, y + (s-a)/2, a, a);
    pg.pop();
}

function drawBase(pg, x, y, p, s = size){
    pg.push();
    pg.noStroke();
    pg.fill(p?red2:blue2);
    const r = 3, r2 = 6 ;
    pg.rect(x-s/r2, y-s/r2, s/r, s/r);
    pg.rect(x+s-s/r2, y-s/r2, s/r, s/r);
    pg.rect(x-s/r2, y+s-s/r2, s/r, s/r);
    pg.rect(x+s-s/r2, y+s-s/r2, s/r, s/r);
    pg.fill(p?red1:blue1);
    pg.rect(x, y, s, s);
    pg.pop();
}

function drawTurret(pg, x, y, p, s = size){
    pg.push();
    pg.stroke(p?red2:blue2);
    pg.strokeWeight(s/6);
    pg.line(x + s/6, y + s/6, x + s - s/6, y + s - s/6);
    pg.line(x + s - s/6, y + s/6, x + s/6, y + s - s/6);
    pg.strokeWeight(1);
    pg.fill(p?red1:blue1);
    pg.ellipse(x+s/2, y+s/2, s*0.65, s*0.65);
    pg.pop();
}

function drawOre(pg, x, y, amt, s = size){
    let max = game_params.ore_deposits.max_amt;
    let a = amt*s/max;
    let b = min(s, a+(s-a)/2);

    pg.push();
    pg.noStroke();
    pg.fill(ore2);
    pg.rect(x + (s-b)/2, y + (s-b)/2, b, b);
    pg.fill(ore1);
    pg.rect(x + (s-a)/2, y + (s-a)/2, a, a);
    pg.pop();
}

function drawFuel(pg, x, y, amt, s = size){
    let max = game_params.fuel_deposits.max_amt;
    let a = amt*s/max;
    let b = min(s, a+(s-a)/2);

    pg.push();
    pg.noStroke();
    pg.fill(fuel2);
    pg.rect(x + (s-b)/2, y + (s-b)/2, b, b);
    pg.fill(fuel1);
    pg.rect(x + (s-a)/2, y + (s-a)/2, a, a);
    pg.pop();
}

function laser(pg, x1, y1, x2, y2, p = 0, n = Math.round(size/6)){
    pg.push();
    for(let i = 0; i < n; i++){
        if(p===2){
            pg.stroke(255, i*255/(n-1), i*255/(n-1), 255-i*150/(n-1));
        }else if(p===1){
            pg.stroke(i*255/(n-1), i*255/(n-1), 255, 255-i*150/(n-1));
        }else{
            pg.stroke(225, i*255/(n-1), 255, 255-i*150/(n-1));
        }
        pg.strokeWeight(n-i);
        pg.line(x1, y1, x2, y2);
    }
    pg.pop();
}

function special_star(pg, x, y, s, p, n){
    pg.push();
    pg.noStroke();
    for(let t = 0; t < n; t++){
        pg.fill(lerpColor(p?red1:blue1, white, t/n));
        let s_ = s*(1 - t/n)
        pg.beginShape();
        for(let i = 0; i < 5; i++){
            let x_ = x + s_*sin(TWO_PI*i/5);
            let y_ = y - s_*cos(TWO_PI*i/5);
            pg.vertex(x_, y_);
            x_ = x + s_*0.4*sin(TWO_PI*(2*i+1)/10);
            y_ = y - s_*0.4*cos(TWO_PI*(2*i+1)/10);
            pg.vertex(x_, y_);
        }
        pg.endShape(CLOSE);
    }
    pg.pop();
}

function lerp_r(r1, r2, d){
    if(d <= 0) return r1;
    if(d >= 1) return r2;
    if(r1 >= r2){
        if(r1 - r2 <= TWO_PI - r1 + r2){
            return (1-d)*r1 + d*r2;
        }else{
            let r = (1-d)*r1 + d*(TWO_PI+r2);
            if(r >= TWO_PI){
                r -= TWO_PI;
            }
            return r;
        }
    }else{
        if(r2 - r1 <= TWO_PI - r2 + r1){
            return (1-d)*r1 + d*r2;
        }else{
            let r = d*r2 +(1-d)*(TWO_PI+r1);
            if(r >= TWO_PI){
                r -= TWO_PI;
            }
            return r;
        }
    }
}
