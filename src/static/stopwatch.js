class StopWatch{

    constructor(){
        this._time = 0;
        this._prev_time = performance.now();
        this._rate = 1;
        this._paused = true;

        this._new_time = 0;

        this._queue = {
            start: false,
            pause: false,
            reset: false,
            time: false
        };
    }

    get time(){
        return this._time;
    }

    set time(new_time){
        this._queue.time = true;
        this._new_time = new_time;
    }

    get isPaused(){
        return this._paused;
    }

    get rate(){
        return this._rate;
    }

    // noinspection JSUnusedGlobalSymbols
    set rate(new_rate){
        this._rate = new_rate;
    }

    start(){ // IMPORTANT: you might want to update after unpause, as it will effectively unpause at next update
        this._queue.start = true;
        this._queue.pause = false;
    }

    pause(){ // IMPORTANT: you might want to update after pause, as it will effectively pause at next update
        this._queue.pause = true;
        this._queue.start = false;
    }

    reset(){
        this._queue.reset = true;
        this._queue.start = false;
        this._queue.time = false;
    }

    update(){
        let t = performance.now();
        if(!this._paused)this._time += this.rate*(t - this._prev_time);
        this._prev_time = t;

        if(this._queue.reset){
            this._time = 0;
            this._rate = 1;
            this._paused = true;
            this._queue.reset = false;
        }
        if(this._queue.time){
            this._time = this._new_time;
            this._queue.time = false;
        }
        if(this._queue.start){
            this._paused = false;
            this._queue.start = false;
        }
        if(this._queue.pause){
            this._paused = true;
            this._queue.pause = false;
        }
    }
}
