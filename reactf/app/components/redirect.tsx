import { MouseEventHandler } from "react";

export default function ControlButton({
    text,
    location
}: {
    text:string,
    location: string
}) {
    function handleRedirect() {
        window.location.href = `${location}`
    }
    return (
        <button onClick={handleRedirect} className="border-2 border-black rounded-lg p-1 h-16 w-48 md:w-96 bg-buttonwhite hover:bg-grey">
            {/* <img src="" alt="redirectimage"/> */}
            {text}
        </button>
    );
}