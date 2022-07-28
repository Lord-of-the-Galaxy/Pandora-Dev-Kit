class AutoProgressBar{
    constructor(x, y, w, h, c1, c2, flip = false, value = 1, size = 10, min_pixels_quantum = 8, r = -1){ // (x,y,w,h) defines the BOUNDING BOX, min_pixels_quantum defines the minimum size at which it remains quantum
        this.x = x, this.y = y, this.w = w, this.h = h;
        this._value = value;
        this._size = size;
        this.flip = flip; // if it is flipped, it fills RTL
        this.mp = min_pixels_quantum;
        if(r < 0){
            this.r = h/6;
        }else{
            this.r = r;
        }
        this.c1 = c1, this.c2 = c2;
    }

    draw(pg){
        pg.push();
        pg.noFill();
        pg.stroke(this.c2);
        pg.strokeWeight(2);
        pg.rect(this.x, this.y, this.w, this.h, this.r);
        pg.noStroke();
        pg.fill(this.c1);
        let flip = this.flip;
        let h = this.h - 6;
        let w = this.w - 6;
        let x = this.x + 3;
        let y = this.y + 3;
        let r = this.r>=1?(this.r - 1):0;
        let s = w/this._size;
        let inc = 1;
        while(s < this.mp){
            s *= 10;
            inc *= 10;
        }
        if(this._value/inc <= 1 && this._value/inc > r/s){
            if(flip){
                pg.rect(x+w-(this._value*s/inc)+1, y, (this._value*s/inc)-1, h, r)
            }else{
                pg.rect(x, y, (this._value*s/inc)-1, h, r);
            }
        }else if(this._value/inc > 1){
            if(flip){
                pg.rect(x+w-s+1, y, s-1, h, 0, r, r, 0)
                let i;
                for(i = 1; i < (this._value/inc) - 1; i++){
                    pg.rect(x+w-s - i*s + 1, y, s-2, h);
                }
                pg.rect(x+w-((this._value - i*inc)*s/inc) - i*s, y, ((this._value - i*inc)*s/inc)-1, h, r, 0, 0, r);
            }else{
                pg.rect(x, y, s-1, h, r, 0, 0, r);
                let i;
                for(i = 1; i < (this._value/inc)-1; i++){
                    pg.rect(x + i*s + 1, y, s-2, h);
                }
                pg.rect(x + i*s + 1, y, ((this._value - i*inc)*s/inc)-1, h, 0, r, r, 0);
            }
        }
        if(h > 12){
            let txt = (flip?"":"×") + inc + (flip?"×":"");
            pg.fill(this.c1);
            pg.noStroke();
            pg.textSize(h-6);
            pg.text(txt, flip?(x+2):(x+w-pg.textWidth(txt)-2), y+h-4);
        }
        pg.pop();
    }

    get value(){
        return this._value;
    }

    set value(new_value){
        if(new_value <= this.size){
            this._value = new_value;
        }else{
            this._value = this.size;
        }
    }

    get size(){
        return this._size;
    }

    set size(new_size){
        if(new_size >= this.value){
            this._size = new_size;
        }else{
            this._size = this._value;
        }
    }
}

const levels = [2, 3, 4, 6, 8, 10, 15, 20, 30, 40, 60, 80, 100, 150, 200, 300, 400, 600, 800, 1000, 1500, 2000, 3000, 4000, 6000, 8000, 10000] // this can be changed, that's why it's been coded in as an array

function progressBarLinkedUpdate(bars, values, ls_max = 0.5, ls_alt_max = 0.6, ls_alt_min = 0.4, hs_max = 0.9, hs_alt_max = 0.8, hs_alt_min = 0.6){ // bars and values must be same length
    let n = bars.length;
    let csa = new Array(n);
    let cs = 0;
    let miv = values[0];
    let mav = values[0];
    for(let i = 0; i < n; i++){
        csa[i] = bars[i].size;
        if(cs < csa[i]){
            cs = csa[i];
        }
        if(miv > values[i]){
            miv = values[i];
        }
        if(mav < values[i]){
            mav = values[i];
        }
    }
    let csi = -1;
    let m = levels.length;
    for(let i = 0; i < m; i++){
        if(cs <= levels[i]){
            csi = i;
            cs = levels[i];
            break;
        }
    }
    if(csi === -1 || mav > levels[m - 1]){
        // we can't handle this case, so let it stay as is, but make all equal size and at least big enough for max value
        let s = mav>cs?mav:cs;
        for(let i = 0; i < n; i++){
            bars[i].size = s;
            bars[i].value = values[i];
        }
        return;
    }
    let ns = cs, nsi = csi;
    while(mav/ns > hs_max && nsi < m-1){
        nsi++;
        ns = levels[nsi];
    }
    while(mav/ns > hs_alt_max && miv/ns > hs_alt_min && nsi < m-1){
        nsi++;
        ns = levels[nsi];
    }
    while(mav/ns <= ls_max && nsi > 0){
        nsi--;
        ns = levels[nsi];
    }
    while(mav/ns <= ls_alt_max && miv/ns <= ls_alt_min && nsi > 0){
        nsi--;
        ns = levels[nsi];
    }
    // ns is the new size now
    for(let i = 0; i < n; i++){
        if(bars[i].value > ns){
            bars[i].value = values[i];
            bars[i].size = ns;
        }else{
            bars[i].size = ns;
            bars[i].value = values[i];
        }
    }
}
