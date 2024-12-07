
function BattleCanvas({ battleState }) {
    return (
        <div className="content-box" style={{display: "grid", gridTemplateColumns: "480px 200px", gridTemplateRows: "224px 120px", gap: "5px", width: "700px"}}>
            <BattlePane scene={scene}/>
            <ControlPane/>
            <BattleLog/>
        </div>
    )
}

function BattlePane({ battleState, scene }) {
    const scenePath = scene.replace(/\\/g, '\\\\');
    return (
        <div style={{gridColumn: "1", gridRow: "1", backgroundImage: `url(${scenePath})`, border: "1px solid black", position: "relative"}}></div>
    )
}

function ControlPane({ battleState }) {
    return (
        <div style={{gridColumn: "1", gridRow: "2"}}></div>
    )
}

function BattleLog({ battleState }) {
    return (
        <textarea style={{gridColumn: "2", gridRow: "1 / span 2"}} id="chat-log" cols="100" rows="20">
        </textarea>
    )
}

const domNode = document.getElementById('battle');
const root = ReactDOM.createRoot(domNode);
root.render(<BattleCanvas battleState={(initialState)} scene={(scene)}/>);