import { MouseEventHandler } from "react";

export default function ControlButton({
    text,
    onClick
}: {
    text:string,
    onClick: MouseEventHandler
}) {
    return (
        <button onClick={onClick} className="border-2 border-black rounded-lg p-1">{text}</button>
    );
}