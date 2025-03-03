'use client'
import Image from "next/image";
import React, { useState, useEffect, useRef, useCallback } from "react";
import Redirect from "@/app/components/redirect";

export default function Home() {

  useEffect(() => {
    // document.location = "/animeop";
  });


  return (
    <div className="flex flex-col h-screen place-items-center justify-start gap-20 mt-16">
      <div>
        Welcome to the Abbotts Portfolio
      </div>
      <div className="flex flex-col h-fit gap-12">
        <Redirect text="Anime OP/ED Theme Player" location="/animeop"></Redirect>
        <Redirect text="Shiny Hunter" location="/animeop"></Redirect>
        <Redirect text="Good Calc" location="https://goodcalc.vercel.app/"></Redirect>
        <Redirect text="RNG Lotto Wheel" location="https://lottery-nine-tau.vercel.app/"></Redirect>
      </div>
    </div>
  );

};
