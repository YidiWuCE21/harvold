function openTab(tabGroup, tab) {
    var i;
    var tabs = document.getElementsByClassName(tabGroup);
    for (i = 0; i < tabs.length; i++) {
        tabs[i].style.display = "none";
    }
    document.getElementById(tab).style.display = "block";
}