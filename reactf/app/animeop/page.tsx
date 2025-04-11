"use client";
import React, { useState, useEffect, useRef, useCallback } from "react";
import ReactPlayer from 'react-player/youtube'
import screenfull from 'screenfull'

import { Queue } from 'queue-typescript';
import packageInfo from '../../package.json'


import api from "@/app/APIclient";
import ControlButton from "@/app/components/controlButton";
import samples from "@/app/samples/urls";


export default function Homepage() {
    const [query, setQuery] = useState<string>('');
    const [q, setQ] = useState<Queue<string[]>>(new Queue<string[]>());
    const [qMap, setMap] = useState<Map<string, string[]>>(new Map<string, string[]>());
    const [URL, setURL] = useState<string>('');
    const [history, setHistory] =  useState<Map<string, string>>(new Map<string, string>());
    const [historyQ, setHistoryQ] = useState<Queue<string[]>>(new Queue<string[]>());
    const [title, setTitle] = useState<string>('');
    const [pip, setPip] = useState(false);
    const [playing, setPlaying] = useState(false);
    const [controls, setControls] = useState(false);
    // const [light, setLight] = useState(false);
    const [volume, setVolume] = useState(0.8);
    const [muted, setMuted] = useState(false);
    const [played, setPlayed] = useState(0);
    const [loaded, setLoaded] = useState(0);
    const [duration, setDuration] = useState(0);
    const [playbackRate, setPlaybackRate] = useState(1.0);
    const [loop, setLoop] = useState(false);
    const [seeking, setSeeking] = useState(false);
    const [qShowing, setQShowing] = useState(false);
    const [idx, setIdx] = useState<number>(0);

    const HISTORY_NUM = 11;

    const SEPARATOR = ' · '

    const [player, setPlayer] = useState<ReactPlayer | undefined>(undefined);

    function load(vid: string[]) {
        setURL(vid[0]);
        setTitle(vid[1]);
        setPlayed(0);
        setLoaded(0);
        setPip(false);
        setPlaying(true);
    }

    const retrieveVideos = useCallback(() => {
        Promise.all([api.getVideos(query, history.values())]).then((res) => {
            console.log("retrieved urls", res);
            let arrayQ: string[][] = [[]];
            if (res[0][0])
                arrayQ = res[0];
            let i = idx;
            for (let item of arrayQ)
            {
                item[2] = i + '';
                i++;
            }
            setIdx(i);
            let freshQ = new Queue<string[]>(...arrayQ);
            //for some reason sends empty data in 0 slot
            //still sends 10 results as intended
            freshQ.dequeue();
            const first = freshQ.dequeue(); 
            setQ(freshQ);
            for (let item of freshQ.toArray())
            {
                if (!qMap.has(item[1]))
                    qMap.set(item[2], [item[0], item[1]]);
            }
            load(first);
        }).catch((err) => {
            const arrayQ: string[][] = samples.urls;
            let i = idx;
            for (let item of arrayQ)
            {
                item[2] = i + '';
                i++;
            }
            setIdx(i);
            let freshQ = new Queue<string[]>(...arrayQ);
            const first = freshQ.dequeue();
            setQ(freshQ);
            for (let item of freshQ.toArray())
            {
                if (!qMap.has(item[1]))
                    qMap.set(item[2], [item[0], item[1]]);
            }
            load(first);
            console.error(err);
        });
    }, [query])

    function nextVid() {
        if (q.length > 0) {
            let next = q.dequeue();
            const nurl = next[0];
            //prevent repeats within HISTORY_NUM videos
            if (history.has(nurl)) {
                console.log('skipped dupe');
                nextVid();
            }
            else {
                load(next);
            }
        }
        else {
            retrieveVideos();
        }
    }

    //important so the state of the player can be ascertained
    //necessary for seek functionality and progress updates below
    //ref is set to this const in the player when content is defined
    const ref = (player: any) => {
        setPlayer(player);
    }



    const handleProgress = (state: {
            played: React.SetStateAction<number>;
            loaded: React.SetStateAction<number>; }) =>  {

            // console.log('onProgress', URL, pip, playing, controls, volume, muted, played, loaded, duration, playbackRate, loop, seeking)
            setPlayed(state.played);
            setLoaded(state.loaded);

    }

    function handleSkip() {
        console.log('video skipped');
        nextVid();
    }

    function handleToggleLoop() {
        setLoop(!loop);
    }

    const handleVolumeChange = (event: any) => {
        setVolume(parseFloat(event.target.value));
    }

    function handleToggleMute() {
        setMuted(!muted);
    }

    function handleTogglePIP() {
        setPip(!pip);
    }

    function handleEnablePIP() {
        console.log('enabling pip');
        setPip(true);
    }

    function handleDisablePIP() {
        console.log('disabling pip');
        setPip(false);
    }

    const handleSeekMouseDown = (event: any) => {
        setSeeking(true);
    }

    const handleSeekChange = (event: any) => {
        console.log(event.target.value);
        setPlayed(parseFloat(event.target.value));
        player?.seekTo(played);
    }

    const handleSeekMouseUp = (event: any) => {
        setSeeking(false);
        if (player)
            player?.seekTo(parseFloat(event.target.value));
    }

    //handle adding ended video to history and starting next video
    function handleEnded() {
        console.log('video end no loop');
        historyQ.enqueue([URL, title]);
        history.set(title, URL);
        if (historyQ.length > HISTORY_NUM) {
            const out = historyQ.dequeue();
            if (history.has(out[1]))
                history.delete(out[1]);
        }
            
        nextVid();
    }

    function handlePlayPause() {
        setPlaying(!playing);
    }

    function handlePlay() {
        console.log('onPlay');
        setPlaying(true);
    }

    function handlePause() {
        console.log('onpause');
        setPlaying(false);
    }
    
    function handleClickFullscreen() {
        const playerdiv = document.querySelector('.react-player');
        if (playerdiv)
            screenfull.request(playerdiv);
    }

    function handleError(e: Error) {
        if (e.toString() == '150') {
            console.log('potential licensing error')
            nextVid();
        }
    }

    function removeItem(id: string) {
        console.log('delete clicked', id);
        let uat = qMap.get(id);
        if (uat) {
            let durl = uat[0]
            let title = uat[1];
            qMap.delete(title);
            setQ(new Queue<string[]>(...q.toArray().filter(item => (item[2] !== id))));
            console.log(durl, title, qMap, q);
        }
    }

    function showQ() {
        let boo = !qShowing
        setQShowing(!qShowing);
        console.log(boo);
        
        const qDisplay = document.getElementById("q-display");
        if (boo && qDisplay) {
            qDisplay.classList.remove('hidden');
            setTimeout(() => {
                qDisplay.style.transform = "translateX(-100%)";
            }, 100)
            console.log(qShowing);
        }
        else if (qDisplay) {
            qDisplay.style.transform = "translateX(0)"
            setTimeout(() => {
                qDisplay.classList.add('hidden'); // Hide element after translation
            }, 500);
        }
        
    }

    useEffect(() => {
        if (URL === '') {
            setQuery('');
            retrieveVideos();
        }
        console.log('i fire once');
    }, [URL, retrieveVideos]);

    let content;
    if (URL != '') {
        content = (
            <div className="flex flex-col justify-around w-fit h-full self-center">
            
                <div className="flex flex-col w-3/4 md:w-4/7 lg:w-3/5 aspect-video place-content-center self-center">
                    <div className="p-2 underline text-4xl place-self-center">
                        Anime OP/ED Channel
                    </div>
                    <div className="border-yellow border-8 rounded-lg player-wrapper">
                        <div className="flex flex-col aspect-video pointer-events-none border-2 w-full bg-black rounded-sm border-black">
                            <ReactPlayer
                                ref={ref}
                                className='flex flex-col react-player aspect-video'
                                height='100%'
                                width='100%'
                                url={URL}
                                pip={pip}
                                playing={playing}
                                controls={controls}
                                light={false}
                                loop={loop}
                                playbackRate={playbackRate}
                                volume={volume}
                                muted={muted}
                                onReady={() => console.log('onReady')}
                                onStart={() => console.log('onStart')}
                                onPlay={handlePlay}
                                onEnablePIP={handleEnablePIP}
                                onDisablePIP={handleDisablePIP}
                                onPause={handlePause}
                                onBuffer={() => console.log('onBuffer')}
                                onSeek={e => console.log('onSeek', e)}
                                onEnded={handleEnded}
                                onError={e => handleError(e)}
                                onProgress={handleProgress}
                                onPlaybackQualityChange={(e: any) => console.log('onPlaybackQualityChange', e)}
                            />
                        </div>
                    </div>
                </div>
                <div className="flex flex-col items-center">
                    <div className="border border-2 border rounded-lg p-2">
                        {title}
                    </div>
                </div>
                <div className="flex flex-col w-screen items-center gap-2 p-4">
                    <table className="flex flex-col md:flex-row gap-2  items-center justify-center w-full">
                        <tbody className="flex flex-col md:flex-row gap-4 border-2 rounded-lg p-4 items-center justify-center h-full w-fit">
                            <tr className="flex flex-col size-full">
                                <td className="flex flex-row gap-2 justify-center w-full">
                                    <ControlButton onClick={handleSkip} text="Skip"></ControlButton>
                                    <ControlButton onClick={handlePlayPause} text={playing ? 'Pause' : 'Play'}></ControlButton>
                                    <ControlButton onClick={handleClickFullscreen} text="Full"></ControlButton>
                                    {ReactPlayer.canEnablePIP(URL) &&
                                        <button onClick={handleTogglePIP}>{pip ? 'Disable PIP' : 'Enable PIP'}</button>}
                                </td>
                            </tr>
                            <tr className="flex flex-col items-center w-full">
                                <th>Seek</th>
                                <td className="flex flex-row gap-2 justify-center w-full">
                                    <input
                                        type='range' min={0} max={0.999999} step='any'
                                        value={played}
                                        onMouseDown={handleSeekMouseDown}
                                        onChange={handleSeekChange}
                                        onMouseUp={handleSeekMouseUp}
                                    />
                                </td>
                            </tr>
                            <tr className="flex flex-col items-center w-full">
                                <th>Volume</th>
                                <td className="flex flex-row gap-2 justify-center w-full">
                                    <input type='range' min={0} max={1} step='any' value={volume} onChange={handleVolumeChange}/>
                                </td>
                            </tr>
                            {/* <tr>
                                <th>
                                    <label htmlFor='controls'>Controls</label>
                                </th>
                                <td>
                                    <input id='controls' type='checkbox' checked={controls} onChange={handleToggleControls}/>
                                    <em>&nbsp; Requires player reload</em>
                                </td>
                            </tr> */}
                            <tr className="flex flex-row items-center justify-center gap-2 w-full">
                                <td className="flex flex-col items-center w-fit">
                                    <label htmlFor='muted'>Muted</label>
                                    <input id='muted' type='checkbox' checked={muted} onChange={handleToggleMute}/>
                                </td>
                                <td className="flex flex-col items-center w-fit">
                                    <label htmlFor='loop'>Loop</label>
                                    <input id='loop' type='checkbox' checked={loop} onChange={handleToggleLoop}/>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <ControlButton text="Q" onClick={showQ}></ControlButton>
                                </td>
                            </tr>
                            {/* <tr>
                                <th>Played</th>
                                <td><progress max={1} value={played}/></td>
                            </tr>
                            <tr>
                                <th>Loaded</th>
                                <td><progress max={1} value={loaded}/></td>
                            </tr> */}
                        </tbody>
                    </table>
                    <footer className='footer flex flex-row gap-2 size-fit'>
                        Version 
                        <strong>{packageInfo.version}</strong>
                        {SEPARATOR}
                        <a href='https://github.com/bmacloud18/animeop'>GitHub</a>
                        {SEPARATOR}
                        <a href='https://www.npmjs.com/package/react-player'>npm</a>
                    </footer>
                </div>
            </div>
        )
    }

    let qDisplayBox = (
        <div id="q-display" className="flex flex-col hidden bg-grey justify-between items-center w-[96rem] h-screen border transition-transform duration-500 ease-out">
            <ul className="flex flex-col w-fit min-w-max max-w-[50%] max-h-[75%] overflow-y-scroll border-b">
                {q.toArray().map(item => (
                    <li className="flex flex-row w-full border-b justify-between p-2 w-full gap-2 place-items-center" key={item[2]}>
                        <div className="flex items-center w-full h-12">
                            {item[1]}
                        </div>
                        <ControlButton text="D" onClick={() => removeItem(item[2])}></ControlButton>
                    </li>
                ))}
            </ul>
            <div className="self-end m-4">
                <ControlButton text="Close" onClick={showQ}></ControlButton>
            </div>
        </div>
    )

    return (
        <div className="flex flex-start content-center overflow-hidden">
            <main className="flex flex-col h-screen w-full">
                {content}
            </main>
            {qDisplayBox}
        </div>

    )
}