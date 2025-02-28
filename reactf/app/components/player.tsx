"use client";
import React, { useState, useEffect, useRef } from "react";

import ReactPlayer from 'react-player/youtube'
import screenfull from 'screenfull'
import { Queue } from 'queue-typescript';

import api from "@/app/APIclient";
import Duration from "@/app/components/duration";

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


    const [player, setPlayer] = useState<ReactPlayer | undefined>(undefined);

    const playerRef = useRef(player);

    function load(url: string) {
        setURL(url);
        setPlayed(0);
        setLoaded(0);
        setPip(false);
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

    const handleSeekMousedown = (event: any) => {
        setSeeking(true);
    }

    const handleSeekChange = (event: any) => {
        setPlayed(parseFloat(event.target.value));
    }

    const handleSeekMouseUp = (event: any) => {
        setSeeking(false);
        if (player)
            player?.seekTo(parseFloat(event.target.value));
    }

    function handleProgress() {
        console.log('onProgress', URL, pip, playing, controls, volume, muted, played, loaded, duration, playbackRate, loop, seeking)
    }

    function handleEnded() {
        console.log('video end');
        if (q.length > 0) {
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
        
        

    }, []);

    return (
        <div className="player">
            <ReactPlayer
              ref={playerRef}
              className='react-player'
              width='100%'
              height='100%'
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
    )
}
    
