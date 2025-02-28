"use client";
import React, { useState, useEffect, useRef } from "react";

import ReactPlayer from 'react-player/youtube'
import screenfull from 'screenfull'
import { Queue } from 'queue-typescript';
import packageInfo from '../../package.json'

import api from "@/app/APIclient";
import Duration from "@/app/components/duration";
import ControlButton from "@/app/components/controlButton";

export default function Player ({
    queue,
}: {
    queue: Queue<string>,
}) {
    const [q, setQ] = useState<Queue<string>>(queue);
    const [URL, setURL] = useState<string>('');
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

    const SEPARATOR = ' · '






    const [player, setPlayer] = useState<ReactPlayer | undefined>(undefined);

    const playerRef = useRef(player);

    function load(url: string) {
        setURL(url);
        setPlayed(0);
        setLoaded(0);
        setPip(false);
    }

    const ref = (player: any) => {
        setPlayer(player);
    }

    function handlePlayPause() {
        setPlaying(!playing);
    }

    function handleStop() {
        setPlaying(false);
        setURL('');
    }

    function handleToggleControls() {
        const curl = URL;
        setControls(!controls);
        setURL('');
        load(curl);
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

    const handleSetPlaybackRate = (event: any) => {
        setPlaybackRate(parseFloat(event.target.value));
    }

    function handleOnPlaybackRateChange(speed: number) {
        setPlaybackRate(speed);
    }

    function handleTogglePIP() {
        setPip(!pip);
    }

    function handlePlay() {
        console.log('onplay');
        setPlaying(true);
    }

    function handlePause() {
        console.log('onpause');
        setPlaying(false);
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

    const handleProgress = (state: {
        played: React.SetStateAction<number>;
        loaded: React.SetStateAction<number>;
      }) =>  {
        console.log('onProgress', URL, pip, playing, controls, volume, muted, played, loaded, duration, playbackRate, loop, seeking)
        setPlayed(state.played);
        setLoaded(state.loaded);
    }

    function handleEnded() {
        console.log('video end');
        if (q.length > 0 && !loop) {
            let next = q.dequeue();
            setURL(next);
        }
        else {
            setPlaying(loop);
        }
    }

    function handleDuration(d: number) {
        console.log('on duration', d);
        setDuration(d);
    }

    function handleClickFullscreen() {
        const playerdiv = document.querySelector('.react-player');
        if (playerdiv)
            screenfull.request(playerdiv);
    }

    function renderLoadButton(url: string, label: any) {
        return (
            <button onClick={() => load(url)}>
                {label}
            </button>
        )
    }

     useEffect(() => {
        load("https://www.youtube.com/watch?v=G8CFuZ9MseQ");
        
    }, []);

    return (
        <div className="flex flex-col player-main h-screen">
            <div className="flex flex-col player flex flex-col h-256 pointer-events-none">
                <ReactPlayer
                    ref={ref}
                    className='flex flex-col react-player h-64'
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
                    onPlaybackRateChange={handleOnPlaybackRateChange}
                    onSeek={e => console.log('onSeek', e)}
                    onEnded={handleEnded}
                    onError={e => console.log('onError', e)}
                    onProgress={handleProgress}
                    onDuration={handleDuration}
                    onPlaybackQualityChange={(e: any) => console.log('onPlaybackQualityChange', e)}
               />
            </div>
            <table className="flex flex-row gap-2">
                <tbody className="flex flex-row gap-2">
                    <tr className="flex flex-col">
                        <td className="flex flex-row gap-2">
                            <ControlButton onClick={handleStop} text="Stop"></ControlButton>
                            <ControlButton onClick={handlePlayPause} text={playing ? 'Pause' : 'Play'}></ControlButton>
                            <ControlButton onClick={handleClickFullscreen} text="Full"></ControlButton>
                            {ReactPlayer.canEnablePIP(URL) &&
                                <button onClick={handleTogglePIP}>{pip ? 'Disable PIP' : 'Enable PIP'}</button>}
                        </td>
                    </tr>
                    <tr>
                        <th>Seek</th>
                        <td>
                            <input
                                type='range' min={0} max={0.999999} step='any'
                                value={played}
                                onMouseDown={handleSeekMouseDown}
                                onChange={handleSeekChange}
                                onMouseUp={handleSeekMouseUp}
                           />
                        </td>
                    </tr>
                    <tr>
                        <th>Volume</th>
                        <td>
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
                    <tr>
                        <th>
                            <label htmlFor='muted'>Muted</label>
                        </th>
                        <td>
                            <input id='muted' type='checkbox' checked={muted} onChange={handleToggleMute}/>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            <label htmlFor='loop'>Loop</label>
                        </th>
                        <td>
                            <input id='loop' type='checkbox' checked={loop} onChange={handleToggleLoop}/>
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
            <footer className='footer flex flex-row'>
            Version <strong>{packageInfo.version}</strong>
                {SEPARATOR}
                <a href='https://github.com/CookPete/react-player'>GitHub</a>
                {SEPARATOR}
                <a href='https://www.npmjs.com/package/react-player'>npm</a>
            </footer>
        </div>
        
    )
}
    
