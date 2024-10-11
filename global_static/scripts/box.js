var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

function listToMatrix(list, elementsPerSubArray) {
    var matrix = [],
        i,
        k;
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

function Box(_ref) {
    var pokemonList = _ref.pokemonList;

    // Convert back to dict and set as state variable
    pokemonList = pokemonList.map(function (pkmn) {
        return JSON.parse(pkmn);
    });

    // Set the state variables

    var _React$useState = React.useState(5),
        _React$useState2 = _slicedToArray(_React$useState, 2),
        rowCount = _React$useState2[0],
        setRows = _React$useState2[1];

    // Init states for sorting and filtering


    var _React$useState3 = React.useState("caught_date"),
        _React$useState4 = _slicedToArray(_React$useState3, 2),
        sortField = _React$useState4[0],
        setSortField = _React$useState4[1];

    var _React$useState5 = React.useState("asc"),
        _React$useState6 = _slicedToArray(_React$useState5, 2),
        sortOrder = _React$useState6[0],
        setSortOrder = _React$useState6[1];

    var _React$useState7 = React.useState(""),
        _React$useState8 = _slicedToArray(_React$useState7, 2),
        filterTag = _React$useState8[0],
        setFilterTag = _React$useState8[1];

    var _React$useState9 = React.useState(""),
        _React$useState10 = _slicedToArray(_React$useState9, 2),
        searchWord = _React$useState10[0],
        setSearchWord = _React$useState10[1];

    // For Pokemon selection


    var _React$useState11 = React.useState({ id: null }),
        _React$useState12 = _slicedToArray(_React$useState11, 2),
        selectedPokemon = _React$useState12[0],
        setSelectedPokemon = _React$useState12[1];

    var _React$useState13 = React.useState({ id: null }),
        _React$useState14 = _slicedToArray(_React$useState13, 2),
        displayedPokemon = _React$useState14[0],
        displayPokemon = _React$useState14[1];

    // Context menu handling


    var _useContextMenu = useContextMenu(),
        clicked = _useContextMenu.clicked,
        setClicked = _useContextMenu.setClicked,
        coords = _useContextMenu.coords,
        setCoords = _useContextMenu.setCoords;

    console.log(selectedPokemon);
    console.log(displayedPokemon);
    // Apply the relevant filters
    var tempList = structuredClone(pokemonList);
    if (filterTag) {
        if (filterTag == "shiny") {
            tempList = tempList.filter(function (pkmn) {
                return pkmn.shiny;
            });
        } else {
            tempList = tempList.filter(function (pkmn) {
                return pkmn.box_tag === filterTag;
            });
        }
    }
    if (searchWord) {
        tempList = tempList.filter(function (pkmn) {
            return pkmn.name.toLowerCase().includes(searchWord.toLowerCase());
        });
    }
    // Sort
    if (sortOrder == "asc") {
        tempList = tempList.sort(function (a, b) {
            return Number(a[sortField]) - Number(b[sortField]);
        });
    } else {
        tempList = tempList.sort(function (a, b) {
            return Number(b[sortField]) - Number(a[sortField]);
        });
    }

    // Create the pages, filling out pages if needed
    var pokemonPages = listToMatrix(tempList, rowCount * 5);
    while (pokemonPages[pokemonPages.length - 1].length < rowCount * 5) {
        pokemonPages[pokemonPages.length - 1].push(null);
    }return React.createElement(
        "div",
        { style: { display: "flex" } },
        clicked && React.createElement(ContextMenu, { top: coords.y, left: coords.x, displayPokemon: displayPokemon, selectedPokemon: selectedPokemon }),
        React.createElement(
            "div",
            { style: { display: "flex" } },
            React.createElement(BoxTabs, { pokemonPages: pokemonPages,
                selectedPokemon: selectedPokemon, setSelectedPokemon: setSelectedPokemon,
                setClicked: setClicked, setCoords: setCoords })
        ),
        React.createElement(
            "div",
            { style: { display: "inline-block" } },
            React.createElement(BoxControls, { rowCount: rowCount, setRows: setRows,
                sortField: sortField, setSortField: setSortField,
                sortOrder: sortOrder, setSortOrder: setSortOrder,
                filterTag: filterTag, setFilterTag: setFilterTag,
                searchWord: searchWord, setSearchWord: setSearchWord })
        )
    );
}

function PokemonDisplay(_ref2) {
    var selectedPokemon = _ref2.selectedPokemon;

    if (selectedPokemon["id"] === null) {
        return React.createElement("div", null);
    } else {
        var styling = { width: '100%', display: 'block', textAlign: 'center' };
        var textStyle = { marginBottom: '2px'
            // Get the image
        };var fileName = selectedPokemon["dex_number"];
        if (selectedPokemon["shiny"]) fileName = fileName + "-s";
        var filePath = imgPath + fileName + ".png";
        // Gender symbol
        var gender = "";
        if (selectedPokemon["sex"] == "m") {
            gender = React.createElement(
                "span",
                { style: { color: 'blue' } },
                "\u2642"
            );
        } else if (selectedPokemon["sex"] == "f") {
            gender = React.createElement(
                "span",
                { style: { color: 'magenta' } },
                "\u2640"
            );
        }
        return React.createElement(
            "div",
            { className: "content-box", style: styling },
            React.createElement(
                "h4",
                null,
                selectedPokemon["name"],
                selectedPokemon["shiny"] ? " (s)" : ""
            ),
            React.createElement("img", { src: filePath, className: "center portrait" }),
            React.createElement(
                "div",
                { className: "center" },
                React.createElement(
                    "p",
                    { style: textStyle },
                    "Level ",
                    selectedPokemon["level"],
                    " ",
                    gender
                ),
                React.createElement(
                    "p",
                    { style: textStyle },
                    selectedPokemon["nature"].charAt(0).toUpperCase() + selectedPokemon["nature"].slice(1)
                ),
                React.createElement(
                    "table",
                    { className: "center" },
                    React.createElement(
                        "tbody",
                        null,
                        React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "th",
                                null,
                                "HP"
                            ),
                            React.createElement(
                                "td",
                                null,
                                selectedPokemon["hp_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' } },
                                "(",
                                selectedPokemon["hp_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' } },
                                "(+",
                                selectedPokemon["hp_ev"],
                                ")"
                            )
                        ),
                        React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "th",
                                null,
                                "Attack"
                            ),
                            React.createElement(
                                "td",
                                null,
                                selectedPokemon["atk_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' } },
                                "(",
                                selectedPokemon["atk_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' } },
                                "(+",
                                selectedPokemon["atk_ev"],
                                ")"
                            )
                        ),
                        React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "th",
                                null,
                                "Defense"
                            ),
                            React.createElement(
                                "td",
                                null,
                                selectedPokemon["def_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' } },
                                "(",
                                selectedPokemon["def_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' } },
                                "(+",
                                selectedPokemon["def_ev"],
                                ")"
                            )
                        ),
                        React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "th",
                                null,
                                "Sp. Attack"
                            ),
                            React.createElement(
                                "td",
                                null,
                                selectedPokemon["spa_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' } },
                                "(",
                                selectedPokemon["spa_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' } },
                                "(+",
                                selectedPokemon["spa_ev"],
                                ")"
                            )
                        ),
                        React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "th",
                                null,
                                "Sp. Defense"
                            ),
                            React.createElement(
                                "td",
                                null,
                                selectedPokemon["spd_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' } },
                                "(",
                                selectedPokemon["spd_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' } },
                                "(+",
                                selectedPokemon["spd_ev"],
                                ")"
                            )
                        ),
                        React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "th",
                                null,
                                "Speed"
                            ),
                            React.createElement(
                                "td",
                                null,
                                selectedPokemon["spe_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' } },
                                "(",
                                selectedPokemon["spe_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' } },
                                "(+",
                                selectedPokemon["spe_ev"],
                                ")"
                            )
                        )
                    )
                )
            )
        );
    }
}

function BoxControls(_ref3) {
    var rowCount = _ref3.rowCount,
        setRows = _ref3.setRows,
        sortField = _ref3.sortField,
        setSortField = _ref3.setSortField,
        sortOrder = _ref3.sortOrder,
        setSortOrder = _ref3.setSortOrder,
        filterTag = _ref3.filterTag,
        setFilterTag = _ref3.setFilterTag,
        searchWord = _ref3.searchWord,
        setSearchWord = _ref3.setSearchWord;

    // Filter by tag then by search word
    return React.createElement(
        "div",
        { className: "control-box" },
        React.createElement(
            "h5",
            null,
            "BOX SORTING"
        ),
        React.createElement(
            "table",
            null,
            React.createElement(
                "tbody",
                null,
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        null,
                        "Search:"
                    ),
                    React.createElement(
                        "td",
                        null,
                        React.createElement("input", {
                            value: searchWord,
                            style: { width: "100%" },
                            onChange: function onChange(e) {
                                return setSearchWord(e.target.value);
                            }
                        })
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        null,
                        "Sort by:"
                    ),
                    React.createElement(
                        "td",
                        null,
                        React.createElement(
                            "select",
                            { value: sortField, style: { width: "100%" }, onChange: function onChange(e) {
                                    return setSortField(e.target.value);
                                } },
                            React.createElement(
                                "option",
                                { value: "caught_date" },
                                "Caught date"
                            ),
                            React.createElement(
                                "option",
                                { value: "dex_number" },
                                "Dex number"
                            ),
                            React.createElement(
                                "option",
                                { value: "level" },
                                "Level"
                            ),
                            React.createElement(
                                "option",
                                { value: "bst" },
                                "Base stat total"
                            ),
                            React.createElement(
                                "option",
                                { value: "iv_total" },
                                "IV total"
                            )
                        )
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        null,
                        "Order:"
                    ),
                    React.createElement(
                        "td",
                        null,
                        React.createElement(
                            "select",
                            { value: sortOrder, style: { width: "100%" }, onChange: function onChange(e) {
                                    return setSortOrder(e.target.value);
                                } },
                            React.createElement(
                                "option",
                                { value: "asc" },
                                "Ascending"
                            ),
                            React.createElement(
                                "option",
                                { value: "desc" },
                                "Descending"
                            )
                        )
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        null,
                        "Filter:"
                    ),
                    React.createElement(
                        "td",
                        null,
                        React.createElement(
                            "select",
                            { value: filterTag, style: { width: "100%" }, onChange: function onChange(e) {
                                    return setFilterTag(e.target.value);
                                } },
                            React.createElement(
                                "option",
                                { value: "" },
                                "None"
                            ),
                            React.createElement(
                                "option",
                                { value: "circle" },
                                "Circle"
                            ),
                            React.createElement(
                                "option",
                                { value: "star" },
                                "Star"
                            ),
                            React.createElement(
                                "option",
                                { value: "square" },
                                "Square"
                            ),
                            React.createElement(
                                "option",
                                { value: "diamond" },
                                "Diamond"
                            ),
                            React.createElement(
                                "option",
                                { value: "shiny" },
                                "Shiny"
                            )
                        )
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        null,
                        "Per page:"
                    ),
                    React.createElement(
                        "td",
                        null,
                        React.createElement(
                            "select",
                            { value: rowCount * 5, style: { width: "100%" }, onChange: function onChange(e) {
                                    return setRows(e.target.value / 5);
                                } },
                            React.createElement(
                                "option",
                                { value: "25" },
                                "25"
                            ),
                            React.createElement(
                                "option",
                                { value: "30" },
                                "30"
                            ),
                            React.createElement(
                                "option",
                                { value: "35" },
                                "35"
                            ),
                            React.createElement(
                                "option",
                                { value: "40" },
                                "40"
                            ),
                            React.createElement(
                                "option",
                                { value: "50" },
                                "50"
                            )
                        )
                    )
                )
            )
        ),
        React.createElement("br", null),
        React.createElement(
            "h5",
            null,
            "ADVANCED"
        )
    );
}

function BoxTabs(_ref4) {
    var pokemonPages = _ref4.pokemonPages,
        selectedPokemon = _ref4.selectedPokemon,
        setSelectedPokemon = _ref4.setSelectedPokemon,
        setClicked = _ref4.setClicked,
        setCoords = _ref4.setCoords;

    // Logic for handling tab opening and closing
    var _React$useState15 = React.useState(0),
        _React$useState16 = _slicedToArray(_React$useState15, 2),
        currentTab = _React$useState16[0],
        newTab = _React$useState16[1];

    var pokemonTabs = pokemonPages.map(function (page, index) {
        return React.createElement(
            "div",
            { key: "page" + index, style: index == currentTab ? {} : { display: 'none' } },
            React.createElement(BoxPage, { page: page, idx: index, selectedPokemon: selectedPokemon,
                setSelectedPokemon: setSelectedPokemon, setClicked: setClicked, setCoords: setCoords })
        );
    });
    var tabOpeners = pokemonPages.map(function (page, index) {
        return React.createElement(
            "button",
            { className: "page-select", key: "btn" + index, onClick: function onClick() {
                    return newTab(index);
                } },
            index + 1
        );
    });
    return React.createElement(
        "div",
        { className: "tabs", style: { textAlign: 'center' } },
        React.createElement(
            "h5",
            null,
            "Pages"
        ),
        tabOpeners,
        pokemonTabs
    );
}

function BoxPage(_ref5) {
    var page = _ref5.page,
        idx = _ref5.idx,
        selectedPokemon = _ref5.selectedPokemon,
        setSelectedPokemon = _ref5.setSelectedPokemon,
        setClicked = _ref5.setClicked,
        setCoords = _ref5.setCoords;

    var pokemonRows = listToMatrix(page, 5).map(function (row, index) {
        return React.createElement(BoxRow, { row: row, key: "row" + index, selectedPokemon: selectedPokemon,
            setSelectedPokemon: setSelectedPokemon, setClicked: setClicked, setCoords: setCoords });
    });

    return React.createElement(
        "table",
        { className: "center" },
        React.createElement(
            "tbody",
            null,
            pokemonRows
        )
    );
}

function BoxRow(_ref6) {
    var row = _ref6.row,
        selectedPokemon = _ref6.selectedPokemon,
        setSelectedPokemon = _ref6.setSelectedPokemon,
        setClicked = _ref6.setClicked,
        setCoords = _ref6.setCoords;

    var pokemonCells = row.map(function (cell, index) {
        return React.createElement(BoxCell, { cell: cell, key: "cell" + index, selectedPokemon: selectedPokemon, setSelectedPokemon: setSelectedPokemon,
            setClicked: setClicked, setCoords: setCoords });
    });
    return React.createElement(
        "tr",
        null,
        pokemonCells
    );
}

function BoxCell(_ref7) {
    var cell = _ref7.cell,
        selectedPokemon = _ref7.selectedPokemon,
        setSelectedPokemon = _ref7.setSelectedPokemon,
        setClicked = _ref7.setClicked,
        setCoords = _ref7.setCoords;

    if (cell) {
        // Get the image
        var fileName = cell["dex_number"];
        if (cell["shiny"]) fileName = fileName + "-s";
        var filePath = imgPath + fileName + ".png";
        // Highlight if selected
        if (selectedPokemon["id"] == cell["id"]) {
            if (cell["shiny"]) {
                var styling = { backgroundColor: 'rgba(230, 208, 163, 0.8)' };
            } else {
                var styling = { backgroundColor: 'rgba(210, 219, 224, 0.8)' };
            }
        } else {
            var styling = {};
        }
        // Gender symbol
        var gender = "";
        if (cell["sex"] == "m") {
            gender = React.createElement(
                "span",
                { style: { color: 'blue' } },
                "\u2642"
            );
        } else if (cell["sex"] == "f") {
            gender = React.createElement(
                "span",
                { style: { color: 'magenta' } },
                "\u2640"
            );
        }
        var cellRender = React.createElement(
            "a",
            { href: detailedUrl + cell["id"] },
            React.createElement(
                "div",
                { className: "box-cell select-card".concat(cell["shiny"] ? " shiny" : "")
                    //onClick={() => setSelectedPokemon(cell)}
                    , onContextMenu: function onContextMenu(e) {
                        e.preventDefault();
                        setClicked(true);
                        setSelectedPokemon(cell);
                        setCoords({ x: e.pageX, y: e.pageY });
                    },
                    style: styling },
                React.createElement(
                    "h1",
                    null,
                    cell["name"]
                ),
                "Level ",
                cell["level"],
                " ",
                gender,
                React.createElement("img", { src: filePath })
            )
        );
    } else {
        var cellRender = React.createElement("div", { className: "box-cell select-card" });
    }
    return React.createElement(
        "td",
        null,
        cellRender
    );
}

function ContextMenu(_ref8) {
    var top = _ref8.top,
        left = _ref8.left,
        displayPokemon = _ref8.displayPokemon,
        selectedPokemon = _ref8.selectedPokemon;

    var positioner = { top: top + "px", left: left + "px" };
    return React.createElement(
        "div",
        { className: "menu-container", style: positioner },
        React.createElement(
            "div",
            { className: "menu-option", onClick: function onClick() {
                    return displayPokemon(selectedPokemon);
                } },
            "Details"
        ),
        React.createElement(
            "div",
            { className: "menu-option" },
            "Add to Party"
        ),
        React.createElement(
            "div",
            { className: "menu-option" },
            "Create Trade"
        ),
        React.createElement(
            "div",
            { className: "menu-option" },
            "Add Tag"
        ),
        React.createElement(
            "div",
            { className: "menu-option" },
            "Release"
        )
    );
}

function useContextMenu() {
    var _React$useState17 = React.useState(false),
        _React$useState18 = _slicedToArray(_React$useState17, 2),
        clicked = _React$useState18[0],
        setClicked = _React$useState18[1];

    var _React$useState19 = React.useState({
        x: 0,
        y: 0
    }),
        _React$useState20 = _slicedToArray(_React$useState19, 2),
        coords = _React$useState20[0],
        setCoords = _React$useState20[1];

    React.useEffect(function () {
        var handleClick = function handleClick() {
            setClicked(false);
        };
        document.addEventListener("click", handleClick);
        return function () {
            document.removeElementListener("click", handleClick);
        };
    }, []);

    return {
        clicked: clicked,
        setClicked: setClicked,
        coords: coords,
        setCoords: setCoords
    };
}

var domNode = document.getElementById('box');
var root = ReactDOM.createRoot(domNode);
root.render(React.createElement(Box, { pokemonList: boxData }));