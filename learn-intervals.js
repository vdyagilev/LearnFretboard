const chalk = require('chalk'); 
const readline = require("readline");
const prompt = require("prompt-sync")({ sigint: true });
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

const tones = ['a','as/bf', 'b', 'c', 'cs/df', 'd', 'ds/ef', 'e', 'f', 'fs/gf', 'g', 'gs/af']
const colors = {
    "a": "#e23232",
    "as/bf": "#5ca3ff",
    "b": "#ba25f5",
    "c": "#e3e3e3",
    "cs/df": "#c6f7fd", 
    "d": "#45d856",
    "ds/ef": "#fce61c",
    "e": "#fa851f",
    "f": "#3d3c3c",
    "fs/gf": "#00027a",
    "g": "#6d411a",
    "gs/af": "#961724",
}
const intervals = ["unison", "minor 2nd", "major 2nd", "minor 3rd", "major 3rd", "perfect 4th",
                    "diminished 5th", "perfect 5th", "minor 6th", "major 6th", "minor 7th", "major 7th",]

function halfStepsBetween(a, b) {
    let halfSteps = 0
    let temp = a
    while (temp != b) {
        if (tones.indexOf(temp) == tones.length-1) {
            temp = tones[0]
        } else {
            temp = tones[tones.indexOf(temp) + 1]
        }
        halfSteps = halfSteps + 1
    }
    return halfSteps
}

 // remove / from accidental
function splitAccidental(tone) {
    const tones = tone.split("/") 
    return tones[Math.floor((Math.random()*tones.length))]
}

function intervalBetween(a, b) {
    const halfSteps = halfStepsBetween(a, b)
    return intervals[halfSteps]
}

function coloredToneText(tone) {
    let toneText = splitAccidental(tone)
    if (Math.random() > 0.5) {
        toneText = " "
    }
    let color = chalk.bgHex(colors[tone])
    if (wc_hex_is_light(colors[tone])) {
        color = color.whiteBright//color.blackBright
    } else {
        color = color.whiteBright
    }
    return color.bold("  " + toneText + "  ")
}



function main() {
    while (true) {
        // get random tones
        let toneA = tones[Math.floor(Math.random()*tones.length)]
        let toneB = tones[Math.floor(Math.random()*tones.length)]
        const interval = intervalBetween(toneA, toneB)
        const halfSteps = halfStepsBetween(toneA, toneB)
        
        
        // ask user question and get input
        const textColor = "#A9B4C2"
        const question = chalk.hex(textColor).dim("What is the interval between ") + coloredToneText(toneA) + chalk.hex(textColor).dim(" and ") + coloredToneText(toneB)+chalk.hex(textColor).dim("?: ")
        guess = prompt(question)
        const correctText = chalk.green.bold("Correct! It was " + interval + " ("+ halfSteps+" halfsteps)\n")
        const incorrectText = chalk.red.underline.bold("Incorrect! It was " + interval+ " ("+ halfSteps+" halfsteps)\n")
        if (guess == interval || guess == halfSteps) {
            console.log(correctText)
        } else {
            console.log(incorrectText)
        }

        // wait
        let sleep = require('util').promisify(setTimeout);
        sleep(1)
    }
}

main()