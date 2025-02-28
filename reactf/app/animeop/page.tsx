"use client";
import React, { useState, useEffect, useRef } from "react";
import ReactPlayer from 'react-player/youtube'
import screenfull from 'screenfull'

import { Queue } from 'queue-typescript';


import api from "@/app/APIclient";
import Player from "@/app/components/player";

export default function Homepage() {
    const [q, setQ] = useState<Queue<string>>(new Queue<string>());
    const [url, setURL] = useState<string>('');

    useEffect(() => {
        Promise.all([api.getVideos("naruto")]).then((res) => {
            console.log("retrieved urls");
            const rq: string[] = res[0];
            const first = res[0][0];
            setQ(new Queue<string>(...rq));
            setURL(first);
        }).catch((err) => {
            console.error(err);
        });
    }, []);

    let content;
    if (url != '') {
        content = (
            <Player queue={q}></Player>
        )
    }

    return (
        <main >
            {content}
        </main>
    )
}