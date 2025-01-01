
function BattleCanvas(_ref) {
    var battleState = _ref.battleState;

    return React.createElement(
        "div",
        { className: "content-box", style: { display: "grid", gridTemplateColumns: "480px 200px", gridTemplateRows: "224px 120px", gap: "5px", width: "700px" } },
        React.createElement(BattlePane, { scene: scene }),
        React.createElement(ControlPane, null),
        React.createElement(BattleLog, null)
    );
}

function BattlePane(_ref2) {
    var battleState = _ref2.battleState,
        scene = _ref2.scene;

    var scenePath = scene.replace(/\\/g, '\\\\');
    return React.createElement("div", { style: { gridColumn: "1", gridRow: "1", backgroundImage: "url(" + scenePath + ")", border: "1px solid black", position: "relative" } });
}

function ControlPane(_ref3) {
    var battleState = _ref3.battleState;

    return React.createElement("div", { style: { gridColumn: "1", gridRow: "2" } });
}

function BattleLog(_ref4) {
    var battleState = _ref4.battleState;

    return React.createElement("textarea", { style: { gridColumn: "2", gridRow: "1 / span 2" }, id: "chat-log", cols: "100", rows: "20" });
}

var domNode = document.getElementById('battle');
var root = ReactDOM.createRoot(domNode);
root.render(React.createElement(BattleCanvas, { battleState: initialState, scene: scene }));