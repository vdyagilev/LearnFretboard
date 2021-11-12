const chalk = require('chalk'); 
const readline = require("readline");
const util = require('util')
const prompt = require("prompt-sync")({ sigint: true });
const { Mode, Note } = require("@tonaljs/tonal");

// p;layng sound
const spawn = require("child_process").spawn;

function wc_hex_is_light(color) {
    const hex = color.replace('#', '');
    const c_r = parseInt(hex.substr(0, 2), 16);
    const c_g = parseInt(hex.substr(2, 2), 16);
    const c_b = parseInt(hex.substr(4, 2), 16);
    const brightness = ((c_r * 299) + (c_g * 587) + (c_b * 114)) / 1000;
    return brightness > 155;
}

const tones = [
    "a",
    "a#",
    "b",
    "bb",
    "c",
    "db", 
    "c#",
    "d",
    "d#",
    "eb",
    "e",
    "f",
    "f#",
    "gb",
    "g",
    "g#",
    "ab",
]
const colors = {
    "a": "#e23232",
    "bbb": "#e23232",
    "a#": "#5ca3ff",
    "bb": "#5ca3ff",
    "b": "#ba25f5",
    "b#": "#e3e3e3", 
    "cb": "#ba25f5",
    "c": "#e3e3e3",
    "c#": "#c6f7fd",
    "db": "#c6f7fd", 
    "d": "#45d856",
    "c##": "#45d856",
    "ebb": "#45d856",
    "d#": "#fce61c",
    "eb": "#fce61c",
    "e": "#fa851f",
    "d##": "#fa851f",
    "e#": "#3d3c3c",
    "fb": "#fa851f",
    "f": "#3d3c3c",
    "f#": "#00027a",
    "gb": "#00027a",
    "g": "#6d411a",
    "f##": "#6d411a",
    "abb": "#6d411a",
    "g#": "#961724",
    "ab": "#961724",
    "g##": "#e23232",
}

const modes = ["ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"]

function capitalize(s)
{
    return s[0].toUpperCase() + s.slice(1);
}

function generateScaleText(mode, rootTone) {
    const notes = Mode.notes(mode, rootTone)
    let str = ""

    for (let i=0; i<notes.length; i++) {
        let note = notes[i]
        const colorHex = colors[note.toLowerCase()]

        let color = chalk.bgHex(colorHex)
        if (Math.random() > 0.5) {
            note = " "
        }

        if (wc_hex_is_light(colorHex)) {
            color = color.whiteBright//color.blackBright
        } else {
            color = color.whiteBright
        }
        
        str = str + color.bold("  " + note + "  ")
    }
    // add root at end again
    str = str + chalk.bgHex(colors[rootTone.toLowerCase()]).whiteBright.bold("  " + capitalize(rootTone) + "  ")
    return str
}

// wait
function spinWait(seconds) {
    var waitTill = new Date(new Date().getTime() + seconds * 1000);
    while(waitTill > new Date()){}
}

function playScale(mode, rootTone, octave) {
    const notes = Mode.notes(mode, rootTone)

    let freqLstStr = ""
    
    function playNotes() {
        for (let i=0; i< notes.length; i++) {
            const noteName = notes[i]
    

            const freq = Math.floor(Note.get(noteName + octave).freq)

            freqLstStr += freq 
            
            freqLstStr += ","
        }    
        freqLstStr += Math.floor(Note.get(notes[0] + octave).freq)

        const duration = 0.5 + Math.random()*0.1 - Math.random()*0.1

        const child_python = spawn('python3',["play_freq.py", freqLstStr, duration])

        spinWait(duration * 10)
    }

    playNotes()
}


function main() {
    
    while (true) {
        // get random scale degree 1-7
        const scaleDegree = Math.floor(Math.random() * 7)
        const mode = modes[scaleDegree]
        const rootTone = tones[Math.floor(Math.random() * 12)]
        const scaleText = generateScaleText(mode, rootTone)
        const octave = 2+Math.floor(Math.random()*3)

        // clear console
        //console.clear()
        
        // ask user question and get input
        const textColor = "#A9B4C2"
        const question = chalk.hex(textColor).dim("What is this mode ") + scaleText + chalk.hex(textColor).dim(" ?")
        console.log(question)

        guess = prompt()
        const correctText = chalk.green.bold("Correct! It was " + rootTone+ " " + mode + "\n")
        const incorrectText = chalk.red.underline.bold("Incorrect! It was " + rootTone + " " + mode + "\n")
        
        let waitSeconds
        if (guess == mode) {
            console.log(correctText)
            waitSeconds = 1
        } else {
            console.log(incorrectText)
            waitSeconds = 3
        }

        // play scale TODO
        playScale(mode, rootTone, octave)
        
        }
}

main()