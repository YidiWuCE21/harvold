var _jsxFileName = "src\\box.js";

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
    var pokemonPages = listToMatrix(tempList, rowCount * 6);
    while (pokemonPages[pokemonPages.length - 1].length < rowCount * 6) {
        pokemonPages[pokemonPages.length - 1].push(null);
    }return React.createElement(
        "div",
        { className: "container", __source: {
                fileName: _jsxFileName,
                lineNumber: 67
            },
            __self: this
        },
        clicked && React.createElement(ContextMenu, { top: coords.y, left: coords.x, displayPokemon: displayPokemon, selectedPokemon: selectedPokemon, __source: {
                fileName: _jsxFileName,
                lineNumber: 69
            },
            __self: this
        }),
        React.createElement(
            "div",
            { className: "row", __source: {
                    fileName: _jsxFileName,
                    lineNumber: 71
                },
                __self: this
            },
            React.createElement(
                "div",
                { className: "col-3", __source: {
                        fileName: _jsxFileName,
                        lineNumber: 72
                    },
                    __self: this
                },
                React.createElement(PokemonDisplay, { selectedPokemon: displayedPokemon, __source: {
                        fileName: _jsxFileName,
                        lineNumber: 73
                    },
                    __self: this
                })
            ),
            React.createElement(
                "div",
                { className: "col-6", __source: {
                        fileName: _jsxFileName,
                        lineNumber: 75
                    },
                    __self: this
                },
                React.createElement(BoxTabs, { pokemonPages: pokemonPages,
                    selectedPokemon: selectedPokemon, setSelectedPokemon: setSelectedPokemon,
                    setClicked: setClicked, setCoords: setCoords, __source: {
                        fileName: _jsxFileName,
                        lineNumber: 76
                    },
                    __self: this
                })
            ),
            React.createElement(
                "div",
                { className: "col-3", __source: {
                        fileName: _jsxFileName,
                        lineNumber: 80
                    },
                    __self: this
                },
                React.createElement(BoxControls, { rowCount: rowCount, setRows: setRows,
                    sortField: sortField, setSortField: setSortField,
                    sortOrder: sortOrder, setSortOrder: setSortOrder,
                    filterTag: filterTag, setFilterTag: setFilterTag,
                    searchWord: searchWord, setSearchWord: setSearchWord, __source: {
                        fileName: _jsxFileName,
                        lineNumber: 81
                    },
                    __self: this
                })
            )
        )
    );
}

function PokemonDisplay(_ref2) {
    var selectedPokemon = _ref2.selectedPokemon;

    if (selectedPokemon["id"] === null) {
        return React.createElement("div", {
            __source: {
                fileName: _jsxFileName,
                lineNumber: 94
            },
            __self: this
        });
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
                { style: { color: 'blue' }, __source: {
                        fileName: _jsxFileName,
                        lineNumber: 105
                    },
                    __self: this
                },
                "\u2642"
            );
        } else if (selectedPokemon["sex"] == "f") {
            gender = React.createElement(
                "span",
                { style: { color: 'magenta' }, __source: {
                        fileName: _jsxFileName,
                        lineNumber: 107
                    },
                    __self: this
                },
                "\u2640"
            );
        }
        return React.createElement(
            "div",
            { className: "content-box", style: styling, __source: {
                    fileName: _jsxFileName,
                    lineNumber: 110
                },
                __self: this
            },
            React.createElement(
                "h4",
                {
                    __source: {
                        fileName: _jsxFileName,
                        lineNumber: 111
                    },
                    __self: this
                },
                selectedPokemon["name"],
                selectedPokemon["shiny"] ? " (s)" : ""
            ),
            React.createElement("img", { src: filePath, className: "center portrait", __source: {
                    fileName: _jsxFileName,
                    lineNumber: 112
                },
                __self: this
            }),
            React.createElement(
                "div",
                { className: "center", __source: {
                        fileName: _jsxFileName,
                        lineNumber: 113
                    },
                    __self: this
                },
                React.createElement(
                    "p",
                    { style: textStyle, __source: {
                            fileName: _jsxFileName,
                            lineNumber: 114
                        },
                        __self: this
                    },
                    "Level ",
                    selectedPokemon["level"],
                    " ",
                    gender
                ),
                React.createElement(
                    "p",
                    { style: textStyle, __source: {
                            fileName: _jsxFileName,
                            lineNumber: 115
                        },
                        __self: this
                    },
                    selectedPokemon["nature"].charAt(0).toUpperCase() + selectedPokemon["nature"].slice(1)
                ),
                React.createElement(
                    "table",
                    { className: "center", __source: {
                            fileName: _jsxFileName,
                            lineNumber: 116
                        },
                        __self: this
                    },
                    React.createElement(
                        "tbody",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 117
                            },
                            __self: this
                        },
                        React.createElement(
                            "tr",
                            {
                                __source: {
                                    fileName: _jsxFileName,
                                    lineNumber: 118
                                },
                                __self: this
                            },
                            React.createElement(
                                "th",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 119
                                    },
                                    __self: this
                                },
                                "HP"
                            ),
                            React.createElement(
                                "td",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 120
                                    },
                                    __self: this
                                },
                                selectedPokemon["hp_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 121
                                    },
                                    __self: this
                                },
                                "(",
                                selectedPokemon["hp_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 122
                                    },
                                    __self: this
                                },
                                "(+",
                                selectedPokemon["hp_ev"],
                                ")"
                            )
                        ),
                        React.createElement(
                            "tr",
                            {
                                __source: {
                                    fileName: _jsxFileName,
                                    lineNumber: 124
                                },
                                __self: this
                            },
                            React.createElement(
                                "th",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 125
                                    },
                                    __self: this
                                },
                                "Attack"
                            ),
                            React.createElement(
                                "td",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 126
                                    },
                                    __self: this
                                },
                                selectedPokemon["atk_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 127
                                    },
                                    __self: this
                                },
                                "(",
                                selectedPokemon["atk_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 128
                                    },
                                    __self: this
                                },
                                "(+",
                                selectedPokemon["atk_ev"],
                                ")"
                            )
                        ),
                        React.createElement(
                            "tr",
                            {
                                __source: {
                                    fileName: _jsxFileName,
                                    lineNumber: 130
                                },
                                __self: this
                            },
                            React.createElement(
                                "th",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 131
                                    },
                                    __self: this
                                },
                                "Defense"
                            ),
                            React.createElement(
                                "td",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 132
                                    },
                                    __self: this
                                },
                                selectedPokemon["def_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 133
                                    },
                                    __self: this
                                },
                                "(",
                                selectedPokemon["def_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 134
                                    },
                                    __self: this
                                },
                                "(+",
                                selectedPokemon["def_ev"],
                                ")"
                            )
                        ),
                        React.createElement(
                            "tr",
                            {
                                __source: {
                                    fileName: _jsxFileName,
                                    lineNumber: 136
                                },
                                __self: this
                            },
                            React.createElement(
                                "th",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 137
                                    },
                                    __self: this
                                },
                                "Sp. Attack"
                            ),
                            React.createElement(
                                "td",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 138
                                    },
                                    __self: this
                                },
                                selectedPokemon["spa_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 139
                                    },
                                    __self: this
                                },
                                "(",
                                selectedPokemon["spa_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 140
                                    },
                                    __self: this
                                },
                                "(+",
                                selectedPokemon["spa_ev"],
                                ")"
                            )
                        ),
                        React.createElement(
                            "tr",
                            {
                                __source: {
                                    fileName: _jsxFileName,
                                    lineNumber: 142
                                },
                                __self: this
                            },
                            React.createElement(
                                "th",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 143
                                    },
                                    __self: this
                                },
                                "Sp. Defense"
                            ),
                            React.createElement(
                                "td",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 144
                                    },
                                    __self: this
                                },
                                selectedPokemon["spd_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 145
                                    },
                                    __self: this
                                },
                                "(",
                                selectedPokemon["spd_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 146
                                    },
                                    __self: this
                                },
                                "(+",
                                selectedPokemon["spd_ev"],
                                ")"
                            )
                        ),
                        React.createElement(
                            "tr",
                            {
                                __source: {
                                    fileName: _jsxFileName,
                                    lineNumber: 148
                                },
                                __self: this
                            },
                            React.createElement(
                                "th",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 149
                                    },
                                    __self: this
                                },
                                "Speed"
                            ),
                            React.createElement(
                                "td",
                                {
                                    __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 150
                                    },
                                    __self: this
                                },
                                selectedPokemon["spe_stat"]
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'orange' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 151
                                    },
                                    __self: this
                                },
                                "(",
                                selectedPokemon["spe_iv"],
                                ")"
                            ),
                            React.createElement(
                                "td",
                                { style: { color: 'green' }, __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 152
                                    },
                                    __self: this
                                },
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
        { className: "control-box", __source: {
                fileName: _jsxFileName,
                lineNumber: 165
            },
            __self: this
        },
        React.createElement(
            "h5",
            {
                __source: {
                    fileName: _jsxFileName,
                    lineNumber: 166
                },
                __self: this
            },
            "BOX SORTING"
        ),
        React.createElement(
            "table",
            {
                __source: {
                    fileName: _jsxFileName,
                    lineNumber: 167
                },
                __self: this
            },
            React.createElement(
                "tbody",
                {
                    __source: {
                        fileName: _jsxFileName,
                        lineNumber: 168
                    },
                    __self: this
                },
                React.createElement(
                    "tr",
                    {
                        __source: {
                            fileName: _jsxFileName,
                            lineNumber: 169
                        },
                        __self: this
                    },
                    React.createElement(
                        "th",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 170
                            },
                            __self: this
                        },
                        "Search:"
                    ),
                    React.createElement(
                        "td",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 171
                            },
                            __self: this
                        },
                        React.createElement("input", {
                            value: searchWord,
                            style: { width: "100%" },
                            onChange: function onChange(e) {
                                return setSearchWord(e.target.value);
                            },
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 172
                            },
                            __self: this
                        })
                    )
                ),
                React.createElement(
                    "tr",
                    {
                        __source: {
                            fileName: _jsxFileName,
                            lineNumber: 179
                        },
                        __self: this
                    },
                    React.createElement(
                        "th",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 180
                            },
                            __self: this
                        },
                        "Sort by:"
                    ),
                    React.createElement(
                        "td",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 181
                            },
                            __self: this
                        },
                        React.createElement(
                            "select",
                            { value: sortField, style: { width: "100%" }, onChange: function onChange(e) {
                                    return setSortField(e.target.value);
                                }, __source: {
                                    fileName: _jsxFileName,
                                    lineNumber: 182
                                },
                                __self: this
                            },
                            React.createElement(
                                "option",
                                { value: "caught_date", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 183
                                    },
                                    __self: this
                                },
                                "Caught date"
                            ),
                            React.createElement(
                                "option",
                                { value: "dex_number", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 184
                                    },
                                    __self: this
                                },
                                "Dex number"
                            ),
                            React.createElement(
                                "option",
                                { value: "level", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 185
                                    },
                                    __self: this
                                },
                                "Level"
                            ),
                            React.createElement(
                                "option",
                                { value: "bst", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 186
                                    },
                                    __self: this
                                },
                                "Base stat total"
                            ),
                            React.createElement(
                                "option",
                                { value: "iv_total", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 187
                                    },
                                    __self: this
                                },
                                "IV total"
                            )
                        )
                    )
                ),
                React.createElement(
                    "tr",
                    {
                        __source: {
                            fileName: _jsxFileName,
                            lineNumber: 191
                        },
                        __self: this
                    },
                    React.createElement(
                        "th",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 192
                            },
                            __self: this
                        },
                        "Order:"
                    ),
                    React.createElement(
                        "td",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 193
                            },
                            __self: this
                        },
                        React.createElement(
                            "select",
                            { value: sortOrder, style: { width: "100%" }, onChange: function onChange(e) {
                                    return setSortOrder(e.target.value);
                                }, __source: {
                                    fileName: _jsxFileName,
                                    lineNumber: 194
                                },
                                __self: this
                            },
                            React.createElement(
                                "option",
                                { value: "asc", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 195
                                    },
                                    __self: this
                                },
                                "Ascending"
                            ),
                            React.createElement(
                                "option",
                                { value: "desc", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 196
                                    },
                                    __self: this
                                },
                                "Descending"
                            )
                        )
                    )
                ),
                React.createElement(
                    "tr",
                    {
                        __source: {
                            fileName: _jsxFileName,
                            lineNumber: 200
                        },
                        __self: this
                    },
                    React.createElement(
                        "th",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 201
                            },
                            __self: this
                        },
                        "Filter:"
                    ),
                    React.createElement(
                        "td",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 202
                            },
                            __self: this
                        },
                        React.createElement(
                            "select",
                            { value: filterTag, style: { width: "100%" }, onChange: function onChange(e) {
                                    return setFilterTag(e.target.value);
                                }, __source: {
                                    fileName: _jsxFileName,
                                    lineNumber: 203
                                },
                                __self: this
                            },
                            React.createElement(
                                "option",
                                { value: "", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 204
                                    },
                                    __self: this
                                },
                                "None"
                            ),
                            React.createElement(
                                "option",
                                { value: "circle", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 205
                                    },
                                    __self: this
                                },
                                "Circle"
                            ),
                            React.createElement(
                                "option",
                                { value: "star", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 206
                                    },
                                    __self: this
                                },
                                "Star"
                            ),
                            React.createElement(
                                "option",
                                { value: "square", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 207
                                    },
                                    __self: this
                                },
                                "Square"
                            ),
                            React.createElement(
                                "option",
                                { value: "diamond", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 208
                                    },
                                    __self: this
                                },
                                "Diamond"
                            ),
                            React.createElement(
                                "option",
                                { value: "shiny", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 209
                                    },
                                    __self: this
                                },
                                "Shiny"
                            )
                        )
                    )
                ),
                React.createElement(
                    "tr",
                    {
                        __source: {
                            fileName: _jsxFileName,
                            lineNumber: 213
                        },
                        __self: this
                    },
                    React.createElement(
                        "th",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 214
                            },
                            __self: this
                        },
                        "Per page:"
                    ),
                    React.createElement(
                        "td",
                        {
                            __source: {
                                fileName: _jsxFileName,
                                lineNumber: 215
                            },
                            __self: this
                        },
                        React.createElement(
                            "select",
                            { value: rowCount * 6, style: { width: "100%" }, onChange: function onChange(e) {
                                    return setRows(e.target.value / 6);
                                }, __source: {
                                    fileName: _jsxFileName,
                                    lineNumber: 216
                                },
                                __self: this
                            },
                            React.createElement(
                                "option",
                                { value: "24", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 217
                                    },
                                    __self: this
                                },
                                "24"
                            ),
                            React.createElement(
                                "option",
                                { value: "30", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 218
                                    },
                                    __self: this
                                },
                                "30"
                            ),
                            React.createElement(
                                "option",
                                { value: "36", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 219
                                    },
                                    __self: this
                                },
                                "36"
                            ),
                            React.createElement(
                                "option",
                                { value: "48", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 220
                                    },
                                    __self: this
                                },
                                "48"
                            ),
                            React.createElement(
                                "option",
                                { value: "60", __source: {
                                        fileName: _jsxFileName,
                                        lineNumber: 221
                                    },
                                    __self: this
                                },
                                "60"
                            )
                        )
                    )
                )
            )
        ),
        React.createElement("br", {
            __source: {
                fileName: _jsxFileName,
                lineNumber: 227
            },
            __self: this
        }),
        React.createElement(
            "h5",
            {
                __source: {
                    fileName: _jsxFileName,
                    lineNumber: 228
                },
                __self: this
            },
            "ADVANCED"
        )
    );
}

function BoxTabs(_ref4) {
    var _this = this;

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
            { key: "page" + index, style: index == currentTab ? {} : { display: 'none' }, __source: {
                    fileName: _jsxFileName,
                    lineNumber: 243
                },
                __self: _this
            },
            React.createElement(BoxPage, { page: page, idx: index, selectedPokemon: selectedPokemon,
                setSelectedPokemon: setSelectedPokemon, setClicked: setClicked, setCoords: setCoords, __source: {
                    fileName: _jsxFileName,
                    lineNumber: 244
                },
                __self: _this
            })
        );
    });
    var tabOpeners = pokemonPages.map(function (page, index) {
        return React.createElement(
            "button",
            { className: "page-select", key: "btn" + index, onClick: function onClick() {
                    return newTab(index);
                }, __source: {
                    fileName: _jsxFileName,
                    lineNumber: 250
                },
                __self: _this
            },
            index + 1
        );
    });
    return React.createElement(
        "div",
        { className: "tabs", style: { textAlign: 'center' }, __source: {
                fileName: _jsxFileName,
                lineNumber: 253
            },
            __self: this
        },
        React.createElement(
            "h5",
            {
                __source: {
                    fileName: _jsxFileName,
                    lineNumber: 254
                },
                __self: this
            },
            "Pages"
        ),
        tabOpeners,
        pokemonTabs
    );
}

function BoxPage(_ref5) {
    var _this2 = this;

    var page = _ref5.page,
        idx = _ref5.idx,
        selectedPokemon = _ref5.selectedPokemon,
        setSelectedPokemon = _ref5.setSelectedPokemon,
        setClicked = _ref5.setClicked,
        setCoords = _ref5.setCoords;

    var pokemonRows = listToMatrix(page, 6).map(function (row, index) {
        return React.createElement(BoxRow, { row: row, key: "row" + index, selectedPokemon: selectedPokemon,
            setSelectedPokemon: setSelectedPokemon, setClicked: setClicked, setCoords: setCoords, __source: {
                fileName: _jsxFileName,
                lineNumber: 263
            },
            __self: _this2
        });
    });

    return React.createElement(
        "table",
        { className: "right", __source: {
                fileName: _jsxFileName,
                lineNumber: 269
            },
            __self: this
        },
        React.createElement(
            "tbody",
            {
                __source: {
                    fileName: _jsxFileName,
                    lineNumber: 270
                },
                __self: this
            },
            pokemonRows
        )
    );
}

function BoxRow(_ref6) {
    var _this3 = this;

    var row = _ref6.row,
        selectedPokemon = _ref6.selectedPokemon,
        setSelectedPokemon = _ref6.setSelectedPokemon,
        setClicked = _ref6.setClicked,
        setCoords = _ref6.setCoords;

    var pokemonCells = row.map(function (cell, index) {
        return React.createElement(BoxCell, { cell: cell, key: "cell" + index, selectedPokemon: selectedPokemon, setSelectedPokemon: setSelectedPokemon,
            setClicked: setClicked, setCoords: setCoords, __source: {
                fileName: _jsxFileName,
                lineNumber: 280
            },
            __self: _this3
        });
    });
    return React.createElement(
        "tr",
        {
            __source: {
                fileName: _jsxFileName,
                lineNumber: 284
            },
            __self: this
        },
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
                { style: { color: 'blue' }, __source: {
                        fileName: _jsxFileName,
                        lineNumber: 310
                    },
                    __self: this
                },
                "\u2642"
            );
        } else if (cell["sex"] == "f") {
            gender = React.createElement(
                "span",
                { style: { color: 'magenta' }, __source: {
                        fileName: _jsxFileName,
                        lineNumber: 312
                    },
                    __self: this
                },
                "\u2640"
            );
        }
        var cellRender = React.createElement(
            "a",
            { href: "https://stackoverflow.com/questions/796087/make-a-div-into-a-link", __source: {
                    fileName: _jsxFileName,
                    lineNumber: 315
                },
                __self: this
            },
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
                    style: styling, __source: {
                        fileName: _jsxFileName,
                        lineNumber: 316
                    },
                    __self: this
                },
                React.createElement(
                    "h1",
                    {
                        __source: {
                            fileName: _jsxFileName,
                            lineNumber: 326
                        },
                        __self: this
                    },
                    cell["name"]
                ),
                "Level ",
                cell["level"],
                " ",
                gender,
                React.createElement("img", { src: filePath, __source: {
                        fileName: _jsxFileName,
                        lineNumber: 328
                    },
                    __self: this
                })
            )
        );
    } else {
        var cellRender = React.createElement("div", { className: "box-cell select-card", __source: {
                fileName: _jsxFileName,
                lineNumber: 333
            },
            __self: this
        });
    }
    return React.createElement(
        "td",
        {
            __source: {
                fileName: _jsxFileName,
                lineNumber: 336
            },
            __self: this
        },
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
        { className: "menu-container", style: positioner, __source: {
                fileName: _jsxFileName,
                lineNumber: 345
            },
            __self: this
        },
        React.createElement(
            "div",
            { className: "menu-option", onClick: function onClick() {
                    return displayPokemon(selectedPokemon);
                }, __source: {
                    fileName: _jsxFileName,
                    lineNumber: 346
                },
                __self: this
            },
            "Details"
        ),
        React.createElement(
            "div",
            { className: "menu-option", __source: {
                    fileName: _jsxFileName,
                    lineNumber: 347
                },
                __self: this
            },
            "Add to Party"
        ),
        React.createElement(
            "div",
            { className: "menu-option", __source: {
                    fileName: _jsxFileName,
                    lineNumber: 348
                },
                __self: this
            },
            "Create Trade"
        ),
        React.createElement(
            "div",
            { className: "menu-option", __source: {
                    fileName: _jsxFileName,
                    lineNumber: 349
                },
                __self: this
            },
            "Add Tag"
        ),
        React.createElement(
            "div",
            { className: "menu-option", __source: {
                    fileName: _jsxFileName,
                    lineNumber: 350
                },
                __self: this
            },
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
root.render(React.createElement(Box, { pokemonList: boxData, __source: {
        fileName: _jsxFileName,
        lineNumber: 380
    },
    __self: this
}));