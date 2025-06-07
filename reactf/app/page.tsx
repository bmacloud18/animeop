'use client'
import Image from "next/image";
import React, { useState, useEffect, useRef, useCallback } from "react";
import Redirect from "@/app/components/redirect";
import { Inter, Archivo_Black } from "next/font/google";



const archivo = Archivo_Black({
  subsets: ["latin"],
  weight: "400"
});

export default function Home() {

  useEffect(() => {

  });


  return (
    <div className={`flex flex-col h-screen place-items-center justify-start gap-20 mt-16 ${archivo.className}`}>
      <div className="p-4 underline text-4xl">
        Welcome to the Abbott Portfolio
      </div>
      <div className="flex flex-col h-fit gap-12">
        <Redirect text="Anime OP/ED Theme Channel" location="/animeop"></Redirect>
        <Redirect text="Shiny Hunter" location="http://ec2-3-16-129-81.us-east-2.compute.amazonaws.com"></Redirect>
        <Redirect text="Good Calc" location="https://goodcalc.vercel.app/"></Redirect>
        <Redirect text="RNG Lotto Wheel" location="https://lottery-nine-tau.vercel.app/"></Redirect>
      </div>
      <div>
        <Redirect text="GitHub" location="https://github.com/bmacloud18/animeop"></Redirect>
      </div>
    </div>
  );
};
