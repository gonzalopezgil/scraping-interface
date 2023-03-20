ENABLE_LINKS_JS = """
        var links = document.getElementsByTagName("a");
    for (var i = 0; i < links.length; i++) {
        links[i].removeEventListener("click", disableLink);
    }
"""

DISABLE_LINKS_JS = """
    var links = document.getElementsByTagName("a");
    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener("click", disableLink);
    }

    function disableLink(event) {
        event.preventDefault();
    }
"""
