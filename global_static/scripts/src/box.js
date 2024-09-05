

function listToMatrix(list, elementsPerSubArray) {
    var matrix = [], i, k;
    if (list.length < 1) {
        matrix[0] = [];
        return matrix;
    }
    for (i = 0, k = -1; i < list.length; i++) {
        if (i % elementsPerSubArray === 0) {
            k++;
            matrix[k] = [];
        }
        matrix[k].push(list[i]);
    }
    return matrix;
}

function Box({ pokemonList }) {
    // Convert back to dict and set as state variable
    pokemonList = pokemonList.map(pkmn => (JSON.parse(pkmn)));

    // Set the state variables
    const [rowCount, setRows] = React.useState(5);
    //const [pokemon, setPokemon] = React.useState(pokemonList)
    // Init states for sorting and filtering
    const [sortField, setSortField] = React.useState("caught_date");
    const [sortOrder, setSortOrder] = React.useState("asc");
    const [filterTag, setFilterTag] = React.useState("");
    const [searchWord, setSearchWord] = React.useState("");

    // For Pokemon selection
    const [selectedPokemon, setSelectedPokemon] = React.useState({id: null});

    console.log(selectedPokemon);

    // Apply the relevant filters
    var tempList = structuredClone(pokemonList);
    if (filterTag) {
        if (filterTag == "shiny") {
            tempList = tempList.filter(pkmn => pkmn.shiny);
        } else {
            tempList = tempList.filter(pkmn => pkmn.box_tag === filterTag);
        }
    }
    if (searchWord) {
        tempList = tempList.filter(pkmn => pkmn.name.toLowerCase().includes(searchWord.toLowerCase()));
    }
    // Sort
    if (sortOrder == "asc") {
        tempList = tempList.sort((a, b) => Number(a[sortField]) - Number(b[sortField]));
    } else {
        tempList = tempList.sort((a, b) => Number(b[sortField]) - Number(a[sortField]));
    }

    // Create the pages, filling out pages if needed
    var pokemonPages = listToMatrix(tempList, rowCount * 6);
    while (pokemonPages[pokemonPages.length - 1].length < rowCount * 6) pokemonPages[pokemonPages.length - 1].push(null);

    return (
        <div className="container">
            <div className="row">
                <div className="col-3">
                    <PokemonDisplay selectedPokemon={selectedPokemon} />
                </div>
                <div className="col-6">
                    <BoxTabs pokemonPages={pokemonPages}
                        selectedPokemon={selectedPokemon} setSelectedPokemon={setSelectedPokemon}/>
                </div>
                <div className="col-3">
                    <BoxControls rowCount={rowCount} setRows={setRows}
                        sortField={sortField} setSortField={setSortField}
                        sortOrder={sortOrder} setSortOrder={setSortOrder}
                        filterTag={filterTag} setFilterTag={setFilterTag}
                        searchWord={searchWord} setSearchWord={setSearchWord} />
                </div>
            </div>
        </div>
    )
}

function PokemonDisplay({ selectedPokemon }) {
    if (selectedPokemon["id"] === null) {
        return (<div></div>);
    } else {
        console.log(selectedPokemon["id"]);
        console.log(selectedPokemon["id"] === null);
        var styling = {width: '100%', display: 'block', textAlign: 'center'};
        var textStyle = {marginBottom: '2px'}
        // Get the image
        var fileName = selectedPokemon["dex_number"];
        if (selectedPokemon["shiny"]) fileName = fileName + "-s";
        var filePath = imgPath + fileName + ".png"
        // Gender symbol
        var gender = "";
        if (selectedPokemon["sex"] == "m") {
            gender = (<span style={{color:'blue'}}>&#9794;</span>);
        } else if (selectedPokemon["sex"] == "f") {
            gender = (<span style={{color:'magenta'}}>&#9792;</span>);
        }
        return (
            <div className="content-box" style={styling}>
                <h4>{selectedPokemon["name"]}{selectedPokemon["shiny"] ? " (s)": ""}</h4>
                <img src={filePath} className="center portrait" />
                <div className="center">
                    <p style={textStyle}>Level {selectedPokemon["level"]} {gender}</p>
                    <p style={textStyle}>{selectedPokemon["nature"].charAt(0).toUpperCase() + selectedPokemon["nature"].slice(1)}</p>
                    <table className="center">
                    <tbody>
                        <tr>
                            <th>HP</th>
                            <td>{selectedPokemon["hp_stat"]}</td>
                            <td style={{color: 'orange'}}>({selectedPokemon["hp_iv"]})</td>
                            <td style={{color: 'green'}}>(+{selectedPokemon["hp_ev"]})</td>
                        </tr>
                        <tr>
                            <th>Attack</th>
                            <td>{selectedPokemon["atk_stat"]}</td>
                            <td style={{color: 'orange'}}>({selectedPokemon["atk_iv"]})</td>
                            <td style={{color: 'green'}}>(+{selectedPokemon["atk_ev"]})</td>
                        </tr>
                        <tr>
                            <th>Defense</th>
                            <td>{selectedPokemon["def_stat"]}</td>
                            <td style={{color: 'orange'}}>({selectedPokemon["def_iv"]})</td>
                            <td style={{color: 'green'}}>(+{selectedPokemon["def_ev"]})</td>
                        </tr>
                        <tr>
                            <th>Sp. Attack</th>
                            <td>{selectedPokemon["spa_stat"]}</td>
                            <td style={{color: 'orange'}}>({selectedPokemon["spa_iv"]})</td>
                            <td style={{color: 'green'}}>(+{selectedPokemon["spa_ev"]})</td>
                        </tr>
                        <tr>
                            <th>Sp. Defense</th>
                            <td>{selectedPokemon["spd_stat"]}</td>
                            <td style={{color: 'orange'}}>({selectedPokemon["spd_iv"]})</td>
                            <td style={{color: 'green'}}>(+{selectedPokemon["spd_ev"]})</td>
                        </tr>
                        <tr>
                            <th>Speed</th>
                            <td>{selectedPokemon["spe_stat"]}</td>
                            <td style={{color: 'orange'}}>({selectedPokemon["spe_iv"]})</td>
                            <td style={{color: 'green'}}>(+{selectedPokemon["spe_ev"]})</td>
                        </tr>
                    </tbody>
                    </table>
                    <button>Details</button>
                    <button>Add to Party</button>
                    <button>View in Pokedex</button>
                    <button>Add Tag</button>
                    <button>Lock</button>
                    <button>Release</button>
                </div>
            </div>
        )
    }
}

function BoxControls({ rowCount, setRows, sortField, setSortField, sortOrder, setSortOrder, filterTag, setFilterTag, searchWord, setSearchWord }) {
    // Filter by tag then by search word
    return (
        <div className="control-box">
        <h5>BOX SORTING</h5>
            <table>
            <tbody>
                <tr>
                    <th>Search:</th>
                    <td>
                    <input
                        value={searchWord}
                        style={{width: "100%"}}
                        onChange={e => setSearchWord(e.target.value)}
                    />
                    </td>
                </tr>
                <tr>
                    <th>Sort by:</th>
                    <td>
                    <select value={sortField} style={{width: "100%"}} onChange={e => setSortField(e.target.value)}>
                        <option value="caught_date">Caught date</option>
                        <option value="dex_number">Dex number</option>
                        <option value="level">Level</option>
                        <option value="bst">Base stat total</option>
                        <option value="iv_total">IV total</option>
                    </select>
                    </td>
                </tr>
                <tr>
                    <th>Order:</th>
                    <td>
                    <select value={sortOrder} style={{width: "100%"}} onChange={e => setSortOrder(e.target.value)}>
                        <option value="asc">Ascending</option>
                        <option value="desc">Descending</option>
                    </select>
                    </td>
                </tr>
                <tr>
                    <th>Filter:</th>
                    <td>
                    <select value={filterTag} style={{width: "100%"}} onChange={e => setFilterTag(e.target.value)}>
                        <option value="">None</option>
                        <option value="circle">Circle</option>
                        <option value="star">Star</option>
                        <option value="square">Square</option>
                        <option value="diamond">Diamond</option>
                        <option value="shiny">Shiny</option>
                    </select>
                    </td>
                </tr>
                <tr>
                    <th>Per page:</th>
                    <td>
                    <select value={rowCount * 6} style={{width: "100%"}} onChange={e => setRows(e.target.value / 6)}>
                        <option value="24">24</option>
                        <option value="30">30</option>
                        <option value="36">36</option>
                        <option value="48">48</option>
                        <option value="60">60</option>
                    </select>
                    </td>
                </tr>
            </tbody>
            </table>
        <br/>
        <h5>ADVANCED</h5>





        </div>
    )
}

function BoxTabs({ pokemonPages, selectedPokemon, setSelectedPokemon }) {
    // Logic for handling tab opening and closing
    const [currentTab, newTab] = React.useState(0);
    const pokemonTabs = pokemonPages.map((page, index) => {
        return (
            <div key={"page" + index} style={(index == currentTab ? {} : {display:'none'})}>
                <BoxPage page={page} idx={index} selectedPokemon={selectedPokemon} setSelectedPokemon={setSelectedPokemon} />
            </div>
        );
    });
    const tabOpeners = pokemonPages.map((page, index) => {
        return <button className={"page-select"} key={"btn" + index} onClick={() => newTab(index)}>{index + 1}</button>
    });
    return (
        <div className="tabs" style={{textAlign: 'center'}}>
            <h5>Pages</h5>
            {tabOpeners}
            {pokemonTabs}
        </div>
    )
}

function BoxPage({ page, idx, selectedPokemon, setSelectedPokemon }) {
    const pokemonRows = listToMatrix(page, 6).map((row, index) => {
        return <BoxRow row={row} key={"row" + index} selectedPokemon={selectedPokemon} setSelectedPokemon={setSelectedPokemon} />;
    });

    return (

        <table className={"right"}>
            <tbody>
                {pokemonRows}
            </tbody>
        </table>
    )

}

function BoxRow({ row, selectedPokemon, setSelectedPokemon }) {
    const pokemonCells = row.map((cell, index) => {
        return <BoxCell cell={cell} key={"cell"+index} selectedPokemon={selectedPokemon} setSelectedPokemon={setSelectedPokemon} />;
    });
    return (
        <tr>
            {pokemonCells}
        </tr>
    )
}

function BoxCell({ cell, selectedPokemon, setSelectedPokemon }) {
    if (cell) {
        // Get the image
        var fileName = cell["dex_number"];
        if (cell["shiny"]) fileName = fileName + "-s";
        var filePath = imgPath + fileName + ".png"
        // Highlight if selected
        if (selectedPokemon["id"] == cell["id"]) {
            var styling = {backgroundColor: 'rgba(210, 219, 224, 0.8)'}
        } else {
            var styling = {};
        }
        // Gender symbol
        var gender = "";
        if (cell["sex"] == "m") {
            gender = (<span style={{color:'blue'}}>&#9794;</span>);
        } else if (cell["sex"] == "f") {
            gender = (<span style={{color:'magenta'}}>&#9792;</span>);
        }
        var cellRender = (
            <div className={"box-cell select-card".concat(cell["shiny"] ? " shiny": "")} onClick={() => setSelectedPokemon(cell)} style={styling}>
                <h1>{cell["name"]}</h1>
                Level {cell["level"]} {gender}
                <img src={filePath}/>
            </div>
        );
    } else {
        var cellRender = <div className="box-cell select-card"></div>;
    }
    return (
        <td>
            {cellRender}
        </td>
    )
}

const domNode = document.getElementById('box');
const root = ReactDOM.createRoot(domNode);
root.render(<Box pokemonList={(boxData)}/>);